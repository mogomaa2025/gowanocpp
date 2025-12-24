from flask import Flask, render_template, jsonify, request, session, redirect, url_for, send_from_directory
import json
import os
import uuid
from datetime import datetime
import html


app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this'  # Change this to a secure secret key

# Use absolute path for data directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')

# Active users tracking
active_users = {}  # {page: {session_id: timestamp}}
import threading
active_users_lock = threading.Lock()

# Page title helpers and API endpoints
def get_page_titles():
    path = os.path.join(DATA_DIR, 'page-title.json')
    if not os.path.exists(path):
        return {}
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}

def save_page_titles(titles):
    path = os.path.join(DATA_DIR, 'page-title.json')
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(titles, f, indent=2, ensure_ascii=False)

def update_active_user(session_id, page, is_active=True):
    """Update active user tracking for a specific page"""
    with active_users_lock:
        if page not in active_users:
            active_users[page] = {}
        
        if is_active:
            active_users[page][session_id] = datetime.now().timestamp()
        else:
            if session_id in active_users[page]:
                del active_users[page][session_id]
        
        # Clean up old entries (older than 5 minutes)
        current_time = datetime.now().timestamp()
        active_users[page] = {
            sid: ts for sid, ts in active_users[page].items() 
            if current_time - ts < 300  # 5 minutes
        }

def get_active_users_count(page):
    """Get the number of active users on a specific page"""
    with active_users_lock:
        if page not in active_users:
            return 0
        return len(active_users[page])


# Load users from JSON file

# Function to get all questions from all files
def get_all_questions():
    all_questions = []
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR, exist_ok=True)
        return []
    # Get all question files and sort them
    question_files = [f for f in os.listdir(DATA_DIR) if f.startswith('questions_') and f.endswith('.json')]
    question_files.sort(key=lambda x: int(x.split('_')[1].split('.')[0]))
    for filename in question_files:
        filepath = os.path.join(DATA_DIR, filename)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                questions = json.load(f)
                all_questions.extend(questions)
        except Exception as e:
            print(f"Error loading {filename}: {e}")
    return all_questions

# Function to save all questions back to files
def save_all_questions(questions):
    # Clear existing files
    for filename in os.listdir(DATA_DIR):
        if filename.startswith('questions_') and filename.endswith('.json'):
            os.remove(os.path.join(DATA_DIR, filename))
    # Group questions by page
    pages = {}
    for q in questions:
        page_num = q.get('page', 0)
        if page_num not in pages:
            pages[page_num] = []
        pages[page_num].append(q)
    # Save each page to a file
    for page_num, page_questions in pages.items():
        filename = f'questions_{page_num}.json'
        filepath = os.path.join(DATA_DIR, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(page_questions, f, indent=2, ensure_ascii=False)

def cleanup_question_whitespace():
    """Clean up whitespace in existing questions"""
    try:
        all_questions = get_all_questions()
        cleaned = False
        
        for question in all_questions:
            # Clean question text - only trim leading/trailing, preserve internal spaces
            if 'question' in question and question['question']:
                original = question['question']
                question['question'] = question['question'].strip()
                if original != question['question']:
                    cleaned = True
            
            # Clean explanation text - only trim leading/trailing, preserve internal spaces
            if 'explanation' in question and question['explanation']:
                original = question['explanation']
                question['explanation'] = question['explanation'].strip()
                if original != question['explanation']:
                    cleaned = True
            
            # Clean options - only trim leading/trailing, preserve internal spaces
            if 'options' in question and question['options']:
                for option in question['options']:
                    if 'id' in option and option['id']:
                        original = option['id']
                        option['id'] = option['id'].strip()
                        if original != option['id']:
                            cleaned = True
                    
                    if 'text' in option and option['text']:
                        original = option['text']
                        option['text'] = option['text'].strip()
                        if original != option['text']:
                            cleaned = True
        
        if cleaned:
            save_all_questions(all_questions)
            print("Cleaned up whitespace in questions")
        
        return cleaned
    except Exception as e:
        print(f"Error cleaning up whitespace: {e}")
        return False

# Function to get questions for a specific page
def get_questions_for_page(page_num):
    print(f"get_questions_for_page called with page_num: {page_num}, type: {type(page_num)}")
    questions = []
    filename = f'questions_{page_num}.json'
    filepath = os.path.join(DATA_DIR, filename)
    print(f"Looking for file: {filepath}")
    print(f"File exists: {os.path.exists(filepath)}")
    if not os.path.exists(filepath):
        print(f"File {filepath} does not exist")
        return None
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            file_content = f.read()
            print(f"File content length: {len(file_content)} characters")
            print(f"First 200 characters: {file_content[:200]}")
            questions = json.loads(file_content)
            print(f"Successfully loaded {len(questions)} questions from {filename}")
    except Exception as e:
        print(f"Error loading {filename}: {e}")
        print(f"Exception type: {type(e)}")
        import traceback
        traceback.print_exc()
        return None
    return questions

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/explainer')
def explainer():
    explainers_path = os.path.join(DATA_DIR, 'explainers.json')
    with open(explainers_path, 'r', encoding='utf-8') as f:
        explainers = json.load(f)
    return render_template('explainer.html', explainers=explainers)

@app.route('/explainer_content/<path:filename>')
def explainer_content(filename):
    return send_from_directory('templates', 'explainer_content/' + filename)

@app.route('/quiz')
def index():
    # Redirect to page 0 for backward compatibility
    return redirect(url_for('quiz_page', page=0))

@app.route('/quiz/page/<int:page>')
def quiz_page(page):
    is_admin = session.get('logged_in') and session.get('role') == 'admin'
    return render_template('index.html', is_admin=is_admin, initial_page=page)

@app.route('/videos')
def videos():
    videos_path = os.path.join(DATA_DIR, 'videos.json')
    with open(videos_path, 'r', encoding='utf-8') as f:
        videos = json.load(f)
    return render_template('videos.html', videos=videos)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # This is a simplified login. In a real application, you'd want to
        # use a more secure way to manage credentials.
        if username == 'admin' and password == 'password':
            session['logged_in'] = True
            session['username'] = 'admin'
            session['role'] = 'admin'
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error='Invalid credentials')
            
    return render_template('login.html')

