from pymongo import MongoClient

# Replace with your MongoDB Atlas connection string
username = "abhishelke297127"
password = "Abhi%402971"
connection_string = f"mongodb+srv://{username}:{password}@cluster0.uu8yq.mongodb.net/?retryWrites=true&w=majority"


# Initialize MongoDB client
client = MongoClient(connection_string)

# Create databases and collections
databases_and_collections = {
    "JavaFileAnalysis": [],
    "loginData": ["users"],
    "Question": ["questions"]
}

for db_name, collections in databases_and_collections.items():
    db = client[db_name]
    for collection_name in collections:
        # Creating collection
        db.create_collection(collection_name)
        print(f"Created collection '{collection_name}' in database '{db_name}'.")

print("All databases and collections have been created successfully.")
