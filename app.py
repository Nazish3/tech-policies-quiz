import streamlit as st

from quiz.models import Question, QuizEngine
from quiz.storage import DEFAULT_PATH, append_attempt, read_attempts
from quiz.utils import is_valid_name, normalise_name, score_percentage


def load_questions():
    # 10 questions: mix of multiple choice + true/false
    return [
        Question(
            qid="SEC-001",
            qtype="multiple_choice",
            prompt="What is the BEST action if you receive a suspicious email link?",
            options=[
                "Click it to see where it goes",
                "Forward it to everyone to warn them",
                "Report it using the company's phishing process",
                "Reply asking if it's real",
            ],
            correct_index=2,
            explanation="Suspicious links should be reported using the approved reporting method.",
        ),
        Question(
            qid="SEC-002",
            qtype="true_false",
            prompt="True or False: It's okay to reuse the same password if it is very complex.",
            options=["True", "False"],
            correct_index=1,
            explanation="Passwords should be unique; reuse increases risk across systems.",
        ),
        Question(
            qid="DATA-001",
            qtype="multiple_choice",
            prompt="Before sharing customer data internally, you should:",
            options=[
                "Share it if the person asks for it",
                "Check classification and verify access need-to-know",
                "Post it in a team chat for convenience",
                "Send the full file to save time",
            ],
            correct_index=1,
            explanation="Data handling follows classification and least-privilege access.",
        ),
        Question(
            qid="INC-001",
            qtype="multiple_choice",
            prompt="If your laptop is lost, what should you do FIRST?",
            options=[
                "Wait to see if it turns up",
                "Tell your friend",
                "Report immediately through the incident process",
                "Buy a new one and move on",
            ],
            correct_index=2,
            explanation="Lost devices are security incidents and must be reported promptly.",
        ),
        Question(
            qid="ACC-001",
            qtype="true_false",
            prompt="True or False: MFA (Multi-Factor Authentication) reduces the risk of account compromise.",
            options=["True", "False"],
            correct_index=0,
            explanation="MFA adds an extra layer of security beyond passwords.",
        ),
        Question(
            qid="POL-001",
            qtype="multiple_choice",
            prompt="Which is the BEST example of acceptable use of company systems?",
            options=[
                "Installing unapproved software to work faster",
                "Sharing your login with a teammate for convenience",
                "Using approved tools for work and following policy",
                "Downloading random browser extensions as needed",
            ],
            correct_index=2,
            explanation="Approved tools and policy compliance reduce security and legal risk.",
        ),
        Question(
            qid="PRIV-001",
            qtype="multiple_choice",
            prompt="What is the safest way to handle confidential documents?",
            options=[
                "Store them on a personal USB",
                "Email them to your personal account to access later",
                "Store them in approved secured locations with access controls",
                "Share them in public channels to get faster feedback",
            ],
            correct_index=2,
            explanation="Confidential data must be stored using approved secured services.",
        ),
        Question(
            qid="SOC-001",
            qtype="true_false",
            prompt="True or False: You should verify identity before sharing sensitive information, even internally.",
            options=["True", "False"],
            correct_index=0,
            explanation="Social engineering can happen internally; verify identity and need-to-know.",
        ),
        Question(
            qid="DEV-001",
            qtype="multiple_choice",
            prompt="In secure development, secrets (API keys, passwords) should be:",
            options=[
                "Hardcoded in the source code for reliability",
                "Stored in a public GitHub repo so the team can access",
                "Stored in environment variables or a secrets manager",
                "Shared in chat when needed",
            ],
            correct_index=2,
            explanation="Secrets should never be hardcoded; use secure secret storage.",
        ),
        Question(
            qid="NET-001",
            qtype="multiple_choice",
            prompt="Which connection is safest on public Wi‑Fi?",
            options=[
                "No protection needed if you trust the café",
                "Using a VPN and HTTPS services",
                "Turning off your firewall",
                "Using any network labelled 'Free Wi‑Fi'",
            ],
            correct_index=1,
            explanation="VPN + HTTPS reduces interception risk on public networks.",
        ),
    ]