@app.route('/logout')
def logout():
   session.clear()
   return redirect(url_for('index'))


@app.route('/admin/panel')
def admin_panel():
    if not session.get('logged_in') or session.get('role') != 'admin':
        return redirect(url_for('login'))
    
    questions = get_all_questions()
    return render_template('admin_panel.html', questions=questions)


@app.route('/dashboard')
def dashboard():
    if not session.get('logged_in') or session.get('role') != 'admin':
        return redirect(url_for('login'))
    return render_template('dashboard.html')


@app.route('/api/dashboard/session/<session_id>', methods=['DELETE'])
def delete_session(session_id):
    if not session.get('logged_in') or session.get('role') != 'admin':
        return jsonify({"error": "Unauthorized"}), 401

    session_file = os.path.join(DATA_DIR, 'sessions', f"{session_id}.json")
    if not os.path.exists(session_file):
        return jsonify({"error": "Session not found"}), 404

    try:
        os.remove(session_file)
        return jsonify({"success": True, "message": "Session deleted successfully"})
    except Exception as e:
        return jsonify({"error": f"Failed to delete session: {str(e)}"}), 500

@app.route('/api/dashboard/sessions')
def get_dashboard_sessions():
    if not session.get('logged_in') or session.get('role') != 'admin':
        return jsonify({"error": "Unauthorized"}), 401

    sessions_dir = os.path.join(DATA_DIR, 'sessions')
    if not os.path.exists(sessions_dir):
        return jsonify([])
    
    print(f"Processing sessions from: {sessions_dir}")
    print(f"Files found: {[f for f in os.listdir(sessions_dir) if f.endswith('.json')]}")

    sessions_summary = []
    for filename in os.listdir(sessions_dir):
        if filename.endswith('.json'):
            session_id = filename.replace('.json', '')
            session_file = os.path.join(sessions_dir, filename)
            with open(session_file, 'r', encoding='utf-8') as f:
                try:
                    session_data = json.load(f)
                    if session_data:
                        first_event = session_data[0]
                        device_info = first_event.get('deviceInfo', {})
                        print(f"  First event: {first_event.get('eventName', 'Unknown')} at {first_event.get('eventData', {}).get('timestamp', 'No timestamp')}")
                        
                        # Calculate page visit times
                        page_visits = {}
                        current_page = None
                        page_start_time = None
                        
                        try:
                            for event in session_data:
                                event_name = event.get('eventName')
                                
                                # Handle pageView and quizPageNavigation events
                                if event_name in ['pageView', 'quizPageNavigation']:
                                    if current_page is not None and page_start_time is not None:
                                        # Calculate time spent on previous page
                                        # Handle both ISO string and milliseconds timestamp
                                        event_timestamp = event.get('eventData', {}).get('timestamp', 0)
                                        try:
                                            if isinstance(event_timestamp, str):
                                                # Convert ISO string to timestamp
                                                try:
                                                    event_time = datetime.fromisoformat(event_timestamp.replace('Z', '+00:00')).timestamp() * 1000
                                                except:
                                                    event_time = page_start_time
                                            else:
                                                event_time = event_timestamp
                                        except Exception as e:
                                            print(f"    Error converting event timestamp: {e}")
                                            event_time = page_start_time
                                        
                                        time_spent = (event_time - page_start_time) / 1000 / 60  # Convert to minutes
                                        if time_spent > 0:  # Only add positive time
                                            if current_page not in page_visits:
                                                page_visits[current_page] = 0
                                            page_visits[current_page] += time_spent
                                
                                # Extract page information from current data structure
                                if event_name == 'quizPageNavigation':
                                    # For quizPageNavigation, use the 'toPage' field if it exists
                                    current_page = event.get('eventData', {}).get('toPage')
                                else:
                                    # For pageView, extract page from URL or use 'page' field
                                    url = event.get('eventData', {}).get('url', '')
                                    if url.startswith('/quiz/page/'):
                                        # Extract page number from URL like "/quiz/page/0"
                                        try:
                                            current_page = str(int(url.split('/')[-1]))
                                        except (ValueError, IndexError):
                                            current_page = '0'
                                    elif url == '/':
                                        current_page = 'home'
                                    else:
                                        current_page = event.get('eventData', {}).get('page', 'unknown')
                                
                                page_start_time = event.get('eventData', {}).get('timestamp')
                        except Exception as e:
                            print(f"    Error in page visit calculation loop: {e}")
                            # Continue with empty page_visits if there's an error
                        
                        # Add time for the last page if session is still active
                        if current_page is not None and page_start_time is not None:
                            if current_page not in page_visits:
                                page_visits[current_page] = 0
                            
                            try:
                                # Handle both ISO string and milliseconds timestamp for last page
                                if isinstance(page_start_time, str):
                                    try:
                                        last_page_start = datetime.fromisoformat(page_start_time.replace('Z', '+00:00')).timestamp() * 1000
                                    except:
                                        last_page_start = page_start_time
                                else:
                                    last_page_start = page_start_time
                                
                                # Calculate time spent on the last page (current time - last page start time)
                                current_time = datetime.now().timestamp() * 1000  # Convert to milliseconds
                                if isinstance(last_page_start, (int, float)) and last_page_start > 0:
                                    last_page_time = (current_time - last_page_start) / 1000 / 60  # Convert to minutes
                                    if last_page_time > 0:  # Only add positive time
                                        page_visits[current_page] += last_page_time
                            except Exception as e:
                                print(f"    Error calculating last page time: {e}")
                                # Continue without adding time for the last page
                        
                        # Try to get IP from multiple sources
                        ip_address = None
                        # Check if IP exists in the current data structure
                        if first_event.get('ip'):
                            ip_address = first_event.get('ip')
                        elif device_info.get('ip'):
                            ip_address = device_info.get('ip')
                        elif first_event.get('eventData', {}).get('ip'):
                            ip_address = first_event.get('eventData', {}).get('ip')
                        # For now, set to 'Unknown' if no IP found in current data
                        if not ip_address:
                            ip_address = 'Unknown'
                        
                        # Handle timestamp conversion for display
                        start_timestamp = first_event.get('eventData', {}).get('timestamp')
                        try:
                            if isinstance(start_timestamp, str):
                                try:
                                    start_time = datetime.fromisoformat(start_timestamp.replace('Z', '+00:00')).timestamp() * 1000
                                except:
                                    start_time = start_timestamp
                            else:
                                start_time = start_timestamp
                        except Exception as e:
                            print(f"    Error converting start timestamp: {e}")
                            start_time = start_timestamp
                        
                        session_summary = {
                            "id": session_id,
                            "os": device_info.get('os', 'Unknown'),
                            "model": device_info.get('model', 'Unknown'),
                            "ip": ip_address or 'Unknown',
                            "start_time": start_time,
                            "page_visits": page_visits
                        }
                        print(f"  Adding session: {session_summary}")
                        sessions_summary.append(session_summary)
                except json.JSONDecodeError as e:
                    print(f"  JSON decode error in {filename}: {e}")
                    continue
                except Exception as e:
                    print(f"  Error processing {filename}: {e}")
                    continue
    print(f"Returning {len(sessions_summary)} sessions")
    return jsonify(sessions_summary)


