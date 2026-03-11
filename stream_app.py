import streamlit as st
from pymongo import MongoClient
from urllib.parse import urlparse
from admin import admin_dashboard, manage_students, manage_questions
from student import student_dashboard, student_assignments, student_data
from github import BadCredentialsException, Github, UnknownObjectException
import requests
from datetime import datetime
import os
import re

# ─────────────────────────────────────────────
#  THEME  — injected once, before any widget
# ─────────────────────────────────────────────
def inject_css():
    st.markdown("""
    <style>
    /* ── Google Fonts ── */
    @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:ital,wght@0,300;0,400;0,500;1,300&display=swap');

    /* ── CSS Variables ── */
    :root {
        --bg:        #0a0c10;
        --surface:   #111318;
        --border:    #1e2128;
        --accent:    #4f8ef7;
        --accent2:   #7c3aed;
        --success:   #22c55e;
        --warning:   #f59e0b;
        --danger:    #ef4444;
        --text:      #e8eaf0;
        --muted:     #6b7280;
        --radius:    12px;
    }

    /* ── Global Reset ── */
    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif;
        background-color: var(--bg) !important;
        color: var(--text) !important;
    }

    /* ── Hide Streamlit chrome ── */
    #MainMenu, footer, header { visibility: hidden; }
    .stDeployButton { display: none; }

    /* ── App container ── */
    .block-container {
        padding: 2rem 3rem !important;
        max-width: 1100px !important;
    }

    /* ── Headings ── */
    h1, h2, h3, h4, h5 {
        font-family: 'Syne', sans-serif !important;
        letter-spacing: -0.02em;
        color: var(--text) !important;
    }
    h1 { font-size: 2.4rem !important; font-weight: 800 !important; }
    h2 { font-size: 1.7rem !important; font-weight: 700 !important; }
    h3 { font-size: 1.25rem !important; font-weight: 600 !important; }

    /* ── Sidebar ── */
    [data-testid="stSidebar"] {
        background: var(--surface) !important;
        border-right: 1px solid var(--border) !important;
        padding-top: 1rem;
    }
    [data-testid="stSidebar"] .stRadio > label {
        font-family: 'Syne', sans-serif !important;
        font-size: 0.7rem !important;
        font-weight: 600 !important;
        letter-spacing: 0.12em !important;
        text-transform: uppercase;
        color: var(--muted) !important;
        margin-bottom: 0.5rem;
    }
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label {
        display: flex;
        align-items: center;
        padding: 0.55rem 0.9rem !important;
        border-radius: 8px !important;
        margin-bottom: 2px !important;
        font-size: 0.9rem !important;
        font-weight: 500 !important;
        color: var(--muted) !important;
        transition: all 0.15s ease;
        cursor: pointer;
    }
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label:hover {
        background: rgba(79,142,247,0.08) !important;
        color: var(--accent) !important;
    }
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label[data-selected="true"] {
        background: rgba(79,142,247,0.12) !important;
        color: var(--accent) !important;
    }

    /* ── Cards ── */
    .card {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: var(--radius);
        padding: 1.8rem 2rem;
        margin-bottom: 1.2rem;
    }
    .card-sm {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: var(--radius);
        padding: 1.2rem 1.4rem;
        margin-bottom: 0.8rem;
    }

    /* ── Inputs ── */
    .stTextInput > div > div > input,
    .stTextArea > div > textarea {
        background: #16181f !important;
        border: 1px solid var(--border) !important;
        border-radius: 8px !important;
        color: var(--text) !important;
        font-family: 'DM Sans', sans-serif !important;
        font-size: 0.93rem !important;
        padding: 0.6rem 0.9rem !important;
        transition: border-color 0.15s;
    }
    .stTextInput > div > div > input:focus,
    .stTextArea > div > textarea:focus {
        border-color: var(--accent) !important;
        box-shadow: 0 0 0 3px rgba(79,142,247,0.15) !important;
        outline: none !important;
    }
    .stTextInput label, .stTextArea label {
        color: var(--muted) !important;
        font-size: 0.8rem !important;
        font-weight: 500 !important;
        letter-spacing: 0.04em !important;
        text-transform: uppercase;
        margin-bottom: 4px;
    }

    /* ── Buttons ── */
    .stButton > button {
        background: var(--accent) !important;
        color: #fff !important;
        border: none !important;
        border-radius: 8px !important;
        font-family: 'Syne', sans-serif !important;
        font-weight: 600 !important;
        font-size: 0.88rem !important;
        letter-spacing: 0.05em !important;
        text-transform: uppercase;
        padding: 0.55rem 1.4rem !important;
        transition: all 0.18s ease !important;
        box-shadow: 0 4px 14px rgba(79,142,247,0.3);
    }
    .stButton > button:hover {
        background: #6fa2ff !important;
        box-shadow: 0 6px 20px rgba(79,142,247,0.45) !important;
        transform: translateY(-1px);
    }
    .stButton > button:active { transform: translateY(0) !important; }

    /* ── Alerts ── */
    .stSuccess > div, .stSuccess {
        background: rgba(34,197,94,0.1) !important;
        border: 1px solid rgba(34,197,94,0.3) !important;
        border-radius: 8px !important;
        color: #4ade80 !important;
    }
    .stError > div, .stError {
        background: rgba(239,68,68,0.1) !important;
        border: 1px solid rgba(239,68,68,0.3) !important;
        border-radius: 8px !important;
        color: #f87171 !important;
    }
    .stWarning > div, .stWarning {
        background: rgba(245,158,11,0.1) !important;
        border: 1px solid rgba(245,158,11,0.3) !important;
        border-radius: 8px !important;
        color: #fbbf24 !important;
    }
    .stInfo > div, .stInfo {
        background: rgba(79,142,247,0.08) !important;
        border: 1px solid rgba(79,142,247,0.25) !important;
        border-radius: 8px !important;
        color: #93c5fd !important;
    }

    /* ── Spinner ── */
    .stSpinner > div { border-top-color: var(--accent) !important; }

    /* ── Divider ── */
    hr { border-color: var(--border) !important; margin: 1.5rem 0; }

    /* ── Scrollbar ── */
    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: var(--bg); }
    ::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }
    ::-webkit-scrollbar-thumb:hover { background: var(--muted); }

    /* ── Custom header bar ── */
    .portal-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0.8rem 0 1.4rem;
        border-bottom: 1px solid var(--border);
        margin-bottom: 2rem;
    }
    .portal-logo {
        font-family: 'Syne', sans-serif;
        font-size: 1.15rem;
        font-weight: 800;
        letter-spacing: -0.01em;
        color: var(--text);
    }
    .portal-logo span { color: var(--accent); }
    .user-pill {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: rgba(79,142,247,0.1);
        border: 1px solid rgba(79,142,247,0.25);
        border-radius: 999px;
        padding: 5px 14px 5px 10px;
        font-size: 0.85rem;
        font-weight: 500;
        color: var(--accent);
    }
    .user-dot {
        width: 8px; height: 8px;
        background: var(--success);
        border-radius: 50%;
        display: inline-block;
    }

    /* ── Feature cards on homepage ── */
    .feature-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
        gap: 1rem;
        margin: 1.5rem 0;
    }
    .feature-card {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: var(--radius);
        padding: 1.4rem;
        transition: border-color 0.2s, transform 0.2s;
    }
    .feature-card:hover {
        border-color: var(--accent);
        transform: translateY(-3px);
    }
    .feature-icon { font-size: 1.8rem; margin-bottom: 0.6rem; }
    .feature-title {
        font-family: 'Syne', sans-serif;
        font-weight: 700;
        font-size: 0.95rem;
        margin-bottom: 0.3rem;
        color: var(--text);
    }
    .feature-desc { font-size: 0.82rem; color: var(--muted); line-height: 1.5; }

    /* ── Step timeline ── */
    .step-row {
        display: flex;
        gap: 1rem;
        align-items: flex-start;
        padding: 1rem 0;
        border-bottom: 1px solid var(--border);
    }
    .step-row:last-child { border-bottom: none; }
    .step-num {
        min-width: 32px; height: 32px;
        background: linear-gradient(135deg, var(--accent), var(--accent2));
        border-radius: 8px;
        display: flex; align-items: center; justify-content: center;
        font-family: 'Syne', sans-serif;
        font-weight: 800; font-size: 0.85rem;
        color: #fff;
        flex-shrink: 0;
    }
    .step-content-title {
        font-family: 'Syne', sans-serif;
        font-weight: 700;
        font-size: 0.95rem;
        margin-bottom: 0.2rem;
        color: var(--text);
    }
    .step-content-desc { font-size: 0.83rem; color: var(--muted); line-height: 1.5; }

    /* ── Badge ── */
    .badge {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 999px;
        font-size: 0.72rem;
        font-weight: 600;
        letter-spacing: 0.04em;
        text-transform: uppercase;
    }
    .badge-blue  { background: rgba(79,142,247,0.15); color: #93c5fd; }
    .badge-green { background: rgba(34,197,94,0.15);  color: #4ade80; }
    .badge-purple{ background: rgba(124,58,237,0.15); color: #c4b5fd; }

    /* ── Sidebar brand ── */
    .sidebar-brand {
        font-family: 'Syne', sans-serif;
        font-weight: 800;
        font-size: 1.1rem;
        color: var(--text);
        padding: 0.5rem 1rem 1.2rem;
        border-bottom: 1px solid var(--border);
        margin-bottom: 1rem;
    }
    .sidebar-brand span { color: var(--accent); }

    /* ── Auth form wrapper ── */
    .auth-wrapper {
        max-width: 480px;
        margin: 2rem auto;
    }
    </style>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  MongoDB
# ─────────────────────────────────────────────
username_db = "streamapp"
password_db = "Dipa%401234"
connection_string = (
    f"mongodb+srv://{username_db}:{password_db}"
    "@cluster0.zs1k9wi.mongodb.net/?retryWrites=true&w=majority"
)

def connect_to_mongo():
    try:
        client = MongoClient(connection_string)
        db = client.Question
        return db
    except Exception as e:
        st.error(f"Error connecting to MongoDB: {e}")
        return None


# ─────────────────────────────────────────────
#  Helpers
# ─────────────────────────────────────────────
def extract_owner_repo(github_url):
    github_url = github_url.rstrip(".git")
    parsed_url = urlparse(github_url)
    path_parts = parsed_url.path.strip("/").split("/")
    if len(path_parts) >= 2:
        return path_parts[0], path_parts[1]
    return None, None


def is_github_repo_public(github_token, owner, repo):
    try:
        g = Github(github_token)
        repository = g.get_repo(f"{owner}/{repo}")
        if repository.private:
            st.error("GitHub repository is private.")
            return False
        repository.get_contents("")
        return True
    except UnknownObjectException:
        st.error("Token does not have access to this repository.")
        return False
    except Exception:
        st.error("Error accessing GitHub repository. Ensure it exists and the token is correct.")
        return False


def validate_username(username):
    pattern = r"^AF0[3-4][0-7]\d{4}$"
    return bool(re.match(pattern, username))


def check_repo_visibility(owner, repo, headers):
    repo_url = f"https://api.github.com/repos/{owner}/{repo}"
    response = requests.get(repo_url, headers=headers)
    if response.status_code == 200:
        repo_data = response.json()
        if repo_data.get("private"):
            st.warning("The repository is private.")
            return False
        return True
    st.error(f"Unable to fetch repository details (Status {response.status_code})")
    return False


def fetch_commits_and_files(owner, repo, db, headers, username):
    commits_url = f"https://api.github.com/repos/{owner}/{repo}/commits"
    page = 1
    collection_name = username

    if collection_name in db.list_collection_names():
        db[collection_name].drop()

    while True:
        response = requests.get(
            f"{commits_url}?page={page}&per_page=100", headers=headers
        )
        if response.status_code == 200:
            commits = response.json()
            if not commits:
                break

            for commit in commits:
                sha = commit["sha"]
                commit_date = commit["commit"]["committer"]["date"]
                commit_datetime = datetime.strptime(commit_date, "%Y-%m-%dT%H:%M:%SZ")
                formatted_date = commit_datetime.strftime("%Y-%m-%d")
                formatted_time = commit_datetime.strftime("%H:%M:%S")
                commit_message = commit["commit"]["message"]

                commit_detail_url = (
                    f"https://api.github.com/repos/{owner}/{repo}/commits/{sha}"
                )
                commit_detail_response = requests.get(commit_detail_url, headers=headers)
                if commit_detail_response.status_code == 200:
                    commit_data = commit_detail_response.json()
                    files = commit_data.get("files", [])

                    added_java_files = {}
                    modified_java_files = {}
                    renamed_java_files = {}
                    deleted_java_files = {}

                    for file in files:
                        if file["filename"].endswith(".java"):
                            status = file["status"]
                            filename = os.path.splitext(
                                os.path.basename(file["filename"])
                            )[0]

                            if status == "renamed":
                                previous_filename = os.path.splitext(
                                    os.path.basename(file.get("previous_filename", ""))
                                )[0]
                                renamed_java_files[previous_filename] = filename
                                raw_url = file.get("raw_url")
                                if raw_url:
                                    file_response = requests.get(raw_url, headers=headers)
                                    if file_response.status_code == 200:
                                        modified_java_files[filename] = file_response.text

                            elif status in ["added", "modified"]:
                                raw_url = file.get("raw_url")
                                file_content = ""
                                if raw_url:
                                    file_response = requests.get(raw_url, headers=headers)
                                    if file_response.status_code == 200:
                                        file_content = file_response.text
                                if status == "added":
                                    added_java_files[filename] = file_content
                                elif status == "modified":
                                    modified_java_files[filename] = file_content

                            elif status == "removed":
                                deleted_java_files[filename] = ""

                    commit_doc = {
                        "commit_id": sha,
                        "commit_date": formatted_date,
                        "commit_time": formatted_time,
                        "commit_message": commit_message,
                        "added_java_files": added_java_files,
                        "modified_java_files": modified_java_files,
                        "renamed_java_files": renamed_java_files,
                        "deleted_java_files": deleted_java_files,
                    }
                    db[collection_name].insert_one(commit_doc)
            page += 1
        else:
            st.error(f"Error fetching commits: {response.status_code}")
            break


# ─────────────────────────────────────────────
#  Auth pages
# ─────────────────────────────────────────────
def login():
    st.markdown('<div class="auth-wrapper">', unsafe_allow_html=True)
    st.markdown("""
        <div style='margin-bottom:2rem;'>
            <div style='font-family:Syne,sans-serif;font-size:1.8rem;font-weight:800;
                        color:#e8eaf0;line-height:1.1;'>Welcome back</div>
            <div style='color:#6b7280;font-size:0.92rem;margin-top:6px;'>
                Sign in to your portal account
            </div>
        </div>
    """, unsafe_allow_html=True)

    client = MongoClient(connection_string)
    login_db = client["LoginData"]

    username = st.text_input("Username", placeholder="e.g. AF0442897")
    password = st.text_input("Password", type="password", placeholder="••••••••")

    if st.button("Sign In →"):
        user = login_db.users.find_one({"username": username, "password": password})
        if user:
            st.session_state["logged_in"] = True
            st.session_state["username"] = username
            st.session_state["role"] = user["role"]
            st.success(f"Welcome back, {user['name']}!")

            if user["role"] == "admin":
                st.session_state["current_page"] = "Admin Dashboard"
            else:
                github_link = user['github_link']
                github_token = user['github_token']
                name = user['name']
                owner, repo = extract_owner_repo(github_link)
                HEADERS = {"Authorization": f"token {github_token}"}
                with st.spinner("Syncing your repository data…"):
                    if check_repo_visibility(owner, repo, HEADERS):
                        db = client.JavaFileAnalysis
                        fetch_commits_and_files(owner, repo, db, HEADERS, name)
                        st.success("Repository synced successfully")
                st.session_state["current_page"] = "Student Dashboard"

            st.rerun()
        else:
            st.error("Invalid username or password")

    st.markdown("</div>", unsafe_allow_html=True)


def register_user():
    st.markdown('<div class="auth-wrapper">', unsafe_allow_html=True)
    st.markdown("""
        <div style='margin-bottom:2rem;'>
            <div style='font-family:Syne,sans-serif;font-size:1.8rem;font-weight:800;
                        color:#e8eaf0;line-height:1.1;'>Create account</div>
            <div style='color:#6b7280;font-size:0.92rem;margin-top:6px;'>
                Register your GitHub repository to get started
            </div>
        </div>
    """, unsafe_allow_html=True)

    client = MongoClient(connection_string)
    login_db = client["LoginData"]

    name = st.text_input("Full Name", placeholder="Enter your full name")
    username = st.text_input("Username", placeholder="e.g. AF0300001")
    github_link = st.text_input("GitHub Repository URL", placeholder="https://github.com/user/repo")
    github_token = st.text_input("GitHub Token", type="password", placeholder="ghp_xxxxxxxxxxxx")

    valid_name = bool(name.strip())
    valid_username = validate_username(username)
    valid_github = False
    valid_token = bool(github_token)
    password = None

    if github_link and github_token:
        owner, repo = extract_owner_repo(github_link)
        if owner and repo and is_github_repo_public(github_token, owner, repo):
            st.success("✓ Repository verified and accessible")
            valid_github = True
            password = st.text_input("Set Password", type="password", placeholder="Create a strong password")
        else:
            st.error("Repository is private or inaccessible.")

    errors = []
    if name and not valid_name:
        errors.append("Name cannot be empty.")
    if username and not valid_username:
        errors.append("Username format must be AF0300000 – AF0479999.")

    if errors:
        st.error("  ·  ".join(errors))

    if valid_name and valid_username and valid_github and valid_token and password:
        if st.button("Create Account →"):
            existing_user = login_db["users"].find_one({"username": username})
            existing_repo = login_db["users"].find_one({"github_link": github_link})
            if existing_user and existing_repo:
                st.error("Username and GitHub link already registered.")
            elif existing_user:
                st.error("Username already exists.")
            elif existing_repo:
                st.error("GitHub link already registered.")
            else:
                login_db["users"].insert_one({
                    "name": name,
                    "username": username,
                    "github_link": github_link,
                    "password": password,
                    "github_token": github_token,
                    "role": "student",
                })
                st.success("Account created! You can now sign in.")
    else:
        st.info("Complete all fields and verify your repository to enable registration.")

    st.markdown("</div>", unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  Logout
# ─────────────────────────────────────────────
def logout():
    st.session_state.logged_in = False
    st.session_state.role = None
    st.session_state.username = None
    st.session_state.current_page = "Home"
    st.rerun()


# ─────────────────────────────────────────────
#  Sidebar
# ─────────────────────────────────────────────
def toolbar():
    with st.sidebar:
        st.markdown(
            "<div class='sidebar-brand'>Git<span>Track</span></div>",
            unsafe_allow_html=True,
        )

        if st.session_state.logged_in:
            if st.session_state.role == "admin":
                options = ["Home", "Manage Questions", "Student Codes", "Admin Dashboard"]
                st.markdown(
                    "<div style='font-size:0.7rem;font-weight:600;letter-spacing:0.1em;"
                    "text-transform:uppercase;color:#6b7280;padding:0 1rem 0.5rem;'>Admin</div>",
                    unsafe_allow_html=True,
                )
                selected = st.radio("", options, key="admin_sidebar", label_visibility="collapsed")
            else:
                options = ["Home", "My Assignments", "Student Dashboard", "My Data"]
                st.markdown(
                    "<div style='font-size:0.7rem;font-weight:600;letter-spacing:0.1em;"
                    "text-transform:uppercase;color:#6b7280;padding:0 1rem 0.5rem;'>Student</div>",
                    unsafe_allow_html=True,
                )
                selected = st.radio("", options, key="student_sidebar", label_visibility="collapsed")
        else:
            options = ["Home", "Login", "Register"]
            st.markdown(
                "<div style='font-size:0.7rem;font-weight:600;letter-spacing:0.1em;"
                "text-transform:uppercase;color:#6b7280;padding:0 1rem 0.5rem;'>Menu</div>",
                unsafe_allow_html=True,
            )
            selected = st.radio("", options, key="public_sidebar", label_visibility="collapsed")

        st.session_state.current_page = selected


# ─────────────────────────────────────────────
#  Header bar
# ─────────────────────────────────────────────
def header():
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.username = ""

    if st.session_state.logged_in:
        col_left, col_right = st.columns([5, 1])
        with col_left:
            st.markdown(
                f"<div style='padding-top:0.3rem;'>"
                f"<span class='badge badge-green'>● Online</span>"
                f"&nbsp;&nbsp;<span style='color:#6b7280;font-size:0.85rem;'>"
                f"Signed in as <strong style='color:#e8eaf0;'>{st.session_state.username}</strong>"
                f"</span></div>",
                unsafe_allow_html=True,
            )
        with col_right:
            if st.button("Sign Out"):
                logout()

        st.markdown(
            "<hr style='margin:0.6rem 0 1.5rem;border-color:#1e2128;'>",
            unsafe_allow_html=True,
        )


# ─────────────────────────────────────────────
#  Homepage
# ─────────────────────────────────────────────
def homepage():
    if not st.session_state.get("logged_in", False):
        # Hero
        st.markdown("""
        <div style='padding: 3rem 0 2rem;'>
            <div class='badge badge-blue' style='margin-bottom:1rem;'>
                GitHub Commit Intelligence
            </div>
            <h1 style='font-size:3rem !important; line-height:1.1; margin-bottom:1rem;'>
                Track every line.<br>
                <span style='color:#4f8ef7;'>Understand every commit.</span>
            </h1>
            <p style='color:#6b7280; font-size:1.05rem; max-width:560px; line-height:1.7;'>
                GitTrack connects to your GitHub repository and gives instructors
                a live view of student progress — commit by commit, file by file.
            </p>
        </div>
        """, unsafe_allow_html=True)

        # Feature cards
        st.markdown("""
        <div class='feature-grid'>
            <div class='feature-card'>
                <div class='feature-icon'>⚡</div>
                <div class='feature-title'>Real-time Sync</div>
                <div class='feature-desc'>Commits are fetched on login and stored instantly in MongoDB.</div>
            </div>
            <div class='feature-card'>
                <div class='feature-icon'>🔍</div>
                <div class='feature-title'>File-level Analysis</div>
                <div class='feature-desc'>See exactly which .java files were added, modified, renamed or deleted.</div>
            </div>
            <div class='feature-card'>
                <div class='feature-icon'>🎓</div>
                <div class='feature-title'>Student Dashboards</div>
                <div class='feature-desc'>Each student gets a personal view of their commit history and assignments.</div>
            </div>
            <div class='feature-card'>
                <div class='feature-icon'>🛡️</div>
                <div class='feature-title'>Role-based Access</div>
                <div class='feature-desc'>Admins manage questions and review all student code submissions.</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # How it works
        st.markdown(
            "<h2 style='margin-bottom:1.2rem;'>How it works</h2>",
            unsafe_allow_html=True,
        )
        steps = [
            ("Register", "Provide your name, student ID, GitHub repo URL, and personal access token."),
            ("Authenticate", "Log in — credentials are checked against the secure MongoDB user store."),
            ("Sync Commits", "The GitHub API is queried for every commit in your repository."),
            ("Store Data", "Structured commit data is saved per-student in MongoDB Cloud."),
            ("Visualise", "Explore your history on the dashboard: dates, messages, and file diffs."),
            ("Admin Review", "Instructors monitor all students, manage questions, and track progress."),
        ]
        for i, (title, desc) in enumerate(steps, 1):
            st.markdown(f"""
            <div class='step-row'>
                <div class='step-num'>{i}</div>
                <div>
                    <div class='step-content-title'>{title}</div>
                    <div class='step-content-desc'>{desc}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Tech stack
        st.markdown(
            "<h2 style='margin-bottom:1rem;'>Technology stack</h2>",
            unsafe_allow_html=True,
        )
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("""
            <div class='card-sm'>
                <div class='badge badge-blue' style='margin-bottom:0.5rem;'>Frontend</div>
                <div style='font-size:0.88rem;color:#9ca3af;line-height:1.7;'>
                    Streamlit · Python
                </div>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown("""
            <div class='card-sm'>
                <div class='badge badge-purple' style='margin-bottom:0.5rem;'>Backend</div>
                <div style='font-size:0.88rem;color:#9ca3af;line-height:1.7;'>
                    GitHub REST API · PyGithub
                </div>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            st.markdown("""
            <div class='card-sm'>
                <div class='badge badge-green' style='margin-bottom:0.5rem;'>Database</div>
                <div style='font-size:0.88rem;color:#9ca3af;line-height:1.7;'>
                    MongoDB Atlas Cloud
                </div>
            </div>
            """, unsafe_allow_html=True)

    else:
        # Logged-in landing
        role_badge = "badge-purple" if st.session_state.role == "admin" else "badge-blue"
        st.markdown(f"""
        <div class='card' style='margin-top:1rem;'>
            <div style='display:flex;align-items:center;gap:12px;margin-bottom:0.5rem;'>
                <span style='font-size:2rem;'>👋</span>
                <div>
                    <div style='font-family:Syne,sans-serif;font-weight:700;font-size:1.3rem;'>
                        Hello, {st.session_state.username}
                    </div>
                    <span class='badge {role_badge}'>
                        {st.session_state.role.capitalize()}
                    </span>
                </div>
            </div>
            <p style='color:#6b7280;font-size:0.9rem;margin:0;'>
                Use the sidebar to navigate to your dashboard.
            </p>
        </div>
        """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  Main
# ─────────────────────────────────────────────
def main():
    st.set_page_config(
        page_title="GitTrack Portal",
        page_icon="⚡",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    inject_css()

    db = connect_to_mongo()

    header()
    toolbar()

    page = st.session_state.get("current_page", "Home")

    if page == "Home":
        homepage()
    elif page == "Login":
        login()
    elif page == "Register":
        register_user()
    elif st.session_state.get("logged_in"):
        if st.session_state.role == "admin":
            if page == "Manage Questions":
                manage_questions(db)
            elif page == "Student Codes":
                manage_students(db)
            elif page == "Admin Dashboard":
                admin_dashboard(db)
        else:
            if page == "My Assignments":
                student_assignments(db, st.session_state.username)
            elif page == "Student Dashboard":
                student_dashboard(db)
            elif page == "My Data":
                student_data(db, st.session_state.username)
    else:
        st.error("Page not found or access restricted.")


if __name__ == "__main__":
    main()