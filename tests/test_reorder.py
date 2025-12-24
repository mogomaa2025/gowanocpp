from app import app, get_all_questions

def test_reorder_questions():
    with app.test_client() as c:
        with c.session_transaction() as sess:
            sess['admin_logged_in'] = True
        questions = get_all_questions()
        if len(questions) < 2:
            return  # Not enough questions to reorder
        orig_ids = [q['id'] for q in questions]
        new_ids = orig_ids[::-1]
        resp = c.post('/api/admin/questions/reorder', json={'question_ids': new_ids})
        assert resp.status_code == 200
        assert resp.get_json()['success']
        # Restore original order
        c.post('/api/admin/questions/reorder', json={'question_ids': orig_ids})
