import os
import uuid
import re
import json
import openai
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

MONGO_URI = os.getenv("MONGO_URI", "mongodb://db:27017")

client = MongoClient(MONGO_URI)
db = client["notes_db"]
collection = db["notes_collection"]

app = FastAPI()

# Adjust CORS if needed
origins = ["http://localhost:3000"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Note(BaseModel):
    id: str
    client: str = "NOT FOUND"
    target_demographic: str = "NOT FOUND"
    platforms: List[str] = []
    notes: str = "NOT FOUND"


@app.get("/")
def root():
    return {"message": "Welcome to the Enhanced LLM-ETL API"}


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    1. Receive a text file with ad/media notes.
    2. Send it to the LLM for parsing into an array of structured objects.
    3. Attempt to parse that array. If there's an error, do a second pass by asking the LLM
       to produce valid JSON (removing backticks, etc.).
    4. Insert each object into MongoDB.
    5. Return the inserted objects with their _id strings.
    """
    try:
        # Read file content
        raw_content = (await file.read()).decode("utf-8", errors="ignore")

        # The main prompt that instructs the LLM to return valid JSON in array form
        parsing_prompt = f"""
        You will receive raw text notes about one or more ad/media targeting plans.
        They may contain multiple distinct sets of information for different clients.

        Task:
        1. Identify each 'group' of data if multiple groups/clients/campaigns appear.
        2. For each group, extract these fields:
           - client
           - target_demographic
           - platforms
           - notes (additional important details)
        3. If a field cannot be identified, use "NOT FOUND" for that field.
        4. Return an array of JSON objects with NO triple backticks or markdown formatting. Example:

           [
             {{
               "client": "XYZ Brand",
               "target_demographic": "Teens 13-18",
               "platforms": ["TikTok", "Instagram"],
               "notes": "Focus on short video ads."
             }},
             ...
           ]

        Here is the text to parse:
        {raw_content}
        """

        # First LLM call
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful data parser."},
                {"role": "user", "content": parsing_prompt}
            ],
            temperature=0.0
        )

        parsed_text = response.choices[0].message["content"].strip()
        print("LLM initial response:", parsed_text)  # Debug in logs

        # 1. Remove triple backticks, if any:
        cleaned_text = re.sub(r"```+", "", parsed_text).strip()

        # 2. Attempt to parse as JSON
        parsed_array = None
        try:
            parsed_array = json.loads(cleaned_text)
        except json.JSONDecodeError:
            # Second pass - ask LLM to fix the formatting
            fix_prompt = f"""
            You previously returned some JSON that was not parseable.
            Here is your output (without triple backticks if any):

            {parsed_text}

            Please provide ONLY valid JSON in the form of an array of objects, with no extra text.
            """

            fix_response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful data parser."},
                    {"role": "user", "content": fix_prompt}
                ],
                temperature=0.0
            )
            second_text = fix_response.choices[0].message["content"].strip()
            print("LLM second pass response:", second_text)

            # Clean up again
            second_cleaned = re.sub(r"```+", "", second_text).strip()
            try:
                parsed_array = json.loads(second_cleaned)
            except json.JSONDecodeError:
                # If it still fails, fallback to a single doc
                parsed_array = [{
                    "client": "NOT FOUND",
                    "target_demographic": "NOT FOUND",
                    "platforms": [],
                    "notes": raw_content
                }]

        # If parsed_array is None or not a list, fallback
        if not parsed_array or not isinstance(parsed_array, list):
            parsed_array = [{
                "client": "NOT FOUND",
                "target_demographic": "NOT FOUND",
                "platforms": [],
                "notes": raw_content
            }]

        # Insert each object in parsed_array
        inserted_docs = []
        for entry in parsed_array:
            client_val = entry.get("client") or "NOT FOUND"
            target_val = entry.get("target_demographic") or "NOT FOUND"
            platforms_val = entry.get("platforms", [])
            if not isinstance(platforms_val, list):
                platforms_val = [str(platforms_val)]
            notes_val = entry.get("notes") or "NOT FOUND"

            note_id = str(uuid.uuid4())
            doc = {
                "id": note_id,
                "client": client_val,
                "target_demographic": target_val,
                "platforms": platforms_val,
                "notes": notes_val
            }
            result = collection.insert_one(doc)
            doc["_id"] = str(result.inserted_id)
            inserted_docs.append(doc)

        return {
            "status": "success",
            "inserted_count": len(inserted_docs),
            "data": inserted_docs
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


@app.get("/notes", response_model=List[Note])
def get_notes():
    """
    Retrieve all structured notes from the database.
    """
    notes_cursor = collection.find({})
    notes_list = []
    for doc in notes_cursor:
        # Convert _id to string if present
        if "_id" in doc:
            doc["_id"] = str(doc["_id"])

        client_val = doc.get("client") or "NOT FOUND"
        target_val = doc.get("target_demographic") or "NOT FOUND"
        platforms_val = doc.get("platforms") or []
        notes_val = doc.get("notes") or "NOT FOUND"

        note_instance = Note(
            id=doc.get("id", ""),
            client=client_val,
            target_demographic=target_val,
            platforms=platforms_val,
            notes=notes_val
        )
        notes_list.append(note_instance)

    return notes_list
