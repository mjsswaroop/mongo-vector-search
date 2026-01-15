# # from pymongo import MongoClient
# # from openai import OpenAI
# # from dotenv import load_dotenv
# # import certifi
# # import os

# # # Load environment variables
# # load_dotenv()

# # # ==============================
# # # CONFIGURATION
# # # ==============================

# # OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# # MONGO_URI = os.getenv("MONGO_URI")
# # DB_NAME = os.getenv("DB_NAME")
# # COLLECTION_NAME = os.getenv("COLLECTION_NAME")
# # VECTOR_INDEX_NAME = os.getenv("VECTOR_INDEX_NAME")
# # VECTOR_FIELD_NAME = os.getenv("VECTOR_FIELD_NAME")
# # EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL")

# # # ==============================
# # # MongoDB Connection
# # # ==============================

# # client = MongoClient(
# #     MONGO_URI,
# #     serverSelectionTimeoutMS=30000,
# #     tlsCAFile=certifi.where()
# # )

# # db = client[DB_NAME]
# # collection = db[COLLECTION_NAME]

# # print("✅ Connected to MongoDB Atlas")

# # # ==============================
# # # OpenAI Client
# # # ==============================

# # openai_client = OpenAI(api_key=OPENAI_API_KEY)

# # # ==============================
# # # Embedding Function
# # # ==============================

# # def get_embedding(text: str):
# #     response = openai_client.embeddings.create(
# #         model=EMBEDDING_MODEL,
# #         input=text
# #     )
# #     return response.data[0].embedding

# # # ==============================
# # # Vector Search Function
# # # ==============================

# # def search_tours(query: str, limit: int = 3):
# #     query_vector = get_embedding(query)

# #     pipeline = [
# #         {
# #             "$vectorSearch": {
# #                 "index": VECTOR_INDEX_NAME,
# #                 "path": VECTOR_FIELD_NAME,
# #                 "queryVector": query_vector,
# #                 "numCandidates": 50,
# #                 "limit": limit
# #             }
# #         },
# #         {
# #             "$project": {
# #                 "_id": 0,
# #                 "tourName": 1,
# #                 "destinations": 1,
# #                 "description": 1,
# #                 "score": {"$meta": "vectorSearchScore"}
# #             }
# #         }
# #     ]

# #     return list(collection.aggregate(pipeline))


# # # ==============================
# # # MAIN
# # # ==============================

# # if __name__ == "__main__":
# #     query = "safari tour in africa"
# #     print(f"\n🔍 Query: {query}")

# #     results = search_tours(query)

# #     print(f"\n✅ Results Found: {len(results)}")

# #     for i, r in enumerate(results, 1):
# #         print("\n------------------------------")
# #         print(f"Result #{i}")
# #         print("Tour Name:", r.get("tourName"))
# #         print("Destinations:", r.get("destinations"))
# #         print("Score:", round(r.get("score", 0), 4))
# from fastapi import FastAPI, Query
# from pymongo import MongoClient
# from openai import OpenAI
# from dotenv import load_dotenv
# import certifi
# import os

# load_dotenv()

# app = FastAPI(title="MongoDB Vector Search API")

# # ==============================
# # CONFIG
# # ==============================

# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# MONGO_URI = os.getenv("MONGO_URI")
# DB_NAME = os.getenv("DB_NAME")
# COLLECTION_NAME = os.getenv("COLLECTION_NAME")
# VECTOR_INDEX_NAME = os.getenv("VECTOR_INDEX_NAME")
# VECTOR_FIELD_NAME = os.getenv("VECTOR_FIELD_NAME")
# EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL")

# # ==============================
# # CLIENTS
# # ==============================

# mongo_client = MongoClient(
#     MONGO_URI,
#     tlsCAFile=certifi.where()
# )

# db = mongo_client[DB_NAME]
# collection = db[COLLECTION_NAME]

# openai_client = OpenAI(api_key=OPENAI_API_KEY)

# # ==============================
# # HELPERS
# # ==============================

# def get_embedding(text: str):
#     response = openai_client.embeddings.create(
#         model=EMBEDDING_MODEL,
#         input=text
#     )
#     return response.data[0].embedding

# # ==============================
# # ROUTES
# # ==============================

# @app.get("/")
# def health():
#     return {"status": "ok"}

# @app.get("/search")
# def search(query: str = Query(..., min_length=3)):
#     vector = get_embedding(query)

#     pipeline = [
#         {
#             "$vectorSearch": {
#                 "index": VECTOR_INDEX_NAME,
#                 "path": VECTOR_FIELD_NAME,
#                 "queryVector": vector,
#                 "numCandidates": 50,
#                 "limit": 3
#             }
#         },
#         {
#             "$project": {
#                 "_id": 0,
#                 "tourName": 1,
#                 "destinations": 1,
#                 "description": 1,
#                 "score": {"$meta": "vectorSearchScore"}
#             }
#         }
#     ]

#     results = list(collection.aggregate(pipeline))
#     return {"query": query, "results": results}
from fastapi import FastAPI, Query
from pydantic import BaseModel
from pymongo import MongoClient
from openai import OpenAI
from dotenv import load_dotenv
import certifi
import os

# ==============================
# Load environment variables
# ==============================

load_dotenv()

# ==============================
# App init
# ==============================

app = FastAPI(title="Travel Vector Search API")

# ==============================
# CONFIG
# ==============================

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")
COLLECTION_NAME = os.getenv("COLLECTION_NAME")
VECTOR_INDEX_NAME = os.getenv("VECTOR_INDEX_NAME")
VECTOR_FIELD_NAME = os.getenv("VECTOR_FIELD_NAME")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL")

# ==============================
# MongoDB Client
# ==============================

mongo_client = MongoClient(
    MONGO_URI,
    serverSelectionTimeoutMS=30000,
    tlsCAFile=certifi.where()
)

db = mongo_client[DB_NAME]
collection = db[COLLECTION_NAME]

# ==============================
# OpenAI Client
# ==============================

openai_client = OpenAI(api_key=OPENAI_API_KEY)

# ==============================
# Helpers
# ==============================

def get_embedding(text: str):
    response = openai_client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=text
    )
    return response.data[0].embedding


def vector_search(query: str, limit: int = 3):
    vector = get_embedding(query)

    pipeline = [
        {
            "$vectorSearch": {
                "index": VECTOR_INDEX_NAME,
                "path": VECTOR_FIELD_NAME,
                "queryVector": vector,
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
# Request Models
# ==============================

class SearchRequest(BaseModel):
    query: str

# ==============================
# Routes
# ==============================

@app.get("/")
def health():
    return {"status": "ok"}

# --- GET (query in URL) ---
@app.get("/search")
def search_get(query: str = Query(..., min_length=3)):
    results = vector_search(query)
    return {
        "query": query,
        "results": results
    }

# --- POST (query in BODY) ---
@app.post("/search")
def search_post(payload: SearchRequest):
    query = payload.query
    results = vector_search(query)
    return {
        "query": query,
        "results": results
    }
