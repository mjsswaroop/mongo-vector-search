from pymongo import MongoClient
from openai import OpenAI
from dotenv import load_dotenv
import certifi
import os

# Load environment variables
load_dotenv()

# ==============================
# CONFIGURATION
# ==============================

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")
COLLECTION_NAME = os.getenv("COLLECTION_NAME")
VECTOR_INDEX_NAME = os.getenv("VECTOR_INDEX_NAME")
VECTOR_FIELD_NAME = os.getenv("VECTOR_FIELD_NAME")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL")

# ==============================
# MongoDB Connection
# ==============================

client = MongoClient(
    MONGO_URI,
    serverSelectionTimeoutMS=30000,
    tlsCAFile=certifi.where()
)

db = client[DB_NAME]
collection = db[COLLECTION_NAME]

print("✅ Connected to MongoDB Atlas")

# ==============================
# OpenAI Client
# ==============================

openai_client = OpenAI(api_key=OPENAI_API_KEY)

# ==============================
# Embedding Function
# ==============================

def get_embedding(text: str):
    response = openai_client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=text
    )
    return response.data[0].embedding

# ==============================
# Vector Search Function
# ==============================

def search_tours(query: str, limit: int = 3):
    query_vector = get_embedding(query)

    pipeline = [
        {
            "$vectorSearch": {
                "index": VECTOR_INDEX_NAME,
                "path": VECTOR_FIELD_NAME,
                "queryVector": query_vector,
                "numCandidates": 50,
                "limit": limit
            }
        },
        {
            "$project": {
                "_id": 0,
                "tourName": 1,
                "destinations": 1,
                "description": 1,
                "score": {"$meta": "vectorSearchScore"}
            }
        }
    ]

    return list(collection.aggregate(pipeline))


# ==============================
# MAIN
# ==============================

if __name__ == "__main__":
    query = "safari tour in africa"
    print(f"\n🔍 Query: {query}")

    results = search_tours(query)

    print(f"\n✅ Results Found: {len(results)}")

    for i, r in enumerate(results, 1):
        print("\n------------------------------")
        print(f"Result #{i}")
        print("Tour Name:", r.get("tourName"))
        print("Destinations:", r.get("destinations"))
        print("Score:", round(r.get("score", 0), 4))
