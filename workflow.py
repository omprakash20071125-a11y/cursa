from langgraph.graph import StateGraph, START, END
from langchain_groq import ChatGroq
from typing import TypedDict, Annotated, Literal
from pydantic import BaseModel, Field
from tavily import TavilyClient
import os
import operator
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import interrupt, Command
from dotenv import load_dotenv

load_dotenv()

checkpoint = MemorySaver()

class resource_format(BaseModel):
    title: str
    url: str
    source: str
    type: str
    why_this_resource: str

class output_resource(BaseModel):
    resource: list[resource_format]

class sub_topic_schema(BaseModel):
    id: int
    subtopic_name: str
    breif: str

class sub_topics(BaseModel):
    main_topic: str
    sub_topic: list[sub_topic_schema]

class MCQ(BaseModel):
    a: str
    b: str
    c: str
    d: str

class Question(BaseModel):
    question: str
    option: MCQ
    correct_answer: Literal["a", "b", "c", "d"]
    explanation: str

class quizschema(BaseModel):
    topic: str
    question: list[Question]

class State(TypedDict):
    topic: str
    quiz: quizschema
    sub_topic: sub_topics
    current_topic_counter: int
    resource_of_current_subtopic: output_resource
    user_answers: list
    score_current_quiz: int
    score_per_subtopic: Annotated[list[dict], operator.add]
    end_session: bool

model = ChatGroq(model=os.getenv("GROQ_MODEL_NAME", "llama-3.3-70b-versatile"))

def generate_subtopics(state: State) -> State:
    structured_model_subtopics = model.with_structured_output(sub_topics)

    result = structured_model_subtopics.invoke(f"""
    You are a curriculum designer for an online learning platform.

    Main topic: {state['topic']}

    Generate exactly 5 sub-topics that a student
    must learn to fully understand {state['topic']}.

    Rules:
    - Order them from foundational to advanced
    - Each sub-topic must be specific, not vague
      GOOD: "dot product and its geometric interpretation"
      BAD:  "linear algebra basics"
    - Each sub-topic should be learnable in one focused session
    - No overlap between sub-topics
    """)

    return {'sub_topic': result, 'current_topic_counter': state['current_topic_counter']}


def fetching_resources(state: State) -> State:
    current_topic_counter = state['current_topic_counter']

    client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
    result = client.search(
        query=f"best resources to learn {state['sub_topic'].sub_topic[current_topic_counter].subtopic_name} tutorial youtube github",
        search_depth="advanced",
        max_results=5
    )

    resources = []
    for item in result.get('results', [])[:3]:
        url = item.get('url', '')
        if 'youtube.com' in url or 'youtu.be' in url:
            source = "YouTube"
            rtype = "video"
        elif 'github.com' in url:
            source = "GitHub"
            rtype = "hands-on"
        else:
            source = "Article"
            rtype = "reading"

        resources.append(resource_format(
            title=item.get('title', 'Resource'),
            url=url,
            source=source,
            type=rtype,
            why_this_resource=item.get('content', 'Helpful resource')[:200]
        ))

    while len(resources) < 3:
        subtopic_name = state['sub_topic'].sub_topic[current_topic_counter].subtopic_name
        resources.append(resource_format(
            title=f"Search: {subtopic_name}",
            url="https://www.google.com/search?q=" + subtopic_name.replace(' ', '+'),
            source="Web Search",
            type="reading",
            why_this_resource="Search for more resources on this topic"
        ))

    validated = output_resource(resource=resources[:3])
    return {'resource_of_current_subtopic': validated}


def generate_quiz(state: State) -> State:
    current_topic_counter = state['current_topic_counter']
    structured_model_quiz = model.with_structured_output(quizschema)

    max_retries = 3
    last_error = None

    for attempt in range(max_retries):
        try:
            quiz = structured_model_quiz.invoke(f"""
                Generate exactly 5 MCQ questions on: {state['sub_topic'].sub_topic[current_topic_counter].subtopic_name}

                STRICT RULES:
                1. Each question must have exactly 4 options (a, b, c, d)
                2. Each question must have one correct answer (a, b, c, or d)
                3. Each question must have a brief explanation
                4. Questions must be unique and non-repetitive
                5. Output must be valid JSON matching the schema

                Topic: {state['sub_topic'].sub_topic[current_topic_counter].subtopic_name}
            """)

            if quiz and quiz.question and len(quiz.question) == 5:
                for q in quiz.question:
                    if not all([q.option.a, q.option.b, q.option.c, q.option.d]):
                        raise ValueError("Empty options found")
                    if q.correct_answer not in ['a', 'b', 'c', 'd']:
                        raise ValueError(f"Invalid correct_answer: {q.correct_answer}")
                return {'quiz': quiz}

        except Exception as e:
            last_error = e
            print(f"Quiz generation attempt {attempt + 1} failed: {e}")

    raise RuntimeError(f"Quiz generation failed after {max_retries} attempts: {last_error}")


def answer_collector(state: State) -> State:
    """
    Pause graph execution here and wait for the frontend to send answers
    via Command(resume=answers). This is the ONLY place execution pauses.
    """
    answers = interrupt("Waiting for user answers")
    return {"user_answers": answers}


def score_calculator(state: State) -> State:
    score = 0
    user_answers = state.get('user_answers', [])
    correct_answers = [q.correct_answer.lower().strip() for q in state['quiz'].question]

    for i in range(min(len(correct_answers), len(user_answers))):
        if user_answers[i].lower().strip() == correct_answers[i]:
            score += 1

    return {
        'score_current_quiz': score,
        'score_per_subtopic': [{
            'subtopic': state['sub_topic'].sub_topic[state['current_topic_counter']].subtopic_name,
            'score': score
        }]
    }


def increment_counter(state: State) -> State:
    return {'current_topic_counter': state['current_topic_counter'] + 1}


# ── Routing ───────────────────────────────────────────────────────────────────

def check_node(state: State) -> str:
    total_questions = len(state['quiz'].question)
    percentage = (state['score_current_quiz'] / total_questions) * 100 if total_questions > 0 else 0
    passed = percentage >= 75
    all_done = state['current_topic_counter'] >= len(state['sub_topic'].sub_topic) - 1

    if passed and all_done:
        return 'end'
    elif passed and not all_done:
        return 'increment_counter'
    else:
        return 'generate_quiz'  # Retry same subtopic with a new quiz

graph = StateGraph(State)

graph.add_node("generate_subtopics", generate_subtopics)
graph.add_node("fetching_resource", fetching_resources)
graph.add_node("generate_quiz", generate_quiz)
graph.add_node("answer_collector", answer_collector)
graph.add_node("score_calculator", score_calculator)
graph.add_node("increment_counter", increment_counter)

graph.add_edge(START, "generate_subtopics")
graph.add_edge("generate_subtopics", "fetching_resource")
graph.add_edge("fetching_resource", "generate_quiz")
graph.add_edge("generate_quiz", "answer_collector")
graph.add_edge("answer_collector", "score_calculator")

graph.add_conditional_edges(
    "score_calculator",
    check_node,
    {
        'increment_counter': 'increment_counter',
        'end': END,
        'generate_quiz': 'generate_quiz',
    }
)

graph.add_edge("increment_counter", "fetching_resource")

ai_tutor = graph.compile(checkpointer=checkpoint)