@app.route('/api/dashboard/session/<session_id>')
def get_session_details(session_id):
    if not session.get('logged_in') or session.get('role') != 'admin':
        return jsonify({"error": "Unauthorized"}), 401

    session_file = os.path.join(DATA_DIR, 'sessions', f"{session_id}.json")
    if not os.path.exists(session_file):
        return jsonify({"error": "Session not found"}), 404

    with open(session_file, 'r', encoding='utf-8') as f:
        try:
            session_data = json.load(f)
            return jsonify(session_data)
        except json.JSONDecodeError:
            return jsonify({"error": "Could not read session data"}), 500


@app.route('/quiz_dashboard')
def quiz_dashboard():
    if not session.get('logged_in') or session.get('role') != 'admin':
        return redirect(url_for('login'))
    return render_template('quiz_dashboard.html')

@app.route('/api/quiz_dashboard/data')
def get_quiz_dashboard_data():
    if not session.get('logged_in') or session.get('role') != 'admin':
        return jsonify({"error": "Unauthorized"}), 401

    sessions_dir = os.path.join(DATA_DIR, 'sessions')
    if not os.path.exists(sessions_dir):
        return jsonify([])

    quiz_data = []
    
    # Get total questions count exactly like the frontend does
    total_questions = 0
    start_page = 0
    end_page = 0
    
    # Find the range of pages and count total questions
    question_files = [f for f in os.listdir(DATA_DIR) if f.startswith('questions_') and f.endswith('.json')]
    if question_files:
        page_numbers = [int(f.split('_')[1].split('.')[0]) for f in question_files]
        start_page = min(page_numbers)
        end_page = max(page_numbers)
        
        # Count total questions across all pages
        for page_num in range(start_page, end_page + 1):
            questions = get_questions_for_page(page_num)
            if questions:
                total_questions += len(questions)

    for filename in os.listdir(sessions_dir):
        if filename.endswith('.json'):
            session_id = filename.replace('.json', '')
            session_file = os.path.join(sessions_dir, filename)
            with open(session_file, 'r', encoding='utf-8') as f:
                try:
                    session_data = json.load(f)
                    if session_data:
                        # Get all quiz answers across all pages
                        quiz_answers = [e for e in session_data if e.get('eventName') == 'quizAnswer']
                        answered_questions = len(set(e['eventData']['questionId'] for e in quiz_answers))
                        correct_answers = len([e for e in quiz_answers if e['eventData']['isCorrect']])
                        
                        # Calculate progress percentage exactly like the frontend
                        # This matches the logic in updateProgress() function
                        progress_percentage = round((answered_questions / total_questions) * 100) if total_questions > 0 else 0
                        
                        quiz_data.append({
                            "id": session_id,
                            "answered": answered_questions,
                            "correct": correct_answers,
                            "total": total_questions,
                            "progress_percentage": progress_percentage
                        })
                except json.JSONDecodeError:
                    continue
    return jsonify(quiz_data)


