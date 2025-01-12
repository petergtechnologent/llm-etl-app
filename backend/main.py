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

# We will read MONGO_URI from environment variables as well, or fallback to default
MONGO_URI = os.getenv("MONGO_URI", "mongodb://db:27017")

client = MongoClient(MONGO_URI)
db = client["notes_db"]
collection = db["notes_collection"]

app = FastAPI()

# Configure CORS so React can talk to our backend
origins = [
    "http://localhost:3000",  # React dev server or the containerized server
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
    client: str = None
    target_demographic: str = None
    platforms: List[str] = []
    notes: str = None


@app.get("/")
def root():
    return {"message": "Welcome to the LLM-Enhanced ETL API"}


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    Upload a text file, parse it with the LLM, store in MongoDB,
    and return the structured data with _id converted to string.
    """
    try:
        raw_content = (await file.read()).decode("utf-8", errors="ignore")
        
        # Use the LLM to parse and structure this data
        prompt = f"""
        You will receive raw text notes about an ad/media targeting plan. 
        Extract and standardize the information into JSON fields with keys:
        "client", "target_demographic", "platforms", and "notes".
        If something is missing, use a placeholder. 
        Here is the text:
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
        
        # Try to parse JSON output
        try:
            structured_data = json.loads(parsed_text)
        except json.JSONDecodeError:
            # fallback if the LLM didn't provide valid JSON
            structured_data = {
                "client": None,
                "target_demographic": None,
                "platforms": [],
                "notes": raw_content
            }

        # Insert a unique ID
        note_id = str(uuid.uuid4())
        structured_data["id"] = note_id

        # Insert into MongoDB
        insert_result = collection.insert_one(structured_data)

        # Convert MongoDB's _id to a string if you want to keep it, or remove it
        structured_data["_id"] = str(insert_result.inserted_id)

        return {
            "status": "success",
            "data": structured_data
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
    Convert the _id field to string or remove it.
    """
    notes_cursor = collection.find({})
    notes_list = []
    for doc in notes_cursor:
        # Convert ObjectId to string if it exists
        if "_id" in doc:
            doc["_id"] = str(doc["_id"])
        # Convert to Note model. If doc doesn't have 'id', fallback to the string version of _id
        notes_list.append(
            Note(
                id=doc.get("id", doc["_id"]),
                client=doc.get("client", ""),
                target_demographic=doc.get("target_demographic", ""),
                platforms=doc.get("platforms", []),
                notes=doc.get("notes", "")
            )
        )
    return notes_list
