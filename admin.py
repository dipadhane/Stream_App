import streamlit as st
from bson.objectid import ObjectId
from pymongo import MongoClient



def admin_dashboard(db):
    st.subheader("Admin Overview")
    st.write("Welcome to the Admin Dashboard")
    
    total_questions = db.questions.count_documents({})

    questions = db.questions.find()

    # Create a dictionary to store class_name as the key and question_name as the value
    class_question_dict = {}

    # Iterate through each document and extract the class_name and question_name
    for question in questions:
        # Assuming 'class_name' and 'question_name' are fields in the document
        if 'class_name' in question and 'question_name' in question:
            class_question_dict[question['class_name']] = question['question_name']

# Display the dictionary
    # st.write("Class and Question Name Mapping: ", class_question_dict)

    username = "abhishelke297127"
    password = "Abhi%402971"
    connection_string = f"mongodb+srv://{username}:{password}@cluster0.uu8yq.mongodb.net/?retryWrites=true&w=majority"
    
    # Connect to MongoDB
    client = MongoClient(connection_string)
    db = client["JavaFileAnalysis"]  # Replace with your actual database name

    # You can add admin summary statistics here
    total_students = len(db.list_collection_names())
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Students", total_students)
    with col2:
        st.metric("Total Questions", total_questions)

def manage_questions(db):
    st.subheader("Manage Questions")
    st.subheader("Assign Questions with Classname")
    st.write("Manage questions for all students:")

    questions_collection = db.questions

    with st.form(key="send_question_form"):
        # Use session state to store form inputs, but don't overwrite them
        question_name = st.text_input("Question Name")
        class_name = st.text_input("Class Name")
        submit_button = st.form_submit_button("Send Question")

        if submit_button:
            if question_name and class_name:
                # Check if the combination of question_name and class_name already exists
                existing_question = questions_collection.find_one({
                    "class_name": class_name
                })

                if existing_question:
                    # Show a warning if a duplicate class_name exists
                    st.warning(f"The class '{class_name}' already has a question assigned.")
                else:
                    # Insert new question if no duplicates are found
                    new_question = {"question_name": question_name, "class_name": class_name}
                    try:
                        questions_collection.insert_one(new_question)
                        st.success("Question sent successfully!")
                        # Reset session state after successful submission
                        st.session_state['new_question_name'] = ""  # Clear the question name field
                        st.session_state['new_class_name'] = ""  # Clear the class name field
                        st.rerun()  # Refresh the page to show updated data
                    except Exception as e:
                        st.error(f"Error while sending the question: {e}")
            else:
                st.warning("Please fill in both fields to send the question.")

    # List existing questions in a table format
    st.write("### Sent Questions:")
    questions = list(questions_collection.find())

    if questions:
        for question in questions:
            col1, col2, col3 = st.columns([7, 1, 2])  # Adjust column widths
            with col1:
                st.markdown(
                    f"**{question['question_name']}** <br> *Class Name: {question['class_name']}*",
                    unsafe_allow_html=True
                )
            with col2:
                if st.button("✏️", key=f"edit_button_{question['_id']}"):  # Edit Icon
                    st.session_state[f"editing_{question['_id']}"] = True
            with col3:
                if st.button("🗑️", key=f"delete_button_{question['_id']}"):  # Delete Icon
                    try:
                        result = questions_collection.delete_one({"_id": ObjectId(question["_id"])})
                        if result.deleted_count > 0:
                            st.success("Question deleted successfully!")
                            st.rerun()
                        else:
                            st.warning("No question found to delete.")
                    except Exception as e:
                        st.error(f"Error while deleting the question: {e}")

            # Show edit form if in edit mode
            if st.session_state.get(f"editing_{question['_id']}", False):
                edit_question(db, question)
    else:
        st.info("No questions available.")

