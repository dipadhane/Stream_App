import streamlit as st


# ─────────────────────────────────────────────────────────────
#  Shared UI helpers  (same design language as stream.py)
# ─────────────────────────────────────────────────────────────

def _metric_card(label, value, icon=""):
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


def _page_header(icon, title, subtitle):
    st.markdown(f"""
    <div style="padding-bottom:1.5rem;border-bottom:1px solid #1e2128;margin-bottom:2rem;">
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:4px;">
            <span style="font-size:1.4rem;">{icon}</span>
            <span style="font-family:'Syne',sans-serif;font-size:1.6rem;
                         font-weight:800;color:#e8eaf0;">{title}</span>
        </div>
        <div style="color:#6b7280;font-size:0.88rem;">{subtitle}</div>
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
#  Student Dashboard
# ─────────────────────────────────────────────────────────────

def student_dashboard(db):
    _page_header(
        "📊",
        "Student Dashboard",
        "Your assignments and progress at a glance.",
    )

    try:
        questions_collection = db.questions
        questions = list(questions_collection.find())

        total = len(questions)
        _metric_card("Total Assignments", total, "📋")

        if questions:
            _section_title("All Assignments", "Questions assigned to your cohort")

            # Table header
            st.markdown("""
            <div style="display:grid;grid-template-columns:0.5fr 3fr 2fr;
                        background:#1e2128;border-radius:10px 10px 0 0;
                        padding:0.6rem 1rem;margin-bottom:1px;">
                <div style="font-size:0.7rem;font-weight:600;letter-spacing:0.1em;
                            text-transform:uppercase;color:#6b7280;">#</div>
                <div style="font-size:0.7rem;font-weight:600;letter-spacing:0.1em;
                            text-transform:uppercase;color:#6b7280;">Question</div>
                <div style="font-size:0.7rem;font-weight:600;letter-spacing:0.1em;
                            text-transform:uppercase;color:#6b7280;">Class Name</div>
            </div>
            """, unsafe_allow_html=True)

            rows_html = ""
            for i, q in enumerate(questions, 1):
                bg = "#111318" if i % 2 != 0 else "#0f1115"
                border_r = "0 0 10px 10px" if i == len(questions) else "0"
                rows_html += f"""
                <div style="display:grid;grid-template-columns:0.5fr 3fr 2fr;
                            background:{bg};border-radius:{border_r};
                            border:1px solid #1e2128;border-top:none;
                            padding:0.75rem 1rem;align-items:center;">
                    <div style="color:#6b7280;font-size:0.8rem;">{i}</div>
                    <div style="color:#e8eaf0;font-size:0.88rem;">
                        {q.get('question_name','—')}
                    </div>
                    <div style="color:#4f8ef7;font-family:monospace;font-size:0.8rem;">
                        {q.get('class_name','—')}
                    </div>
                </div>
                """
            st.markdown(rows_html, unsafe_allow_html=True)

        else:
            st.markdown("""
            <div style="background:#111318;border:1px dashed #1e2128;border-radius:10px;
                        padding:2.5rem;text-align:center;color:#6b7280;font-size:0.9rem;">
                No assignments have been posted yet.
            </div>
            """, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Error fetching assignments: {e}")


# ─────────────────────────────────────────────────────────────
#  Student Assignments
# ─────────────────────────────────────────────────────────────

def student_assignments(db, username):
    _page_header(
        "✅",
        "My Assignments",
        "Track which questions you have completed and what's still pending.",
    )

    try:
        questions_collection = db.questions
        questions = list(questions_collection.find(
            {}, {"question_name": 1, "class_name": 1, "_id": 0}
        ))

        if not isinstance(questions, list):
            raise ValueError("Questions fetch returned a non-list object.")

        # Resolve student name
        login_db = db.client["LoginData"]
        name = None
        for col_name in login_db.list_collection_names():
            user = login_db[col_name].find_one({"username": username})
            if user:
                name = user["name"]
                break

        if not name:
            raise ValueError(f"User '{username}' not found.")

        # Gather submitted file keys
        java_analysis_db = db.client["JavaFileAnalysis"]
        added_java_keys = []

        if name in java_analysis_db.list_collection_names():
            docs = list(java_analysis_db[name].find({}, {"added_java_files": 1, "_id": 0}))
            for doc in docs:
                added = doc.get("added_java_files", {})
                if isinstance(added, dict):
                    added_java_keys.extend(added.keys())
        else:
            st.warning(f"No repository data found for **{name}**.")

        submitted_keys = set(k.replace(".java", "") for k in added_java_keys)

        # Counts
        completed = [
            q for q in questions
            if q.get("class_name", "").replace(".java", "") in submitted_keys
        ]
        pending = [
            q for q in questions
            if q.get("class_name", "").replace(".java", "") not in submitted_keys
        ]

        # Progress bar
        total = len(questions)
        pct = int(len(completed) / total * 100) if total else 0

        # Metric row
        col1, col2, col3 = st.columns(3)
        with col1:
            _metric_card("Total", total, "📋")
        with col2:
            _metric_card("Completed", len(completed), "✅")
        with col3:
            _metric_card("Pending", len(pending), "⏳")

        # Progress bar
        st.markdown(f"""
        <div style="margin:1.5rem 0;">
            <div style="display:flex;justify-content:space-between;
                        margin-bottom:6px;font-size:0.8rem;color:#6b7280;">
                <span>Progress</span>
                <span style="color:#4ade80;font-weight:600;">{pct}%</span>
            </div>
            <div style="background:#1e2128;border-radius:999px;height:8px;overflow:hidden;">
                <div style="
                    height:100%;width:{pct}%;
                    background:linear-gradient(90deg,#4f8ef7,#22c55e);
                    border-radius:999px;
                    transition:width 0.4s ease;
                "></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        _divider()

        # Filter
        filter_options = [
            f"All ({total})",
            f"Completed ({len(completed)})",
            f"Pending ({len(pending)})",
        ]
        filter_status = st.selectbox("Filter by status", filter_options)

        # Assignment list
        if questions:
            for q in questions:
                cls = q.get("class_name", "").replace(".java", "")
                done = cls in submitted_keys

                if "Pending" in filter_status and done:
                    continue
                if "Completed" in filter_status and not done:
                    continue

                status_icon = "✅" if done else "⏳"
                status_color = "#4ade80" if done else "#f59e0b"
                status_label = "Completed" if done else "Pending"
                status_bg = "rgba(34,197,94,0.08)" if done else "rgba(245,158,11,0.08)"
                status_border = "rgba(34,197,94,0.2)" if done else "rgba(245,158,11,0.2)"

                st.markdown(f"""
                <div style="
                    background:{status_bg};
                    border:1px solid {status_border};
                    border-radius:10px;
                    padding:0.85rem 1.2rem;
                    margin-bottom:0.5rem;
                    display:flex;
                    align-items:center;
                    justify-content:space-between;
                ">
                    <div style="display:flex;align-items:center;gap:12px;">
                        <span style="font-size:1.1rem;">{status_icon}</span>
                        <div>
                            <div style="color:#e8eaf0;font-size:0.9rem;font-weight:500;">
                                {q.get('question_name','Unnamed')}
                            </div>
                            <div style="color:#4f8ef7;font-family:monospace;font-size:0.78rem;margin-top:2px;">
                                {cls}
                            </div>
                        </div>
                    </div>
                    <span style="
                        background:rgba(0,0,0,0.2);
                        color:{status_color};
                        border-radius:999px;
                        padding:3px 12px;
                        font-size:0.72rem;
                        font-weight:600;
                        letter-spacing:0.05em;
                        text-transform:uppercase;
                    ">{status_label}</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No assignments found.")

    except ValueError as ve:
        st.error(f"Value Error: {ve}")
    except Exception as e:
        st.error(f"Error fetching assignments: {e}")


# ─────────────────────────────────────────────────────────────
#  Student Data  (My Data)
# ─────────────────────────────────────────────────────────────

def student_data(db, username):
    _page_header(
        "👤",
        "My Profile & Data",
        "View your submitted Java files and commit history.",
    )

    try:
        # Resolve user
        login_db = db.client["LoginData"]
        user = None
        for col_name in login_db.list_collection_names():
            user = login_db[col_name].find_one({"username": username})
            if user:
                break

        if not user:
            raise ValueError(f"User '{username}' not found.")

        name = user.get("name", "Unknown")

        # Profile card
        st.markdown(f"""
        <div style="background:#111318;border:1px solid #1e2128;border-radius:12px;
                    padding:1.4rem 1.8rem;margin-bottom:1.5rem;
                    display:flex;align-items:center;gap:1.4rem;">
            <div style="
                width:56px;height:56px;
                background:linear-gradient(135deg,#4f8ef7,#7c3aed);
                border-radius:50%;
                display:flex;align-items:center;justify-content:center;
                font-family:'Syne',sans-serif;font-weight:800;font-size:1.3rem;
                color:#fff;flex-shrink:0;
            ">{name[0].upper()}</div>
            <div>
                <div style="font-family:'Syne',sans-serif;font-weight:700;
                            font-size:1.15rem;color:#e8eaf0;">{name}</div>
                <div style="color:#6b7280;font-size:0.85rem;margin-top:2px;">
                    @{username} &nbsp;·&nbsp;
                    <span style="color:#4ade80;">● Student</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Fetch java analysis data
        java_analysis_db = db.client["JavaFileAnalysis"]
        student_collection = java_analysis_db[name]
        student_data_list = list(student_collection.find())

        if not student_data_list:
            st.markdown("""
            <div style="background:#111318;border:1px dashed #1e2128;border-radius:10px;
                        padding:2.5rem;text-align:center;color:#6b7280;">
                No commit data found. Push some code to sync your repository.
            </div>
            """, unsafe_allow_html=True)
            return

        # Aggregate files
        added_java_files = {}
        modified_java_files = {}
        for record in student_data_list:
            added_java_files.update(record.get("added_java_files", {}))
            modified_java_files.update(record.get("modified_java_files", {}))

        # Metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            _metric_card("Total Commits", len(student_data_list), "🔄")
        with col2:
            _metric_card("Files Added", len(added_java_files), "➕")
        with col3:
            _metric_card("Files Modified", len(modified_java_files), "✏️")

        if not added_java_files and not modified_java_files:
            st.info("No added or modified Java files found in your commits.")
            return

        _divider()

        # Tabs for added vs modified
        tab1, tab2 = st.tabs([
            f"☕ Added Files ({len(added_java_files)})",
            f"🔧 Modified Files ({len(modified_java_files)})",
        ])

        with tab1:
            if added_java_files:
                selected_added = st.selectbox(
                    "Select file",
                    sorted(added_java_files.keys()),
                    key="added_files",
                )
                st.markdown(f"""
                <div style="display:flex;align-items:center;gap:8px;margin-bottom:6px;">
                    <span style="background:#1e2128;border-radius:6px;padding:3px 12px;
                                  font-family:monospace;color:#4f8ef7;font-size:0.82rem;">
                        {selected_added}.java
                    </span>
                    <span style="background:rgba(34,197,94,0.1);color:#4ade80;
                                  border-radius:999px;padding:2px 10px;
                                  font-size:0.7rem;font-weight:600;letter-spacing:0.05em;">
                        ADDED
                    </span>
                </div>
                """, unsafe_allow_html=True)
                content = added_java_files[selected_added]
                num_lines = len(str(content).split("\n"))
                st.text_area(
                    "Source",
                    value=str(content),
                    height=max(200, min(num_lines * 20, 600)),
                    label_visibility="collapsed",
                    key="added_content",
                )
            else:
                st.info("No added files found.")

        with tab2:
            if modified_java_files:
                selected_modified = st.selectbox(
                    "Select file",
                    sorted(modified_java_files.keys()),
                    key="modified_files",
                )
                st.markdown(f"""
                <div style="display:flex;align-items:center;gap:8px;margin-bottom:6px;">
                    <span style="background:#1e2128;border-radius:6px;padding:3px 12px;
                                  font-family:monospace;color:#4f8ef7;font-size:0.82rem;">
                        {selected_modified}.java
                    </span>
                    <span style="background:rgba(245,158,11,0.1);color:#fbbf24;
                                  border-radius:999px;padding:2px 10px;
                                  font-size:0.7rem;font-weight:600;letter-spacing:0.05em;">
                        MODIFIED
                    </span>
                </div>
                """, unsafe_allow_html=True)
                content = modified_java_files[selected_modified]
                num_lines = len(str(content).split("\n"))
                st.text_area(
                    "Source",
                    value=str(content),
                    height=max(200, min(num_lines * 20, 600)),
                    label_visibility="collapsed",
                    key="modified_content",
                )
            else:
                st.info("No modified files found.")

        # Commit history timeline
        _divider()
        _section_title("Commit Timeline", "Most recent commits with file activity")

        for i, record in enumerate(reversed(student_data_list[:10])):
            added_count   = len(record.get("added_java_files", {}))
            modified_count= len(record.get("modified_java_files", {}))
            deleted_count = len(record.get("deleted_java_files", {}))
            renamed_count = len(record.get("renamed_java_files", {}))
            msg = record.get("commit_message", "—")

            st.markdown(f"""
            <div style="background:#111318;border:1px solid #1e2128;border-radius:10px;
                        padding:0.9rem 1.2rem;margin-bottom:0.5rem;">
                <div style="display:flex;align-items:center;justify-content:space-between;
                            flex-wrap:wrap;gap:8px;">
                    <div>
                        <div style="color:#e8eaf0;font-size:0.88rem;font-weight:500;">
                            {msg[:80]}{"…" if len(msg) > 80 else ""}
                        </div>
                        <div style="color:#6b7280;font-size:0.75rem;margin-top:3px;font-family:monospace;">
                            {record.get('commit_date','—')} &nbsp;{record.get('commit_time','—')}
                        </div>
                    </div>
                    <div style="display:flex;gap:6px;flex-wrap:wrap;">
                        {"<span style='background:rgba(34,197,94,0.1);color:#4ade80;border-radius:6px;padding:2px 8px;font-size:0.72rem;font-weight:600;'>+" + str(added_count) + " added</span>" if added_count else ""}
                        {"<span style='background:rgba(245,158,11,0.1);color:#fbbf24;border-radius:6px;padding:2px 8px;font-size:0.72rem;font-weight:600;'>" + str(modified_count) + " modified</span>" if modified_count else ""}
                        {"<span style='background:rgba(239,68,68,0.1);color:#f87171;border-radius:6px;padding:2px 8px;font-size:0.72rem;font-weight:600;'>" + str(deleted_count) + " deleted</span>" if deleted_count else ""}
                        {"<span style='background:rgba(124,58,237,0.1);color:#c4b5fd;border-radius:6px;padding:2px 8px;font-size:0.72rem;font-weight:600;'>" + str(renamed_count) + " renamed</span>" if renamed_count else ""}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        if len(student_data_list) > 10:
            st.markdown(
                f"<div style='text-align:center;color:#6b7280;font-size:0.82rem;margin-top:0.5rem;'>"
                f"Showing latest 10 of {len(student_data_list)} commits</div>",
                unsafe_allow_html=True,
            )

    except ValueError as ve:
        st.error(f"Value Error: {ve}")
    except Exception as e:
        st.error(f"An error occurred: {e}")