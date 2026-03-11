import streamlit as st
from bson.objectid import ObjectId
from pymongo import MongoClient


# ─────────────────────────────────────────────────────────────
#  Shared UI helpers
# ─────────────────────────────────────────────────────────────

def _metric_card(label, value, icon="", accent="#4f8ef7"):
    st.markdown(f"""
    <div style="
        background:#111318;
        border:1px solid #1e2128;
        border-radius:12px;
        padding:1.4rem 1.6rem;
        display:flex;
        align-items:center;
        gap:1rem;
    ">
        <div style="
            width:48px;height:48px;
            background:rgba(79,142,247,0.12);
            border-radius:10px;
            display:flex;align-items:center;justify-content:center;
            font-size:1.4rem;flex-shrink:0;
        ">{icon}</div>
        <div>
            <div style="color:#6b7280;font-size:0.72rem;font-weight:600;
                        letter-spacing:0.1em;text-transform:uppercase;margin-bottom:2px;">
                {label}
            </div>
            <div style="font-family:'Syne',sans-serif;font-size:2rem;
                        font-weight:800;color:#e8eaf0;line-height:1;">
                {value}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def _section_title(text, subtitle=""):
    st.markdown(f"""
    <div style="margin:2rem 0 1.2rem;">
        <div style="font-family:'Syne',sans-serif;font-size:1.3rem;
                    font-weight:700;color:#e8eaf0;">{text}</div>
        {"<div style='color:#6b7280;font-size:0.85rem;margin-top:3px;'>" + subtitle + "</div>" if subtitle else ""}
    </div>
    """, unsafe_allow_html=True)


def _divider():
    st.markdown(
        "<hr style='border:none;border-top:1px solid #1e2128;margin:1.2rem 0;'>",
        unsafe_allow_html=True,
    )


def _badge(text, color="blue"):
    colors = {
        "blue":   ("rgba(79,142,247,0.15)",  "#93c5fd"),
        "green":  ("rgba(34,197,94,0.15)",   "#4ade80"),
        "purple": ("rgba(124,58,237,0.15)",  "#c4b5fd"),
        "amber":  ("rgba(245,158,11,0.15)",  "#fbbf24"),
        "red":    ("rgba(239,68,68,0.15)",   "#f87171"),
    }
    bg, fg = colors.get(color, colors["blue"])
    return (
        f"<span style='background:{bg};color:{fg};border-radius:999px;"
        f"padding:3px 10px;font-size:0.7rem;font-weight:600;"
        f"letter-spacing:0.05em;text-transform:uppercase;'>{text}</span>"
    )


# ─────────────────────────────────────────────────────────────
#  Admin Dashboard
# ─────────────────────────────────────────────────────────────

def admin_dashboard(db):
    # Page header
    st.markdown("""
    <div style="padding-bottom:1.5rem;border-bottom:1px solid #1e2128;margin-bottom:2rem;">
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:4px;">
            <span style="font-size:1.4rem;">🛡️</span>
            <span style="font-family:'Syne',sans-serif;font-size:1.6rem;
                         font-weight:800;color:#e8eaf0;">Admin Overview</span>
        </div>
        <div style="color:#6b7280;font-size:0.88rem;">
            Monitor students, questions, and system activity at a glance.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Metrics
    total_questions = db.questions.count_documents({})

    questions = db.questions.find()
    class_question_dict = {}
    for question in questions:
        if "class_name" in question and "question_name" in question:
            class_question_dict[question["class_name"]] = question["question_name"]

    java_db = db.client["JavaFileAnalysis"]
    total_students = len(java_db.list_collection_names())

    col1, col2, col3 = st.columns(3)
    with col1:
        _metric_card("Registered Students", total_students, "🎓")
    with col2:
        _metric_card("Active Questions", total_questions, "📋")
    with col3:
        coverage = (
            f"{round(len(class_question_dict)/max(total_questions,1)*100)}%"
            if total_questions
            else "—"
        )
        _metric_card("Class Coverage", coverage, "📊")

    _divider()

    # Quick summary table
    _section_title("Question — Class Mapping", "All assigned questions and their target class names")

    if class_question_dict:
        # Table header
        st.markdown("""
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:0;
                    background:#1e2128;border-radius:10px 10px 0 0;
                    padding:0.6rem 1rem;margin-bottom:1px;">
            <div style="font-size:0.72rem;font-weight:600;letter-spacing:0.1em;
                        text-transform:uppercase;color:#6b7280;">Question</div>
            <div style="font-size:0.72rem;font-weight:600;letter-spacing:0.1em;
                        text-transform:uppercase;color:#6b7280;">Class Name</div>
        </div>
        """, unsafe_allow_html=True)

        rows_html = ""
        for i, (cls, qname) in enumerate(class_question_dict.items()):
            bg = "#111318" if i % 2 == 0 else "#0f1115"
            border_r = "0 0 10px 10px" if i == len(class_question_dict) - 1 else "0"
            rows_html += f"""
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:0;
                        background:{bg};border-radius:{border_r};
                        border:1px solid #1e2128;border-top:none;
                        padding:0.7rem 1rem;">
                <div style="color:#e8eaf0;font-size:0.88rem;">{qname}</div>
                <div style="color:#4f8ef7;font-size:0.85rem;font-family:monospace;">{cls}</div>
            </div>
            """
        st.markdown(rows_html, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="background:#111318;border:1px solid #1e2128;border-radius:10px;
                    padding:2rem;text-align:center;color:#6b7280;font-size:0.9rem;">
            No questions assigned yet. Go to <strong style="color:#4f8ef7;">Manage Questions</strong> to add some.
        </div>
        """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
#  Manage Questions
# ─────────────────────────────────────────────────────────────

def manage_questions(db):
    st.markdown("""
    <div style="padding-bottom:1.5rem;border-bottom:1px solid #1e2128;margin-bottom:2rem;">
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:4px;">
            <span style="font-size:1.4rem;">📋</span>
            <span style="font-family:'Syne',sans-serif;font-size:1.6rem;
                         font-weight:800;color:#e8eaf0;">Manage Questions</span>
        </div>
        <div style="color:#6b7280;font-size:0.88rem;">
            Assign questions to Java class names for student tracking.
        </div>
    </div>
    """, unsafe_allow_html=True)

    questions_collection = db.questions

    # ── Add question card ──
    st.markdown("""
    <div style="background:#111318;border:1px solid #1e2128;border-radius:12px;
                padding:1.6rem 1.8rem;margin-bottom:2rem;">
        <div style="font-family:'Syne',sans-serif;font-weight:700;font-size:1rem;
                    color:#e8eaf0;margin-bottom:1.2rem;">
            ＋ Assign New Question
        </div>
    """, unsafe_allow_html=True)

    with st.form(key="send_question_form"):
        col_a, col_b = st.columns(2)
        with col_a:
            question_name = st.text_input("Question Name", placeholder="e.g. Implement Binary Search")
        with col_b:
            class_name = st.text_input("Class Name", placeholder="e.g. BinarySearch")

        submitted = st.form_submit_button("Assign Question →")

        if submitted:
            if question_name and class_name:
                existing = questions_collection.find_one({"class_name": class_name})
                if existing:
                    st.warning(f"Class **{class_name}** already has a question assigned.")
                else:
                    try:
                        questions_collection.insert_one(
                            {"question_name": question_name, "class_name": class_name}
                        )
                        st.success("Question assigned successfully!")
                        st.session_state["new_question_name"] = ""
                        st.session_state["new_class_name"] = ""
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")
            else:
                st.warning("Both fields are required.")

    st.markdown("</div>", unsafe_allow_html=True)

    # ── Question list ──
    _section_title("Assigned Questions", "Click ✏️ to edit or 🗑️ to remove a question")

    questions = list(questions_collection.find())

    if questions:
        for question in questions:
            qid = question["_id"]
            is_editing = st.session_state.get(f"editing_{qid}", False)

            # Card container
            st.markdown(f"""
            <div style="background:#111318;border:1px solid #1e2128;border-radius:10px;
                        padding:1rem 1.2rem;margin-bottom:0.6rem;">
            """, unsafe_allow_html=True)

            if not is_editing:
                col1, col2, col3 = st.columns([7, 1, 1])
                with col1:
                    st.markdown(
                        f"<div style='color:#e8eaf0;font-weight:500;font-size:0.92rem;'>"
                        f"{question['question_name']}</div>"
                        f"<div style='color:#4f8ef7;font-family:monospace;font-size:0.8rem;"
                        f"margin-top:3px;'>{question['class_name']}</div>",
                        unsafe_allow_html=True,
                    )
                with col2:
                    if st.button("✏️", key=f"edit_button_{qid}", help="Edit"):
                        st.session_state[f"editing_{qid}"] = True
                        st.rerun()
                with col3:
                    if st.button("🗑️", key=f"delete_button_{qid}", help="Delete"):
                        try:
                            result = questions_collection.delete_one({"_id": ObjectId(qid)})
                            if result.deleted_count > 0:
                                st.success("Question deleted.")
                                st.rerun()
                            else:
                                st.warning("Could not find question to delete.")
                        except Exception as e:
                            st.error(f"Error: {e}")
            else:
                edit_question(db, question)

            st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="background:#111318;border:1px dashed #1e2128;border-radius:10px;
                    padding:2.5rem;text-align:center;color:#6b7280;font-size:0.9rem;">
            No questions yet. Use the form above to assign your first one.
        </div>
        """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
#  Edit question (inline)
# ─────────────────────────────────────────────────────────────

def edit_question(db, question):
    questions_collection = db.questions
    qid = question["_id"]

    st.markdown(
        f"<div style='color:#f59e0b;font-size:0.8rem;font-weight:600;"
        f"letter-spacing:0.05em;text-transform:uppercase;margin-bottom:0.8rem;'>"
        f"✏️ Editing Question</div>",
        unsafe_allow_html=True,
    )

    with st.form(key=f"edit_question_form_{qid}"):
        col_a, col_b = st.columns(2)
        with col_a:
            new_question_name = st.text_input(
                "Question Name",
                value=question.get("question_name", ""),
                key=f"edit_name_{qid}",
            )
        with col_b:
            new_class_name = st.text_input(
                "Class Name",
                value=question.get("class_name", ""),
                key=f"edit_class_{qid}",
            )

        col_save, col_cancel = st.columns([1, 5])
        with col_save:
            save = st.form_submit_button("Save →")
        with col_cancel:
            cancel = st.form_submit_button("Cancel")

        if save:
            if new_question_name and new_class_name:
                try:
                    result = questions_collection.update_one(
                        {"_id": ObjectId(qid)},
                        {"$set": {
                            "question_name": new_question_name,
                            "class_name": new_class_name,
                        }},
                    )
                    if result.modified_count > 0:
                        st.success("Updated successfully!")
                        st.session_state[f"editing_{qid}"] = False
                        st.rerun()
                    else:
                        st.warning("No changes detected.")
                except Exception as e:
                    st.error(f"Error: {e}")
            else:
                st.warning("Both fields are required.")

        if cancel:
            st.session_state[f"editing_{qid}"] = False
            st.rerun()


# ─────────────────────────────────────────────────────────────
#  Manage Students  (Student Codes)
# ─────────────────────────────────────────────────────────────

def manage_students(db):
    st.markdown("""
    <div style="padding-bottom:1.5rem;border-bottom:1px solid #1e2128;margin-bottom:2rem;">
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:4px;">
            <span style="font-size:1.4rem;">🎓</span>
            <span style="font-family:'Syne',sans-serif;font-size:1.6rem;
                         font-weight:800;color:#e8eaf0;">Student Codes</span>
        </div>
        <div style="color:#6b7280;font-size:0.88rem;">
            Browse submitted Java files for each student.
        </div>
    </div>
    """, unsafe_allow_html=True)

    java_db = db.client["JavaFileAnalysis"]
    collections = java_db.list_collection_names()

    # Summary bar
    st.markdown(f"""
    <div style="display:flex;gap:1rem;margin-bottom:1.5rem;flex-wrap:wrap;">
        <div style="background:#111318;border:1px solid #1e2128;border-radius:8px;
                    padding:0.6rem 1.2rem;font-size:0.85rem;color:#9ca3af;">
            <span style="color:#4f8ef7;font-weight:700;font-family:'Syne',sans-serif;">
                {len(collections)}
            </span>&nbsp; students registered
        </div>
    </div>
    """, unsafe_allow_html=True)

    if not collections:
        st.markdown("""
        <div style="background:#111318;border:1px dashed #1e2128;border-radius:10px;
                    padding:3rem;text-align:center;color:#6b7280;">
            No student collections found in JavaFileAnalysis.
        </div>
        """, unsafe_allow_html=True)
        return

    selected_collection = st.selectbox(
        "Select Student",
        collections,
        help="Each entry corresponds to one student's commit collection.",
    )

    if not selected_collection:
        return

    documents = list(java_db[selected_collection].find())

    # Stats row
    java_files_keys = set()
    for doc in documents:
        added = doc.get("added_java_files", {})
        if isinstance(added, dict):
            java_files_keys.update(added.keys())

    col1, col2 = st.columns(2)
    with col1:
        _metric_card("Total Commits", len(documents), "🔄")
    with col2:
        _metric_card("Java Files Submitted", len(java_files_keys), "☕")

    if not documents:
        st.info("No commits found for this student.")
        return

    if not java_files_keys:
        st.markdown("""
        <div style="background:#111318;border:1px solid #1e2128;border-radius:10px;
                    padding:1.5rem;color:#6b7280;margin-top:1rem;">
            No <code style="color:#4f8ef7;">.java</code> files found in added_java_files.
        </div>
        """, unsafe_allow_html=True)
        return

    _divider()
    _section_title("View File Content", "Select a Java file to inspect its source code")

    selected_key = st.selectbox(
        "Java File",
        sorted(java_files_keys),
        help="Files sourced from added_java_files across all commits",
    )

    if selected_key:
        values = []
        for doc in documents:
            added = doc.get("added_java_files", {})
            if isinstance(added, dict) and selected_key in added:
                values.append({
                    "date": doc.get("commit_date", "—"),
                    "time": doc.get("commit_time", "—"),
                    "message": doc.get("commit_message", "—"),
                    "content": added[selected_key],
                })

        for i, v in enumerate(values):
            st.markdown(f"""
            <div style="display:flex;align-items:center;gap:10px;margin:0.8rem 0 0.3rem;">
                <span style="background:#1e2128;border-radius:6px;padding:2px 10px;
                              font-family:monospace;font-size:0.78rem;color:#6b7280;">
                    {v['date']} {v['time']}
                </span>
                <span style="color:#9ca3af;font-size:0.83rem;font-style:italic;">
                    {v['message'][:72]}{"…" if len(v['message'])>72 else ""}
                </span>
            </div>
            """, unsafe_allow_html=True)

            num_lines = len(str(v["content"]).split("\n"))
            height = max(120, min(num_lines * 20, 500))
            st.text_area(
                f"Version {i+1}",
                value=str(v["content"]),
                height=height,
                key=f"code_{selected_key}_{i}",
                label_visibility="collapsed",
            )