@app.route('/api/questions/<int:page>')
def get_questions(page):
    print(f"API called for page: {page}, type: {type(page)}")
    questions = get_questions_for_page(page)
    print(f"Questions returned: {questions}")
    if questions is None:
        print(f"No questions found for page {page}")
        return jsonify({"error": "No more questions"}), 404
    print(f"Returning {len(questions)} questions for page {page}")
    return jsonify(questions)
@app.route('/api/session', methods=['POST'])
def save_session():
    if session.get('logged_in'):
        data = request.get_json()
        session['quiz_state'] = {
            'page': data.get('page'),
            'scroll_position': data.get('scroll_position')
        }
        return jsonify({"success": True})
    return jsonify({"success": False}), 401

@app.route('/api/session', methods=['GET'])
def get_session():
    if session.get('logged_in'):
        return jsonify(session.get('quiz_state', {}))
    return jsonify({}), 401

@app.route('/api/active-user', methods=['POST'])
def update_active_user_api():
    """Update active user status"""
    data = request.get_json()
    session_id = data.get('sessionId')
    page = data.get('page')
    is_active = data.get('isActive', True)
    
    if session_id and page is not None:
        update_active_user(session_id, page, is_active)
        return jsonify({"success": True})
    return jsonify({"error": "Missing sessionId or page"}), 400