# Edit question function
def edit_question(db, question):
    questions_collection = db.questions

    # Display the current question data in an editable form
    with st.form(key=f"edit_question_form_{question['_id']}"):
        # Pre-fill form fields with current data
        new_question_name = st.text_input(
            "Edit Question Name",
            value=question.get("question_name", ""),
            key=f"edit_name_{question['_id']}"
        )
        new_class_name = st.text_input(
            "Edit Class Name",
            value=question.get("class_name", ""),
            key=f"edit_class_{question['_id']}"
        )

        # Submit button for saving changes
        save_button = st.form_submit_button("Save Changes")

        if save_button:
            if new_question_name and new_class_name:
                try:
                    # Update question in MongoDB
                    result = questions_collection.update_one(
                        {"_id": ObjectId(question["_id"])},
                        {"$set": {"question_name": new_question_name, "class_name": new_class_name}}
                    )

                    if result.modified_count > 0:
                        st.success("Question updated successfully!")
                        st.session_state[f"editing_{question['_id']}"] = False  # Reset edit state
                        st.rerun()  # Refresh to show changes
                    else:
                        st.warning("No changes were made.")
                except Exception as e:
                    pass
            else:
                st.warning("Both fields are required to update the question.")

        # Cancel button to exit edit mode
        if st.form_submit_button("Cancel"):
            st.session_state[f"editing_{question['_id']}"] = False

    # Existing question management code remains the same as in the previous admin_dashboard
    # (Keep the existing form for adding, editing, and deleting questions)
def manage_students(db):
    st.subheader("Manage Students")
    
    # MongoDB credentials
    username = "abhishelke297127"
    password = "Abhi%402971"
    connection_string = f"mongodb+srv://{username}:{password}@cluster0.uu8yq.mongodb.net/?retryWrites=true&w=majority"
    
    # Connect to MongoDB
    client = MongoClient(connection_string)
    db = client["JavaFileAnalysis"]  # Replace with your actual database name

    # Assuming db is already connected to the MongoDB database
    collections = db.list_collection_names()
    st.write(f"Total Students: {len(collections)}")

    if collections:
        selected_collection = st.selectbox("Select a collection", collections)
        st.write(f"You selected: {selected_collection}")

        # Fetch all documents from the selected collection
        documents = list(db[selected_collection].find())  # Assuming you're using MongoDB

        # Show number of documents
        st.write(f"Total Commit: {len(documents)}")

        if documents:
            # Traverse all documents to collect unique keys from the 'added_java_files' field
            java_files_keys = set()
            
            for doc in documents:
                if 'added_java_files' in doc:
                    # Ensure 'added_java_files' is a dictionary before accessing its keys
                    if isinstance(doc['added_java_files'], dict):
                        java_files_keys.update(doc['added_java_files'].keys())  # Collect unique keys
                    else:
                        st.write(f"Warning: 'added_java_files' in document {doc['_id']} is not a dictionary")
                else:
                    st.write(f"Warning: 'added_java_files' field is missing in document {doc['_id']}")

            # Convert the set of keys to a list
            java_files_keys = list(java_files_keys)
            st.write(f"Total .java Files are : {len(java_files_keys)}")
            if java_files_keys:
                selected_key = st.selectbox("Select a key from 'added_java_files'", java_files_keys)

                # Once a key is selected, traverse all documents again to display the values for that key
                if selected_key:
                    values = []
                    for doc in documents:
                        if 'added_java_files' in doc and isinstance(doc['added_java_files'], dict):
                            if selected_key in doc['added_java_files']:
                                values.append(doc['added_java_files'][selected_key])
                    
                    # Display values for the selected key
                    st.write(f"Values for the key '{selected_key}':")
                    
                    for value in values:
                        # Calculate the number of lines in the value (to adjust height)
                        num_lines = len(str(value).split('\n'))
                        # Estimate height based on the number of lines (adjust as needed)
                        height = max(100, num_lines * 20)  # Minimum height of 100, 20 pixels per line
                        st.text_area("Value", value=str(value), height=height)

            else:
                st.write("No 'added_java_files' field found in any documents or no keys in 'added_java_files'.")
        else:
            st.write("No documents found in the selected collection.")
    else:
        st.write("No collections found in this database.")



