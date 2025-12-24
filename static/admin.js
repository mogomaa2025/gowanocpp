document.addEventListener('DOMContentLoaded', function() {
    const questionList = document.getElementById('question-list');
    if (questionList) {
        const sortable = new Sortable(questionList, {
            animation: 150,
            handle: '.handle',
            ghostClass: 'blue-background-class'
        });

        document.getElementById('save-order-btn').addEventListener('click', () => {
            const questions = Array.from(questionList.children).map(item => ({
                id: parseInt(item.dataset.id),
                page: parseInt(item.querySelector('[data-page-input]').value)
            }));
            
            fetch('/api/admin/questions/reorder', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ questions: questions })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('Order saved successfully!');
                    location.reload();
                } else {
                    alert('Error saving order: ' + (data.error || 'Unknown error'));
                }
            });
        });

        questionList.addEventListener('click', function(e) {
            if (e.target.closest('[data-delete-btn]')) {
                const item = e.target.closest('.question-item');
                const questionId = item.dataset.id;
                if (confirm(`Are you sure you want to delete question ${questionId}?`)) {
                    fetch(`/api/admin/question/${questionId}`, { method: 'DELETE' })
                        .then(response => response.json())
                        .then(data => {
                            if(data.success) {
                                item.remove();
                                location.reload(); // Reload to show re-ordered questions
                            } else {
                                alert('Error deleting question: ' + (data.error || 'Unknown error'));
                            }
                        });
                }
            }
        });
    }
});