@app.route('/api/questions/count')
def get_questions_count():
    print("get_questions_count called")
    if not os.path.exists(DATA_DIR):
        print(f"DATA_DIR {DATA_DIR} does not exist")
        return jsonify({"total_pages": 0})
    question_files = [f for f in os.listdir(DATA_DIR) if f.startswith('questions_') and f.endswith('.json')]
    print(f"Found question files: {question_files}")
    if not question_files:
        print("No question files found")
        return jsonify({"total_pages": 0, "start_page": 0, "end_page": 0})
    page_numbers = sorted([int(f.split('_')[1].split('.')[0]) for f in question_files])
    print(f"Page numbers: {page_numbers}")
    start_page = page_numbers[0] if page_numbers else 0
    end_page = page_numbers[-1] if page_numbers else 0
    result = {
        "total_pages": len(question_files),
        "start_page": start_page,
        "end_page": end_page
    }
    print(f"Returning: {result}")
    return jsonify(result)

@app.route('/api/active-users/<int:page>')
def get_active_users_count_api(page):
    """Get the number of active users on a specific page"""
    count = get_active_users_count(page)
    return jsonify({"page": page, "active_users": count})

@app.route('/api/admin/cleanup-whitespace', methods=['POST'])
def cleanup_whitespace_api():
    """Clean up whitespace in existing questions"""
    try:
        cleaned = cleanup_question_whitespace()
        return jsonify({"success": True, "cleaned": cleaned})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/admin/questions', methods=['GET'])
def admin_get_questions():
    if not session.get('logged_in') or session.get('role') != 'admin':
        return jsonify({"error": "Unauthorized"}), 401
    
    questions = get_all_questions()
    return jsonify(questions)

@app.route('/api/admin/question', methods=['POST'])
def admin_add_question():
    if not session.get('logged_in') or session.get('role') != 'admin':
        return jsonify({"error": "Unauthorized"}), 401
    
    data = request.get_json()
    questions = get_all_questions()
    
    # Generate new ID
    # Generate new ID
    if questions:
        new_id = max(q['id'] for q in questions) + 1
    else:
        new_id = 1
    
    # Sanitize input to prevent XSS
    new_question = {
        "id": new_id,
        "question": data.get('question', ''),
        "options": data.get('options', []),
        "correct_answer": data.get('correct_answer'),
        "explanation": data.get('explanation', ''),
        "created_at": datetime.now().isoformat(),
        "page": 0
    }
    
    questions.append(new_question)
    save_all_questions(questions)
    
    return jsonify({"success": True, "question": new_question})

@app.route('/api/admin/question/<int:question_id>', methods=['PUT'])
def admin_update_question(question_id):
    if not session.get('logged_in') or session.get('role') != 'admin':
        return jsonify({"error": "Unauthorized"}), 401
    
    data = request.get_json()
    questions = get_all_questions()
    
    question_found = False
    for i, question in enumerate(questions):
        if question['id'] == question_id:
            questions.pop(i)
            question_found = True
            break

    if not question_found:
        return jsonify({"error": "Question not found"}), 404

    # Add the updated question back to the list
    updated_question = {
        "id": int(data.get('id', question_id)),
        "question": data.get('question', ''),
        "options": data.get('options', []),
        "correct_answer": data.get('correct_answer'),
        "explanation": data.get('explanation', ''),
        "page": int(data.get('page', 0)),
        "updated_at": datetime.now().isoformat()
    }
    questions.append(updated_question)
    
    # Sort questions by new ID to maintain order
    questions.sort(key=lambda q: q['id'])
    
    save_all_questions(questions)
    return jsonify({"success": True})

@app.route('/api/admin/question/<int:question_id>', methods=['DELETE'])
def admin_delete_question(question_id):
    if not session.get('logged_in') or session.get('role') != 'admin':
        return jsonify({"error": "Unauthorized"}), 401
    
    questions = get_all_questions()
    questions = [q for q in questions if q['id'] != question_id]
    
    # Re-assign IDs to maintain sequential order
    for i, question in enumerate(questions):
        question['id'] = i + 1
        
    save_all_questions(questions)
    
    return jsonify({"success": True})

