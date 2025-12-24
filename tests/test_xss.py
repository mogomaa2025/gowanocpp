from app import app
import html

def test_xss_sanitization():
    malicious = '<img src=x onerror=alert(1)>'
    with app.test_client() as c:
        with c.session_transaction() as sess:
            sess['admin_logged_in'] = True
        resp = c.post('/api/admin/question', json={
            'question': malicious,
            'options': [{'id': 'A', 'text': malicious}, {'id': 'B', 'text': 'ok'}],
            'correct_answer': 'A',
            'explanation': malicious
        })
        assert resp.status_code == 200
        data = resp.get_json()
        assert html.escape(malicious) in data['question']['question']
        assert html.escape(malicious) in data['question']['explanation']
        assert html.escape(malicious) in data['question']['options'][0]['text']
