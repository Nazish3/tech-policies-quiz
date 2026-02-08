import pytest
from quiz.models import Question, QuizEngine


def test_engine_scores_correct_answers():
    questions = [
        Question("Q1", "true_false", "T/F?", ["True", "False"], 0),
        Question("Q2", "multiple_choice", "MCQ?", ["a", "b"], 1),
    ]
    engine = QuizEngine(questions)

    assert engine.answer_current(0) is True   # correct
    assert engine.answer_current(0) is False  # wrong
    assert engine.score == 1
    assert engine.is_finished() is True


def test_engine_requires_questions():
    with pytest.raises(ValueError):
        QuizEngine([])


def test_engine_missed_questions_returns_only_incorrect():
    questions = [
        Question("Q1", "true_false", "T/F?", ["True", "False"], 0),
        Question("Q2", "multiple_choice", "MCQ?", ["a", "b"], 1),
    ]
    engine = QuizEngine(questions)

    engine.answer_current(1)  # wrong
    engine.answer_current(1)  # correct

    missed = engine.missed_questions()
    assert len(missed) == 1
    assert missed[0]["qid"] == "Q1"