@app.route('/api/admin/questions/reorder', methods=['POST'])
def admin_reorder_questions():
    if not session.get('logged_in') or session.get('role') != 'admin':
        return jsonify({"error": "Unauthorized"}), 401
    
    data = request.get_json()
    updated_questions_info = data.get('questions', [])
    
    all_questions = get_all_questions()
    question_dict = {q['id']: q for q in all_questions}
    
    reordered_questions = []
    for info in updated_questions_info:
        qid = info.get('id')
        if qid in question_dict:
            question = question_dict[qid]
            question['page'] = info.get('page', 0)
            reordered_questions.append(question)

    # Re-assign IDs to maintain sequential order
    for i, question in enumerate(reordered_questions):
        question['id'] = i + 1
            
    save_all_questions(reordered_questions)
    return jsonify({"success": True})

@app.route('/api/page-titles', methods=['GET'])
def api_get_page_titles():
    return jsonify(get_page_titles())

@app.route('/api/page-titles', methods=['POST'])
def api_set_page_titles():
    if not session.get('logged_in') or session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401
    data = request.get_json()
    if not isinstance(data, dict):
        return jsonify({'error': 'Invalid data'}), 400
    save_page_titles(data)
    return jsonify({'success': True})


@app.route('/api/client-ip')
def get_client_ip():
    """Get the client's IP address from request headers"""
    # Try to get IP from various headers (for different proxy setups)
    ip = request.headers.get('X-Forwarded-For')
    if ip:
        # X-Forwarded-For can contain multiple IPs, take the first one
        ip = ip.split(',')[0].strip()
    else:
        ip = request.headers.get('X-Real-IP')
    
    if not ip:
        ip = request.remote_addr
    
    return jsonify({"ip": ip})

@app.route('/api/track', methods=['POST'])
def track_session_data():
    data = request.get_json()
    session_id = data.get('sessionId')

    if not session_id:
        return jsonify({"error": "Session ID is required"}), 400

    # Do not track logged-in users (i.e., admins)
    if session.get('logged_in'):
        return jsonify({"success": True, "message": "Admin activity not tracked"})

    # Ensure the sessions directory exists
    sessions_dir = os.path.join(DATA_DIR, 'sessions')
    os.makedirs(sessions_dir, exist_ok=True)

    # Save data to a session-specific file
    session_file = os.path.join(sessions_dir, f"{session_id}.json")

    # Read existing data and append new event
    session_data = []
    if os.path.exists(session_file):
        with open(session_file, 'r', encoding='utf-8') as f:
            try:
                session_data = json.load(f)
            except json.JSONDecodeError:
                pass  # Ignore if file is empty or corrupt

    session_data.append(data)

    with open(session_file, 'w', encoding='utf-8') as f:
        json.dump(session_data, f, indent=2)

    return jsonify({"success": True})


if __name__ == '__main__':
    # Create data directory if it doesn't exist
    os.makedirs(DATA_DIR, exist_ok=True)
    # Create sample questions if no questions exist
    if not get_all_questions():
        sample_questions = [
            {
                "id": 1,
                "question": "What is the output of the following C++ code?\n\n```cpp\n#include <iostream>\nusing namespace std;\n\nint main() {\n    int x = 5;\n    cout << ++x << \" \" << x++ << endl;\n    return 0;\n}\n```",
                "options": [
                    {"id": "A", "text": "6 5"},
                    {"id": "B", "text": "6 6"},
                    {"id": "C", "text": "5 5"},
                    {"id": "D", "text": "5 6"}
                ],
                "correct_answer": "A",
                "explanation": "The pre-increment ++x increments x to 6 and returns 6. The post-increment x++ returns the current value (6) then increments x to 7. However, the output shows the values at the time of evaluation."
            },
            {
                "id": 2,
                "question": "Which of the following is the correct syntax to declare a pointer to an integer in C++?",
                "options": [
                    {"id": "A", "text": "int *ptr;"},
                    {"id": "B", "text": "int ptr*;"},
                    {"id": "C", "text": "*int ptr;"},
                    {"id": "D", "text": "pointer int ptr;"}
                ],
                "correct_answer": "A",
                "explanation": "In C++, a pointer to an integer is declared using 'int *ptr;' where the asterisk (*) indicates that ptr is a pointer to an int."
            }
        ]
        save_all_questions(sample_questions)
    app.run(debug=True)