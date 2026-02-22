![CI](https://github.com/Nazish3/tech-policies-quiz/actions/workflows/ci.yml/badge.svg)

# Tech Policies Quiz (MVP)

A Python + Streamlit quiz application designed to improve workplace awareness of key technology and security policies. This MVP demonstrates a full software development lifecycle including design, implementation, testing, continuous integration, documentation and deployment.

**Live App:**  
https://tech-policies-quiz-mwynmdjqnexj2j9jedpdf4.streamlit.app


# 1. Introduction

Modern technology organisations depend heavily on employees understanding and consistently following internal policies relating to cybersecurity, data protection, acceptable use of systems and incident reporting. Human error remains one of the largest causes of security incidents and policy awareness naturally fades over time when reinforced only during onboarding. Staff may forget reporting procedures, overlook data‑handling guidelines, or underestimate risks around phishing emails or public Wi‑Fi usage.

To address this, the **Tech Policies Quiz MVP** offers a practical, interactive way for employees to refresh essential policy knowledge in a low‑pressure format. The quiz is intentionally short (10 questions) and covers real‑world workplace scenarios involving password hygiene, MFA, data classification, lost devices, phishing, acceptable use, secure development and safe network practices. Each question includes an explanation to reinforce learning immediately after answering.

This project demonstrates a complete professional development workflow suitable for junior developers, apprentices, and technical roles. The application uses **Python** for logic, **Streamlit** for the graphical user interface, **CSV** for persistent attempt storage, **pytest** for automated testing, and **GitHub Actions** for continuous integration. It follows modular software architecture principles: separating UI, logic (QuizEngine), data models, storage functions and pure validation utilities. This improves maintainability, testability, and extensibility of the system.

The application’s attempt logging supports basic analytics — capturing timestamped results, user names, score percentages, missed questions, and answer summaries. This enables teams or training departments to identify common misunderstanding areas and reinforce weak points in staff knowledge.

Overall, this MVP provides a lightweight yet realistic example of how internal training tools can be built, tested, deployed and documented using modern software development practices.


# 2. Design Section

## 2.1 GUI Design (Figma Prototypes)

The interface was prototyped using Figma to visualise the user journey and ensure a simple, accessible and professional user experience.

### Start Screen  
![Start](figma_start.png)

### Question Screen  
![Question](figma_question.png)

### Results Screen  
![Results](figma_results.png)


## 2.2 Functional Requirements

| Requirement | Description |
|---|---|
| Display 10 questions | Must present all quiz questions sequentially. |
| Mixed question types | Supports multiple-choice and true/false. |
| Name validation | User must enter a valid name to start. |
| Progress tracking | Shows question number and updates after each answer. |
| Answer submission | Only one answer allowed per question. |
| Scoring | Calculates total score and percentage. |
| Review system | Shows detailed feedback including explanations. |
| Persistent storage | Saves every attempt into CSV. |
| CSV export | Allows staff to download attempts from the sidebar. |


## 2.3 Non‑Functional Requirements

| Category | Requirement |
|---|---|
| Usability | Clean UI, minimal steps, simple navigation. |
| Performance | Instant responses, no visible lag. |
| Reliability | Handles errors gracefully (CSV write errors, invalid names). |
| Maintainability | Modular folder structure. |
| Testability | Pure functions implemented for validation and scoring. |
| Security | Stores minimal non-sensitive data; no credentials stored. |
| Accessibility | Clear text, spacing, consistent layout. |


## 2.4 Tech Stack

- **Python 3**
- **Streamlit** — GUI framework
- **Pytest** — automated testing
- **GitHub Actions** — continuous integration
- **CSV** — persistent storage
- **Figma** — UI/UX prototyping
- **Git & GitHub** — version control and CI/CD


## 2.5 Code Design (Class Diagram)

![UML](uml_class_diagram.png)


# 3. Development Section

The project follows a modular structure to separate responsibilities and support testability.

```text
tech-policies-quiz/
├── app.py
├── README.md
├── requirements.txt
├── quiz/
│   ├── __init__.py
│   ├── models.py
│   ├── storage.py
│   └── utils.py
├── tests/
│   ├── conftest.py
│   ├── test_engine.py
│   └── test_utils.py
└── data/
    └── attempts.csv (auto-created)
```

## 3.1 Logic Layer (quiz/models.py)

The Question class represents each quiz item:

from dataclasses import dataclass
from typing import List, Literal, Dict, Any

QuestionType = Literal["multiple_choice", "true_false"]

@dataclass(frozen=True)
class Question:
    """Represents a single question (multiple choice or true/false)."""
    qid: str
    qtype: QuestionType
    prompt: str
    options: List[str]
    correct_index: int
    explanation: str = ""

The QuizEngine manages scoring, progress, and answer tracking:

class QuizEngine:
    """
    Runs quiz logic independent of the GUI.
    Tracks progress, stores answers, calculates score.
    """

    def __init__(self, questions: List[Question]):
        if not questions:
            raise ValueError("Quiz must contain at least one question.")
        self._questions = questions
        self._current = 0
        self._score = 0
        self._answers = []  # (question_index, selected_index, is_correct)

    @property
    def current_index(self) -> int:
        return self._current

    @property
    def score(self) -> int:
        return self._score

    @property
    def total(self) -> int:
        return len(self._questions)

    def current_question(self) -> Question:
        return self._questions[self._current]

    def answer_current(self, selected_index: int) -> bool:
        """Answers the current question, updates score, and moves forward."""
        q = self.current_question()
        is_correct = (selected_index == q.correct_index)
        self._answers.append((self._current, selected_index, is_correct))
        if is_correct:
            self._score += 1
        self._current += 1
        return is_correct

    def is_finished(self) -> bool:
        return self._current >= len(self._questions)

    def answers_summary(self) -> List[Dict[str, Any]]:
        """Structured summary of all answers (good for storage and analytics)."""
        summary = []
        for q_index, selected, is_correct in self._answers:
            q = self._questions[q_index]
            summary.append({
                "qid": q.qid,
                "type": q.qtype,
                "prompt": q.prompt,
                "selected_index": selected,
                "selected_text": q.options[selected] if 0 <= selected < len(q.options) else "Invalid",
                "correct_index": q.correct_index,
                "correct_text": q.options[q.correct_index],
                "is_correct": is_correct
            })
        return summary

    def missed_questions(self) -> List[Dict[str, Any]]:
        """Only the incorrect answers (useful for training insights)."""
        return [a for a in self.answers_summary() if not a["is_correct"]]

    def results_breakdown(self) -> List[Dict[str, Any]]:
        """Detailed breakdown for the review screen, including explanations."""
        breakdown = []
        for q_index, selected, is_correct in self._answers:
            q = self._questions[q_index]
            breakdown.append({
                "qid": q.qid,
                "type": q.qtype,
                "question": q.prompt,
                "selected": q.options[selected] if 0 <= selected < len(q.options) else "Invalid",
                "correct": q.options[q.correct_index],
                "is_correct": is_correct,
                "explanation": q.explanation,
            })
        return breakdown


## 3.2 Utility Layer (quiz/utils.py)

Validation and scoring functions are implemented as pure functions:

```python
import re

def normalise_name(name: str) -> str:
    """
    Pure function: trims whitespace and collapses multiple spaces.
    Example: "  Nazish   Jujara " -> "Nazish Jujara"
    """
    return " ".join((name or "").strip().split())

def is_valid_name(name: str) -> bool:
    """
    Pure function: validates a user name.
    Rules:
    - 2 to 40 characters
    - letters/spaces/hyphen/apostrophe allowed
    - must start with a letter
    """
    cleaned = normalise_name(name)
    if not (2 <= len(cleaned) <= 40):
        return False
    return bool(re.fullmatch(r"[A-Za-z][A-Za-z\s'\-]*", cleaned))

def score_percentage(score: int, total: int) -> int:
    """
    Pure function: returns score as a percentage (0-100).
    Raises ValueError if inputs are invalid.
    """
    if total <= 0:
        raise ValueError("Total must be greater than 0.")
    if score < 0 or score > total:
        raise ValueError("Score must be between 0 and total.")
    return round((score / total) * 100)
```

## 3.3 Storage Layer (quiz/storage.py)

## 3.3 Storage Layer (quiz/storage.py)

Attempts are stored in CSV for persistence and easy export.  
Missed questions and full answers are stored as JSON strings inside CSV columns.

```python
import csv
import os
import json
from datetime import datetime
from typing import List, Dict, Any

DEFAULT_PATH = os.path.join("data", "attempts.csv")

def ensure_data_dir(path: str) -> None:
    """Creates the parent folder for the CSV if it doesn't exist."""
    os.makedirs(os.path.dirname(path), exist_ok=True)

def append_attempt(path, name, score, total, percentage, missed, answers) -> None:
    """
    Appends a quiz attempt to CSV.
    Missed questions and full answers are stored as JSON strings.
    """
    ensure_data_dir(path)
    file_exists = os.path.exists(path)

    row = {
        "timestamp": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "name": name,
        "score": score,
        "total": total,
        "percentage": percentage,
        "missed_questions": json.dumps(missed, ensure_ascii=False),
        "answers": json.dumps(answers, ensure_ascii=False),
    }

    try:
        with open(path, mode="a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=row.keys())
            if not file_exists:
                writer.writeheader()
            writer.writerow(row)
    except OSError as e:
        raise OSError(f"Failed to write attempts CSV: {e}") from e

def read_attempts(path: str) -> List[Dict[str, str]]:
    """Reads quiz attempts from CSV; returns empty list if file not found."""
    if not os.path.exists(path):
        return []
    try:
        with open(path, mode="r", newline="", encoding="utf-8") as f:
            return list(csv.DictReader(f))
    except OSError as e:
        raise OSError(f"Failed to read attempts CSV: {e}") from e
```

## 3.4 GUI Layer (app.py)
Streamlit handles the interface and application flow:

Start screen (name input + validation)
Quiz flow (radio options and submit)
Results and explanations
CSV download via sidebar
Session state to keep progress and avoid duplicate saves

# 4. Testing Section

## 4.1 Testing Strategy

Automated testing (pytest) covers:

name validation
percentage scoring
QuizEngine logic
missed questions behaviour

Manual GUI testing covers:

navigation
validation messages
CSV saving and download
restart logic

## 4.2 Manual Test Table

| Test ID | Description        | Expected              | Actual | Pass |
|---------|--------------------|------------------------|--------|------|
| MT01    | Invalid name       | Error shown            | Works  | ✔    |
| MT02    | Valid name         | Quiz starts            | Works  | ✔    |
| MT03    | No answer selected | Error shown            | Works  | ✔    |
| MT04    | Submit answer      | Goes to next question  | Works  | ✔    |
| MT05    | Finish quiz        | Shows score            | Works  | ✔    |
| MT06    | Save attempt       | CSV updated            | Works  | ✔    |
| MT07    | Download CSV       | Works                  | Works  | ✔    |
| MT08    | Restart quiz       | Returns to start       | Works  | ✔    |

## 4.3 Unit Test Output

![alt text](tests_passed.png)

# 5. Documentation Section

## 5.1 User Documentation

Enter name
Click Start Quiz
Select an answer and Submit
Review score and explanations
Download CSV (sidebar) if needed
Click Restart Quiz to retake

## 5.2 Technical Documentation

Install: pip install -r requirements.txt
Run: streamlit run app.py
Test: pytest

# 6. Deployment Section

Streamlit Cloud Deployment
Live App:
https://tech-policies-quiz-mwynmdjqnexj2j9jedpdf4.streamlit.app

Streamlit Cloud provides zero‑configuration hosting from GitHub and quick redeploys, which is ideal for small internal tools and MVPs.

# 7. Evaluation Section

This project was a valuable learning experience across the full development lifecycle. Designing the UI in Figma provided clarity before coding. Streamlit made GUI development accessible without needing separate frontend frameworks. Keeping logic (QuizEngine), utilities and storage separate made the code easier to work with and test.
Understanding Streamlit’s rerun behaviour took some trial and error; using session_state and saving once at completion avoided duplicate CSV rows. Storing detail as JSON inside a CSV kept the data simple but still useful for basic analysis. Future improvements could include a question bank, randomisation, accessibility improvements, an analytics dashboard, and optional authentication.
Overall, the project demonstrates practical software engineering practices: modular design, testing with CI, persistent storage, documentation and a live deployment.