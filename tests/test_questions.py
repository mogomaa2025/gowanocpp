from app import app, get_all_questions

def test_questions_exist():
    questions = get_all_questions()
    assert isinstance(questions, list)
    assert len(questions) > 0
    for q in questions:
        assert 'id' in q
        assert 'question' in q
        assert 'options' in q
        assert 'correct_answer' in q
        assert 'explanation' in q
