import streamlit as st
import uuid
from workflow import ai_tutor
from langgraph.types import Command

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Tutor",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&display=swap');

:root {
    --bg:      #0D0F14;
    --surface: #14171F;
    --card:    #1B1F2B;
    --border:  #252A38;
    --accent:  #6C63FF;
    --accent2: #A78BFA;
    --green:   #34D399;
    --red:     #F87171;
    --yellow:  #FBBF24;
    --text:    #E8EAF0;
    --muted:   #7B80A0;
    --radius:  12px;
}
html, body, .stApp { background-color: var(--bg) !important; font-family: 'Inter', sans-serif; color: var(--text); }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2rem 3rem !important; max-width: 900px !important; margin: 0 auto; }
h1, h2, h3 { font-family: 'Space Grotesk', sans-serif; }

.hero { text-align: center; padding: 3.5rem 2rem 2.5rem; }
.hero-badge {
    display: inline-block;
    background: linear-gradient(135deg, #6C63FF22, #A78BFA22);
    border: 1px solid #6C63FF55; color: var(--accent2);
    font-size: 0.75rem; font-weight: 600; letter-spacing: 0.12em;
    text-transform: uppercase; padding: 0.35rem 1rem;
    border-radius: 100px; margin-bottom: 1.25rem;
}
.hero-title {
    font-size: 2.8rem; font-weight: 700; line-height: 1.15;
    background: linear-gradient(135deg, #E8EAF0 30%, #A78BFA 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    margin-bottom: 0.75rem;
}
.hero-sub { color: var(--muted); font-size: 1rem; max-width: 480px; margin: 0 auto 2rem; line-height: 1.6; }

.input-card { background: var(--card); border: 1px solid var(--border); border-radius: var(--radius); padding: 2rem; margin-bottom: 1.5rem; }

.stTextInput > label { display: none !important; }
.stTextInput input {
    background: var(--surface) !important; border: 1px solid var(--border) !important;
    border-radius: 8px !important; color: var(--text) !important;
    font-size: 1rem !important; padding: 0.8rem 1rem !important;
}
.stTextInput input:focus { border-color: var(--accent) !important; box-shadow: 0 0 0 3px #6C63FF22 !important; }
.stTextInput input::placeholder { color: var(--muted) !important; }

.stButton > button {
    background: linear-gradient(135deg, #6C63FF, #8B5CF6) !important;
    color: white !important; border: none !important; border-radius: 8px !important;
    font-family: 'Inter', sans-serif !important; font-weight: 600 !important;
    font-size: 0.9rem !important; padding: 0.65rem 1.5rem !important;
    cursor: pointer !important; transition: opacity 0.2s !important; width: 100%;
}
.stButton > button:hover { opacity: 0.88 !important; }

.progress-wrap { margin: 1.5rem 0; }
.progress-label { display: flex; justify-content: space-between; font-size: 0.8rem; color: var(--muted); margin-bottom: 0.5rem; }
.progress-track { background: var(--card); border-radius: 100px; height: 8px; overflow: hidden; border: 1px solid var(--border); }
.progress-fill { height: 100%; border-radius: 100px; background: linear-gradient(90deg, #6C63FF, #A78BFA); transition: width 0.5s ease; }

.subtopic-grid { display: flex; flex-wrap: wrap; gap: 0.6rem; margin: 1rem 0 1.5rem; }
.subtopic-pill { background: var(--card); border: 1px solid var(--border); border-radius: 100px; padding: 0.4rem 1rem; font-size: 0.82rem; color: var(--muted); white-space: nowrap; }
.subtopic-pill.active { background: #6C63FF22; border-color: var(--accent); color: var(--accent2); font-weight: 600; }
.subtopic-pill.done { background: #34D39922; border-color: var(--green); color: var(--green); }

.section-header { display: flex; align-items: center; gap: 0.75rem; margin-bottom: 1rem; }
.section-icon { width: 36px; height: 36px; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 1rem; flex-shrink: 0; }
.icon-purple { background: #6C63FF22; }
.icon-blue   { background: #3B82F622; }
.icon-green  { background: #34D39922; }
.section-title { font-family: 'Space Grotesk', sans-serif; font-size: 1.1rem; font-weight: 600; color: var(--text); margin: 0; }
.section-sub { font-size: 0.8rem; color: var(--muted); }

.resource-card { background: var(--card); border: 1px solid var(--border); border-radius: var(--radius); padding: 1rem 1.25rem; margin-bottom: 0.75rem; display: flex; align-items: flex-start; gap: 0.85rem; }
.resource-card:hover { border-color: var(--accent); }
.resource-badge { display:inline-block; flex-shrink: 0; font-size: 0.7rem; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase; padding: 0.25rem 0.6rem; border-radius: 6px; white-space: nowrap; }
.badge-video   { background: #EF444422; color: #F87171; }
.badge-handson { background: #6C63FF22; color: #A78BFA; }
.badge-reading { background: #3B82F622; color: #93C5FD; }
.badge-web     { background: #FBBF2422; color: #FCD34D; }
.resource-title { font-weight: 500; font-size: 0.9rem; color: var(--text); margin-bottom: 0.3rem; line-height: 1.4; word-break: break-word; }
.resource-why { font-size: 0.78rem; color: var(--muted); line-height: 1.55; word-break: break-word; }

.quiz-card { background: var(--card); border: 1px solid var(--border); border-radius: var(--radius); padding: 1.5rem; margin-bottom: 0.75rem; }
.q-number { font-size: 0.72rem; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; color: var(--accent2); margin-bottom: 0.5rem; }
.q-text { font-size: 1rem; font-weight: 500; color: var(--text); line-height: 1.55; }

div[data-testid="stRadio"] > label { display: none !important; }
div[data-testid="stRadio"] div[role="radiogroup"] { gap: 0.5rem !important; display: flex !important; flex-direction: column !important; }
div[data-testid="stRadio"] label { background: var(--surface) !important; border: 1px solid var(--border) !important; border-radius: 8px !important; padding: 0.65rem 1rem !important; cursor: pointer !important; font-size: 0.88rem !important; color: var(--text) !important; }
div[data-testid="stRadio"] label:hover { border-color: var(--accent) !important; }

.score-card { background: var(--card); border: 1px solid var(--border); border-radius: var(--radius); padding: 1.5rem; text-align: center; margin-bottom: 1.5rem; }
.score-big { font-family: 'Space Grotesk', sans-serif; font-size: 3.5rem; font-weight: 700; line-height: 1; margin-bottom: 0.25rem; }
.score-label { font-size: 0.85rem; color: var(--muted); }
.score-pass { color: var(--green); }
.score-fail { color: var(--red); }

.answer-row { display: flex; align-items: flex-start; gap: 0.75rem; padding: 0.65rem 1rem; border-radius: 8px; margin-bottom: 0.5rem; font-size: 0.88rem; }
.answer-correct { background: #34D39922; border: 1px solid #34D39966; color: var(--green); }
.answer-wrong   { background: #F8717122; border: 1px solid #F8717166; color: var(--red); }
.answer-icon { font-size: 1rem; flex-shrink: 0; margin-top: 1px; }
.answer-text { flex: 1; }
.answer-expl { font-size: 0.78rem; color: var(--muted); margin-top: 0.3rem; }

.final-card { background: linear-gradient(135deg, #1B1F2B 0%, #16192400 100%); border: 1px solid var(--accent); border-radius: 16px; padding: 2.5rem; text-align: center; margin-bottom: 2rem; }
.final-icon { font-size: 3rem; margin-bottom: 1rem; }
.final-title { font-family: 'Space Grotesk', sans-serif; font-size: 1.8rem; font-weight: 700; color: var(--text); margin-bottom: 0.5rem; }
.final-sub { color: var(--muted); font-size: 0.95rem; }

.score-row { display: flex; justify-content: space-between; align-items: center; padding: 0.75rem 1rem; background: var(--surface); border: 1px solid var(--border); border-radius: 8px; margin-bottom: 0.5rem; font-size: 0.88rem; }
.score-row-name { color: var(--text); font-weight: 500; }
.score-row-val  { font-weight: 700; }
.val-high { color: var(--green); }
.val-mid  { color: var(--yellow); }
.val-low  { color: var(--red); }

.divider { height: 1px; background: var(--border); margin: 1.5rem 0; }
.stSpinner > div { border-top-color: var(--accent) !important; }
</style>
""", unsafe_allow_html=True)


# ── Session state ──────────────────────────────────────────────────────────────
def init_state():
    defaults = {
        "phase": "start",
        "thread_id": str(uuid.uuid4()),
        "graph_state": None,
        "topic": "",
        "quiz_answers": [],
        "subtopics_done": [],
        # frontend-computed score (never read from graph)
        "fe_score": 0,
        "fe_passed": False,
        "questions_snap": [],
        "correct_answers_snap": [],
        # ── FIX: snapshot the subtopic index at submit time so the score
        #    phase uses the correct index even after the graph increments
        #    current_topic_counter.
        "submitted_topic_idx": 0,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()


# ── Helpers ────────────────────────────────────────────────────────────────────
def run_until_interrupt(inputs=None, command=None):
    config = {"configurable": {"thread_id": st.session_state.thread_id}}
    if command is not None:
        list(ai_tutor.stream(command, config, stream_mode="values"))
    else:
        list(ai_tutor.stream(inputs, config, stream_mode="values"))
    snapshot = ai_tutor.get_state(config)
    interrupt_val = (
        snapshot.tasks[0].interrupts[0].value
        if snapshot.tasks and snapshot.tasks[0].interrupts
        else None
    )
    return snapshot, interrupt_val


def compute_score(user_answers: list, correct_answers: list) -> tuple[int, int]:
    """
    Compare user_answers (list of 'a'/'b'/'c'/'d') against correct_answers
    (list of 'a'/'b'/'c'/'d') captured at submission time — never re-read
    from graph state so a retry quiz cannot corrupt the score.
    """
    total = len(correct_answers)
    if total == 0:
        return 0, 0
    score = sum(
        1
        for i, correct in enumerate(correct_answers)
        if i < len(user_answers) and user_answers[i].strip().lower() == correct.strip().lower()
    )
    return score, total


def badge_html(rtype: str) -> str:
    classes = {"video": "badge-video", "hands-on": "badge-handson",
                "reading": "badge-reading", "web search": "badge-web"}
    icons   = {"video": "▶", "hands-on": "💻", "reading": "📄", "web search": "🔍"}
    cls = classes.get(rtype.lower(), "badge-reading")
    ico = icons.get(rtype.lower(), "📄")
    return f'<span class="resource-badge {cls}">{ico} {rtype}</span>'


def score_color(score, total) -> str:
    pct = (score / total * 100) if total else 0
    if pct >= 80: return "val-high"
    if pct >= 60: return "val-mid"
    return "val-low"


# ── Shared header ──────────────────────────────────────────────────────────────
def render_header():
    gs = st.session_state.graph_state
    if not gs or "sub_topic" not in gs:
        return
    subtopics = gs["sub_topic"].sub_topic
    current   = gs.get("current_topic_counter", 0)
    total     = len(subtopics)
    done_ids  = {d["idx"] for d in st.session_state.subtopics_done if isinstance(d, dict)}
    completed = len(done_ids)

    pills = ""
    for i, sub in enumerate(subtopics):
        if i in done_ids:
            # Already passed — always show green regardless of current counter
            pills += f'<span class="subtopic-pill done">✓ {sub.subtopic_name}</span>'
        elif i == current and i not in done_ids:
            pills += f'<span class="subtopic-pill active">{sub.subtopic_name}</span>'
        else:
            pills += f'<span class="subtopic-pill">{sub.subtopic_name}</span>'

    pct = int((completed / total) * 100)

    st.markdown(f"""
    <div style="font-size:0.75rem;color:#7B80A0;letter-spacing:0.08em;text-transform:uppercase;margin-bottom:0.25rem;">
        {st.session_state.topic}
    </div>
    <div class="progress-wrap">
      <div class="progress-label">
        <span>Progress</span><span>{completed}/{total} subtopics</span>
      </div>
      <div class="progress-track">
        <div class="progress-fill" style="width:{pct}%"></div>
      </div>
    </div>
    <div class="subtopic-grid">{pills}</div>
    """, unsafe_allow_html=True)


# ── Phase router ───────────────────────────────────────────────────────────────
phase = st.session_state.phase


# ── START ──────────────────────────────────────────────────────────────────────
if phase == "start":
    st.markdown("""
    <div class="hero">
      <div class="hero-badge">AI-Powered Learning</div>
      <div class="hero-title">Master anything,<br>one topic at a time</div>
      <div class="hero-sub">Enter a subject and your AI tutor builds a personalised learning path with curated resources and quizzes.</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="display:flex;gap:1rem;margin-bottom:1.5rem;flex-wrap:wrap;">
      <div style="flex:1;min-width:180px;background:#1B1F2B;border:1px solid #252A38;border-radius:12px;padding:1.1rem 1.25rem;display:flex;align-items:flex-start;gap:0.75rem;">
        <div style="font-size:1.4rem;line-height:1;">🗺️</div>
        <div>
          <div style="font-family:'Space Grotesk',sans-serif;font-size:0.9rem;font-weight:600;color:#E8EAF0;margin-bottom:0.25rem;">Personalised Path</div>
          <div style="font-size:0.78rem;color:#7B80A0;line-height:1.5;">Your topic is broken into bite-sized subtopics in a logical learning order.</div>
        </div>
      </div>
      <div style="flex:1;min-width:180px;background:#1B1F2B;border:1px solid #252A38;border-radius:12px;padding:1.1rem 1.25rem;display:flex;align-items:flex-start;gap:0.75rem;">
        <div style="font-size:1.4rem;line-height:1;">📚</div>
        <div>
          <div style="font-family:'Space Grotesk',sans-serif;font-size:0.9rem;font-weight:600;color:#E8EAF0;margin-bottom:0.25rem;">Curated Resources</div>
          <div style="font-size:0.78rem;color:#7B80A0;line-height:1.5;">Videos, articles and hands-on guides handpicked for each subtopic.</div>
        </div>
      </div>
      <div style="flex:1;min-width:180px;background:#1B1F2B;border:1px solid #252A38;border-radius:12px;padding:1.1rem 1.25rem;display:flex;align-items:flex-start;gap:0.75rem;">
        <div style="font-size:1.4rem;line-height:1;">🧠</div>
        <div>
          <div style="font-family:'Space Grotesk',sans-serif;font-size:0.9rem;font-weight:600;color:#E8EAF0;margin-bottom:0.25rem;">Quiz & Advance</div>
          <div style="font-size:0.78rem;color:#7B80A0;line-height:1.5;">Score ≥ 75% on each quiz to unlock the next subtopic and track your progress.</div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    topic = st.text_input("topic", placeholder="e.g.  Transformers in NLP,  Docker networking,  Calculus derivatives…")
    if st.button("Start Learning →"):
        if topic.strip():
            st.session_state.topic = topic.strip()
            st.session_state.phase = "loading"
            st.rerun()
        else:
            st.error("Please enter a topic to continue.")

    st.markdown("""
    <div style="text-align:center;margin-top:1rem;">
      <span style="font-size:0.78rem;color:#7B80A0;">Try: </span>
      <span style="font-size:0.78rem;color:#7B80A0;margin:0 0.4rem;">Machine Learning Basics</span>·
      <span style="font-size:0.78rem;color:#7B80A0;margin:0 0.4rem;">React Hooks</span>·
      <span style="font-size:0.78rem;color:#7B80A0;margin:0 0.4rem;">SQL Joins</span>·
      <span style="font-size:0.78rem;color:#7B80A0;margin:0 0.4rem;">Recursion</span>
    </div>
    """, unsafe_allow_html=True)


# ── LOADING ────────────────────────────────────────────────────────────────────
elif phase == "loading":
    st.markdown(f"""
    <div style="padding:2rem 0 1rem;text-align:center;">
      <div style="font-size:0.75rem;color:#7B80A0;letter-spacing:0.1em;text-transform:uppercase;margin-bottom:0.5rem;">Building your path</div>
      <div style="font-family:'Space Grotesk',sans-serif;font-size:1.8rem;font-weight:700;color:#E8EAF0;">{st.session_state.topic}</div>
    </div>
    """, unsafe_allow_html=True)

    with st.spinner("Generating subtopics and fetching resources…"):
        snapshot, interrupt_val = run_until_interrupt(
            inputs={
                "topic": st.session_state.topic,
                "current_topic_counter": 0,
                "score_per_subtopic": [],
                "user_answers": [],
            }
        )
        st.session_state.graph_state = snapshot.values
        st.session_state.phase = "resources" if interrupt_val is not None else "final"
    st.rerun()


# ── RESOURCES ─────────────────────────────────────────────────────────────────
elif phase == "resources":
    render_header()

    gs  = st.session_state.graph_state
    idx = gs.get("current_topic_counter", 0)
    sub = gs["sub_topic"].sub_topic[idx]

    st.markdown(f"""
    <div class="section-header">
      <div class="section-icon icon-blue">📚</div>
      <div>
        <div class="section-title">{sub.subtopic_name}</div>
        <div class="section-sub">Study these resources before the quiz</div>
      </div>
    </div>
    <p style="font-size:0.88rem;color:#7B80A0;line-height:1.55;margin-bottom:1.25rem;">{sub.breif}</p>
    """, unsafe_allow_html=True)

    resources = gs.get("resource_of_current_subtopic")
    if resources:
        for r in resources.resource:
            bdg = badge_html(r.type.lower())
            import html as html_mod
            why_raw = r.why_this_resource.replace("\n", " ").replace("\r", " ")
            why_raw = " ".join(why_raw.split())
            why_raw = html_mod.escape(why_raw)
            why = why_raw[:200] + ("…" if len(why_raw) > 200 else "")

            title_clean = html_mod.escape(r.title)
            url_clean   = r.url.replace('"', '%22')

            st.markdown(f"""
            <div class="resource-card">
              <div style="display:flex;flex-direction:column;align-items:flex-start;flex-shrink:0;padding-top:2px;">
                {bdg}
              </div>
              <div style="flex:1;min-width:0;">
                <div class="resource-title">
                  <a href="{url_clean}" target="_blank"
                     style="color:var(--text);text-decoration:none;word-break:break-word;">
                    {title_clean}
                  </a>
                </div>
                <div class="resource-why">{why}</div>
              </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    st.markdown('<p style="font-size:0.85rem;color:#7B80A0;margin-bottom:1rem;">When you\'re ready, take the quiz to move forward.</p>', unsafe_allow_html=True)

    if st.button("Take the Quiz →"):
        st.session_state.phase = "quiz"
        st.session_state.quiz_answers = []
        st.rerun()


# ── QUIZ ───────────────────────────────────────────────────────────────────────
elif phase == "quiz":
    render_header()

    gs   = st.session_state.graph_state
    idx  = gs.get("current_topic_counter", 0)
    sub  = gs["sub_topic"].sub_topic[idx]
    quiz = gs.get("quiz")

    st.markdown(f"""
    <div class="section-header">
      <div class="section-icon icon-purple">🧠</div>
      <div>
        <div class="section-title">Quiz: {sub.subtopic_name}</div>
        <div class="section-sub">Answer all 5 questions · Score ≥ 75% to advance</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    answers_collected = {}

    if quiz:
        for i, q in enumerate(quiz.question):
            st.markdown(f"""
            <div class="quiz-card">
              <div class="q-number">Question {i + 1} of {len(quiz.question)}</div>
              <div class="q-text">{q.question}</div>
            </div>
            """, unsafe_allow_html=True)

            chosen = st.radio(
                label=f"q{i}",
                options=[f"A.  {q.option.a}", f"B.  {q.option.b}",
                         f"C.  {q.option.c}", f"D.  {q.option.d}"],
                key=f"quiz_q_{i}",
                index=None,
                label_visibility="collapsed",
            )
            answers_collected[i] = chosen

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    all_answered = len(answers_collected) > 0 and all(v is not None for v in answers_collected.values())

    if not all_answered:
        st.markdown('<p style="font-size:0.82rem;color:#7B80A0;">Answer all questions to submit.</p>', unsafe_allow_html=True)

    if st.button("Submit Quiz →", disabled=not all_answered):
        # Map "A.  something" → "a"
        final_answers = [
            answers_collected[i][0].lower()
            for i in range(len(quiz.question))
        ]

        # ── Snapshot correct answers NOW, before the graph can replace the quiz
        correct_answers_snapshot = [
            q.correct_answer.strip().lower() for q in quiz.question
        ]
        # ── Also snapshot question objects so the breakdown shows the RIGHT quiz
        questions_snapshot = list(quiz.question)

        st.session_state.quiz_answers           = final_answers
        st.session_state.correct_answers_snap   = correct_answers_snapshot
        st.session_state.questions_snap         = questions_snapshot
        # ── FIX: snapshot the subtopic index NOW, before the graph advances
        #    current_topic_counter, so the score phase marks the correct pill green.
        st.session_state.submitted_topic_idx    = idx

        # ── FRONTEND SCORE CALCULATION (uses snapshot, immune to retry rewrites)
        score, total = compute_score(final_answers, correct_answers_snapshot)
        passed = (score / total * 100) >= 75 if total else False
        st.session_state.fe_score  = score
        st.session_state.fe_passed = passed
        # ─────────────────────────────────────────────────────────────────────

        with st.spinner("Submitting answers…"):
            snapshot, interrupt_val = run_until_interrupt(
                command=Command(resume=final_answers)
            )
            st.session_state.graph_state        = snapshot.values
            st.session_state.phase              = "score"
            st.session_state.graph_has_interrupt = interrupt_val is not None
        st.rerun()


# ── SCORE ──────────────────────────────────────────────────────────────────────
elif phase == "score":
    render_header()

    gs = st.session_state.graph_state

    # ── FIX: use the index snapshotted at submit time, not the (now-advanced)
    #    current_topic_counter from the graph, so we mark the RIGHT pill green.
    idx = st.session_state.get("submitted_topic_idx", gs.get("current_topic_counter", 0))

    # Always use the snapshotted questions & correct answers taken at submit time
    # so a retry-generated quiz never corrupts what's displayed here
    questions_snap       = st.session_state.get("questions_snap", [])
    correct_answers_snap = st.session_state.get("correct_answers_snap", [])
    user_answers         = st.session_state.get("quiz_answers", [])

    score  = st.session_state.fe_score
    total  = len(questions_snap) if questions_snap else 5
    pct    = int((score / total) * 100) if total else 0
    passed = st.session_state.fe_passed

    score_cls = "score-pass" if passed else "score-fail"
    msg = "Nicely done — moving on!" if passed else "Not quite — let's try a fresh quiz."

    # Mark done IMMEDIATELY when score is shown (using snapshotted idx) so
    # render_header() above already sees it on this very render.
    if passed:
        done = st.session_state.subtopics_done
        if not any(d.get("idx") == idx for d in done):
            done.append({"idx": idx, "score": score})
            st.session_state.subtopics_done = done

    st.markdown(f"""
    <div class="score-card">
      <div class="score-big {score_cls}">{score}<span style="font-size:1.5rem;color:#7B80A0;">/{total}</span></div>
      <div style="font-size:1rem;font-weight:600;margin:0.35rem 0 0.2rem;color:var(--text);">{pct}%</div>
      <div class="score-label">{"✅ Passed · " if passed else "❌ Below 75% · "}{msg}</div>
    </div>
    """, unsafe_allow_html=True)

    # Answer breakdown — rendered from snapshots, 100% stable
    if questions_snap and user_answers:
        st.markdown("""
        <div class="section-header">
          <div class="section-icon icon-green">📋</div>
          <div><div class="section-title">Answer Breakdown</div></div>
        </div>
        """, unsafe_allow_html=True)

        opt_getters = {
            "a": lambda q: q.option.a, "b": lambda q: q.option.b,
            "c": lambda q: q.option.c, "d": lambda q: q.option.d,
        }

        for i, q in enumerate(questions_snap):
            user_ans = user_answers[i] if i < len(user_answers) else "?"
            correct  = correct_answers_snap[i] if i < len(correct_answers_snap) else "?"
            is_correct = user_ans.strip().lower() == correct.strip().lower()
            row_cls    = "answer-correct" if is_correct else "answer-wrong"
            icon       = "✓" if is_correct else "✗"

            user_text    = opt_getters[user_ans](q) if user_ans in opt_getters else "?"
            correct_text = opt_getters[correct](q)  if correct  in opt_getters else "?"

            detail = (
                f"Correct: {correct.upper()}. {correct_text}"
                if is_correct else
                f"Your answer: {user_ans.upper()}. {user_text} &nbsp;·&nbsp; Correct: {correct.upper()}. {correct_text}"
            )
            expl = (" · " + q.explanation[:140]) if not is_correct and q.explanation else ""

            st.markdown(f"""
            <div class="{row_cls} answer-row">
              <span class="answer-icon">{icon}</span>
              <div class="answer-text">
                <strong>Q{i + 1}:</strong> {q.question[:90]}{"…" if len(q.question) > 90 else ""}
                <div class="answer-expl">{detail}{expl}</div>
              </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    graph_has_interrupt = st.session_state.get("graph_has_interrupt", False)

    if passed:
        if st.button("Continue →"):
            if graph_has_interrupt:
                st.session_state.phase = "resources"
            else:
                st.session_state.phase = "final"
            st.rerun()
    else:
        if st.button("Retry Quiz →"):
            if graph_has_interrupt:
                # Clear old radio selections so Streamlit doesn't pre-fill them
                for k in list(st.session_state.keys()):
                    if k.startswith("quiz_q_"):
                        del st.session_state[k]
                # Pull fresh quiz from graph (graph already ran generate_quiz again)
                config   = {"configurable": {"thread_id": st.session_state.thread_id}}
                snapshot = ai_tutor.get_state(config)
                st.session_state.graph_state        = snapshot.values
                st.session_state.quiz_answers       = []
                st.session_state.questions_snap     = []
                st.session_state.correct_answers_snap = []
                st.session_state.phase = "quiz"
            else:
                st.session_state.phase = "final"
            st.rerun()


# ── FINAL ──────────────────────────────────────────────────────────────────────
elif phase == "final":
    topic      = st.session_state.topic
    done_list  = st.session_state.subtopics_done   # [{idx, score}, ...]
    total_q    = len(done_list) * 5
    total_s    = sum(d.get("score", 0) for d in done_list)
    overall    = int((total_s / total_q) * 100) if total_q else 0
    oc         = "val-high" if overall >= 80 else ("val-mid" if overall >= 60 else "val-low")

    # Also pull subtopic names from graph state for the table
    gs        = st.session_state.graph_state or {}
    subtopics = gs.get("sub_topic")

    st.markdown(f"""
    <div class="final-card">
      <div class="final-icon">🎓</div>
      <div class="final-title">Course Complete!</div>
      <div class="final-sub">You finished <strong style="color:var(--accent2)">{topic}</strong> — here's how you did.</div>
    </div>
    <div class="score-card" style="margin-bottom:1.25rem;">
      <div class="score-big {oc}">{overall}<span style="font-size:1.5rem;color:#7B80A0;">%</span></div>
      <div class="score-label">Overall score across {len(done_list)} subtopics</div>
    </div>
    """, unsafe_allow_html=True)

    if done_list:
        st.markdown("""
        <div class="section-header">
          <div class="section-icon icon-purple">📊</div>
          <div><div class="section-title">Score by Subtopic</div></div>
        </div>
        """, unsafe_allow_html=True)

        for d in done_list:
            idx  = d.get("idx", 0)
            sc   = d.get("score", 0)
            name = subtopics.sub_topic[idx].subtopic_name if subtopics and idx < len(subtopics.sub_topic) else f"Subtopic {idx + 1}"
            vc   = score_color(sc, 5)
            st.markdown(f"""
            <div class="score-row">
              <span class="score-row-name">{name}</span>
              <span class="score-row-val {vc}">{sc}/5 ({int(sc / 5 * 100)}%)</span>
            </div>
            """, unsafe_allow_html=True)

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    if st.button("Start a New Topic →"):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.rerun()