def init_state():
    if "engine" not in st.session_state:
        st.session_state.engine = None
    if "name" not in st.session_state:
        st.session_state.name = ""
    if "started" not in st.session_state:
        st.session_state.started = False
    if "last_result" not in st.session_state:
        st.session_state.last_result = None
    if "saved_this_run" not in st.session_state:
        st.session_state.saved_this_run = False


st.set_page_config(page_title="Tech Policies Quiz", page_icon="🛡️", layout="centered")
init_state()

st.title("🛡️ Tech Policies Quiz (MVP)")
st.write("A short workplace quiz on security and policy basics.")


# Sidebar: Attempts info + download
with st.sidebar:
    st.header("📁 Attempts")
    attempts = read_attempts(DEFAULT_PATH)
    st.write(f"Saved attempts: **{len(attempts)}**")

    if attempts:
        try:
            with open(DEFAULT_PATH, "rb") as f:
                st.download_button(
                    "Download attempts CSV",
                    data=f.read(),
                    file_name="attempts.csv",
                    mime="text/csv",
                )
        except OSError:
            st.caption("Could not read CSV for download (file access issue).")

    st.caption("CSV includes timestamp, name, score, percentage, and missed questions.")


# Start screen
if not st.session_state.started:
    st.subheader("Start")
    name_input = st.text_input(
        "Your name",
        value=st.session_state.name,
        placeholder="e.g., Nazish Jujara"
    )
    st.session_state.name = name_input

    if st.button("Start Quiz"):
        cleaned = normalise_name(name_input)
        if not is_valid_name(cleaned):
            st.error("Please enter a valid name (2–40 letters, spaces, hyphen, apostrophe).")
        else:
            st.session_state.engine = QuizEngine(load_questions())
            st.session_state.started = True
            st.session_state.last_result = None
            st.session_state.saved_this_run = False
            st.rerun()

else:
    engine: QuizEngine = st.session_state.engine

    if engine.is_finished():
        st.success("Quiz complete! ✅")
        pct = score_percentage(engine.score, engine.total)
        st.metric("Score", f"{engine.score}/{engine.total}", f"{pct}%")

        # Save attempt ONCE per completion (prevents duplicates on rerun)
        if not st.session_state.saved_this_run:
            try:
                append_attempt(
                    DEFAULT_PATH,
                    normalise_name(st.session_state.name),
                    engine.score,
                    engine.total,
                    pct,
                    missed=engine.missed_questions(),
                    answers=engine.answers_summary(),
                )
                st.info("Attempt saved to CSV (includes missed questions).")
            except OSError as e:
                st.warning(str(e))
            st.session_state.saved_this_run = True

        st.subheader("Review")
        for item in engine.results_breakdown():
            if item["is_correct"]:
                st.write("✅", item["question"])
            else:
                st.write("❌", item["question"])
                st.caption(f"Your answer: {item['selected']}")
                st.caption(f"Correct answer: {item['correct']}")
            if item["explanation"]:
                st.caption(item["explanation"])
            st.divider()

        if st.button("Restart"):
            st.session_state.started = False
            st.session_state.engine = None
            st.session_state.last_result = None
            st.session_state.saved_this_run = False
            st.rerun()

    else:
        q = engine.current_question()
        st.subheader(f"Question {engine.current_index + 1} of {engine.total}")
        st.write(q.prompt)

        choice = st.radio("Select an answer:", q.options, index=None)

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Submit"):
                if choice is None:
                    st.error("Please choose an answer before submitting.")
                else:
                    selected_index = q.options.index(choice)
                    correct = engine.answer_current(selected_index)
                    st.session_state.last_result = correct
                    st.rerun()

        with col2:
            if st.session_state.last_result is not None:
                st.write("✅ Correct!" if st.session_state.last_result else "❌ Not quite.")