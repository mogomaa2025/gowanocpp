from app import app, get_all_questions

def test_add_edit_delete_question():
    with app.test_client() as c:
        with c.session_transaction() as sess:
            sess['admin_logged_in'] = True
        # Add
        resp = c.post('/api/admin/question', json={
            'question': 'Test Q',
            'options': [{'id': 'A', 'text': '1'}, {'id': 'B', 'text': '2'}],
            'correct_answer': 'A',
            'explanation': 'Test E'
        })
        assert resp.status_code == 200
        qid = resp.get_json()['question']['id']
        # Edit
        resp = c.put(f'/api/admin/question/{qid}', json={
            'question': 'Test Q2',
            'options': [{'id': 'A', 'text': '1'}, {'id': 'B', 'text': '2'}],
            'correct_answer': 'B',
            'explanation': 'Test E2'
        })
        assert resp.status_code == 200
        # Delete
        resp = c.delete(f'/api/admin/question/{qid}')
        assert resp.status_code == 200
        assert resp.get_json()['success']
