import os
import uuid
import openai
import json
from fastapi import FastAPI, File, UploadFile, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env if you want

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

MONGO_URI = os.getenv("MONGO_URI", "mongodb://db:27017")

client = MongoClient(MONGO_URI)
db = client["notes_db"]
collection = db["notes_collection"]

app = FastAPI()

origins = [
    "http://localhost:3000",  # React dev server or containerized
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Note(BaseModel):
    id: str
    client: str
    target_demographic: str
    platforms: List[str]
    notes: str


@app.get("/")
def root():
    return {"message": "Welcome to the Enhanced LLM-ETL API"}


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    1. Receive a text file.
    2. Send it to the LLM for parsing into multiple structured objects if needed.
    3. Each parsed object is inserted separately into MongoDB.
    4. Return an array of inserted objects with _id (converted to string).
    """
    try:
        raw_content = (await file.read()).decode("utf-8", errors="ignore")
        
        prompt = f"""
        You will receive raw text notes about one or more ad/media targeting plans.
        They may contain multiple distinct sets of information for different clients.

        Task:
        1. Identify each 'group' of data if multiple groups/clients/campaigns appear.
        2. For each group, extract these fields:
           - client
           - target_demographic
           - platforms
           - notes (a summary of what's important or leftover details)

        3. If a field cannot be identified, use "NOT FOUND" for that field.
        4. Return an array of JSON objects. Example:
           [
             {
               "client": "...",
               "target_demographic": "...",
               "platforms": ["...", "..."],
               "notes": "..."
             },
             {
               ...
             }
           ]

        Here is the raw text:
        {raw_content}
        """

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful data parser."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.0
        )

        parsed_text = response.choices[0].message["content"].strip()

        # Expecting an array of objects. Try to parse it. 
        # If it fails or isn't valid JSON, we fall back to a single default doc.
        try:
            parsed_array = json.loads(parsed_text)
            if not isinstance(parsed_array, list):
                # Force it into a list if the LLM didn't provide an array
                parsed_array = [parsed_array]
        except json.JSONDecodeError:
            parsed_array = [{
                "client": "NOT FOUND",
                "target_demographic": "NOT FOUND",
                "platforms": [],
                "notes": raw_content
            }]

        # Insert each object as a separate document
        inserted_docs = []
        for obj in parsed_array:
            client_val = obj.get("client", "NOT FOUND") or "NOT FOUND"
            target_val = obj.get("target_demographic", "NOT FOUND") or "NOT FOUND"
            platforms_val = obj.get("platforms", [])
            if not isinstance(platforms_val, list):
                platforms_val = [str(platforms_val)]
            notes_val = obj.get("notes", "NOT FOUND") or "NOT FOUND"

            note_id = str(uuid.uuid4())
            structured_data = {
                "id": note_id,
                "client": client_val,
                "target_demographic": target_val,
                "platforms": platforms_val,
                "notes": notes_val
            }

            insert_result = collection.insert_one(structured_data)
            structured_data["_id"] = str(insert_result.inserted_id)
            inserted_docs.append(structured_data)

        return {
            "status": "success",
            "count": len(inserted_docs),
            "data": inserted_docs
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


@app.get("/notes", response_model=List[Note])
def get_notes():
    notes_cursor = collection.find({})
    notes_list = []
    for doc in notes_cursor:
        if "_id" in doc:
            doc["_id"] = str(doc["_id"])
        notes_list.append(
            Note(
                id=doc.get("id", ""),
                client=doc.get("client", "NOT FOUND"),
                target_demographic=doc.get("target_demographic", "NOT FOUND"),
                platforms=doc.get("platforms", []),
                notes=doc.get("notes", "NOT FOUND")
            )
        )
    return notes_list
