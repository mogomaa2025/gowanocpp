# C++ Learning Corner

## Project Description
This is a full-stack web application built with Flask, designed to serve as a comprehensive learning platform for C++. It provides structured learning content through explainers (lectures), interactive quizzes, and video resources. The application supports user authentication, tracks session data, and includes an administrative panel for content management.

## Features
*   **User Authentication:** Secure login for users.
*   **Interactive Dashboard:** Personalized user dashboard for tracking progress.
*   **C++ Explainers:** Structured lecture content for various C++ topics.
*   **Quizzes:** Interactive quizzes (`questions_X.json`) to test knowledge.
*   **Video Resources:** Dedicated section for learning videos (`videos.json`).
*   **Session Tracking:** Stores user session data (`data/sessions/`).
*   **Admin Panel:** Tools for managing explainers, quizzes, and other content.
*   **Static Assets:** Custom CSS and JavaScript for a responsive and interactive user experience.
  
## Screenshots
<img width="817" height="890" alt="image" src="https://github.com/user-attachments/assets/c2c9935b-0f3a-42c2-b04a-3b0b38925e92" />
<img width="559" height="487" alt="image" src="https://github.com/user-attachments/assets/7ecb289a-40b2-4ea4-8ff0-233845e7a464" />
<img width="832" height="892" alt="image" src="https://github.com/user-attachments/assets/e9ca547f-1343-45e4-b424-2907c7ac4294" />
<img width="1124" height="921" alt="image" src="https://github.com/user-attachments/assets/2a6f0ead-6b18-4858-93ea-1c5b25d0ebe1" />
<img width="1496" height="929" alt="image" src="https://github.com/user-attachments/assets/d52b9a45-0f38-4443-bd37-41c2e7ce86e3" />
<img width="772" height="945" alt="image" src="https://github.com/user-attachments/assets/7f1d1b64-2cb6-4917-a7f0-b3447df5b114" />
<img width="772" height="945" alt="image" src="https://github.com/user-attachments/assets/6569f787-94d9-4846-85d9-8ade3f4e5370" />

## Setup Instructions

### Prerequisites
*   Python 3.x
*   `pip` (Python package installer)

### Installation
1.  **Clone the repository:**
    ```bash
    git clone <your-repository-url>
    cd cpplearningcorner
    ```
2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv venv
    .\venv\Scripts\activate # On Windows
    source venv/bin/activate # On macOS/Linux
    ```
3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Configure application settings:**
    Edit `app_settings.json` with your desired configuration (e.g., secret key, database path).

5.  **Run the application:**
    ```bash
    python flask_app.py
    ```
    The application should now be running on `http://127.0.0.1:5000` (or another port if configured).

## Project Structure
```
.
├───app_settings.json
├───flask_app.py
├───README.md
├───requirements.txt
├───data/
│   ├───explainers.json
│   ├───page-title.json
│   ├───questions_0.json
│   ├───... (other questions.json files)
│   ├───videos.json
│   └───sessions/
│       └───... (session data files)
├───static/
│   ├───admin.js
│   ├───custom.css
│   ├───custom.js
│   ├───favicon.ico
│   └───tracking.js
└───templates/
    ├───admin_panel.html
    ├───dashboard.html
    ├───explainer_admin.html
    ├───explainer.html
    ├───home.html
    ├───index.html
    ├───login.html
    ├───quiz_dashboard.html
    ├───videos.html
    └───explainer_content/
        ├───lecture1.html
        ├───... (other lecture html files)
        └───tricks.html
└───tests/
    ├───test_add_edit_delete.py
    ├───test_api.py
    ├───test_questions.py
    ├───test_reorder.py
    ├───test_security.py
    └───test_xss.py
```

