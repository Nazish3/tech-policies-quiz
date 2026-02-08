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