# LLM-Enhanced ETL Application

An end-to-end application that:
- Ingests large, messy text notes regarding media targeting and advertisement.  
- Uses a Large Language Model (OpenAI) via FastAPI to parse and standardize those notes into a consistent schema.  
- Stores structured data in MongoDB.  
- Provides a React frontend to view and upload new notes.

## Table of Contents
1. [Features](#features)  
2. [Architecture Overview](#architecture-overview)  
3. [Prerequisites](#prerequisites)  
4. [Installation & Setup](#installation--setup)  
5. [Usage](#usage)  
6. [Configuration](#configuration)  
7. [Folder Structure](#folder-structure)  
8. [Contributing](#contributing)  
9. [License](#license)

---

## Features
1. **File Upload**  
   - Upload raw text files through a React-based UI.
2. **LLM Parsing**  
   - Uses OpenAI’s GPT model to parse unstructured text and extract fields such as client name, target audience, platforms, and notes.
3. **Database Storage**  
   - Stores the parsed data in a MongoDB collection.
4. **Data Browsing**  
   - View existing parsed notes in the frontend, including client name, demographic, platforms, and notes.
5. **Containerized**  
   - The entire project (backend, frontend, and MongoDB) runs via `docker-compose`.

---

## Architecture Overview

```
                   +--------------+
                   |   React UI   |
                   |  (Frontend)  |
                   +------+------+  
                          |  (HTTP)
                          v
        +------------------------+
        |      FastAPI API      |
        | (LLM Parsing Logic)   | ---->   Calls OpenAI API
        +----------+------------+
                   |
                   |  (MongoDB client)
                   v
             +-----------+
             |  MongoDB  |
             +-----------+
```

1. **Frontend (React)**  
   - Uploads text files  
   - Displays structured notes
2. **Backend (FastAPI)**  
   - Receives uploaded files (`/upload`)  
   - Sends content to OpenAI for parsing  
   - Stores parsed results in MongoDB  
   - Exposes `/notes` endpoint to list stored data
3. **MongoDB**  
   - Stores all parsed notes in `notes_db.notes_collection`

---

## Prerequisites

1. **Docker & Docker Compose**  
   - Make sure you have Docker installed (version 20+ recommended).
   - Docker Compose plugin or `docker-compose` CLI must be available.
2. **OpenAI API Key**  
   - You need a valid OpenAI API key to enable the LLM parsing. 

---

## Installation & Setup

1. **Clone the Repository**  
   ```bash
   git clone https://github.com/yourusername/my-etl-llm-app.git
   cd my-etl-llm-app
   ```

2. **Set Environment Variables**  
   - Create a `.env` file in the root directory (or set them in your shell), for example:
     ```
     OPENAI_API_KEY=sk-<your-api-key>
     ```
   - By default, the backend looks for `OPENAI_API_KEY` and (optionally) `MONGO_URI`.

3. **Build & Run Containers**  
   ```bash
   docker-compose up --build
   ```
   - This will:
     1. Pull/build the MongoDB container.  
     2. Build the FastAPI backend container (including dependencies).  
     3. Build the React frontend container, then serve it via Nginx.

4. **Check Logs**  
   - In the terminal, you’ll see logs for `my_mongo`, `my_backend`, and `my_frontend`.  
   - If everything starts without errors, you’re ready to use the app.

---

## Usage

1. **Access the Frontend**  
   - Go to [http://localhost:3000](http://localhost:3000) (by default) in your browser.  
   - You should see the React UI with an option to upload files and a list of parsed notes.

2. **Upload a File**  
   - Click on the file chooser button.  
   - Select a messy notes text file (e.g. `random1.txt`, `huge_messy_notes.txt`, etc.).  
   - Click **Upload**.  

3. **View Parsed Notes**  
   - Once uploaded, the backend sends the file content to the OpenAI API for parsing.  
   - The structured data is stored in MongoDB.  
   - The frontend will automatically refresh to show the newly added note(s).

---

## Configuration

- **Environment Variables**  
  - **`OPENAI_API_KEY`**: Required. Your personal or org-level key from OpenAI.  
  - **`MONGO_URI`**: Optional. If you want to point to an external Mongo instance. By default, it uses `mongodb://db:27017`.

- **Ports**  
  - **Backend**: Exposed on `8000`.  
  - **Frontend**: Exposed on `3000`.  
  - **MongoDB**: Exposed on `27017`.  

You can modify these in the `docker-compose.yml` file if needed.

---

## Folder Structure

```
my-etl-llm-app/
│
├── backend/
│   ├── main.py
│   ├── requirements.txt
│   ├── Dockerfile
│   └── ...
│
├── frontend/
│   ├── package.json
│   ├── Dockerfile
│   └── src/
│       ├── App.js
│       ├── api.js
│       └── ...
│
├── db/
│   ├── Dockerfile (optional, we might just use official Mongo image)
│   └── ...
│
├── data/
│   ├── random1.txt
│   ├── random2.txt
│   └── ...
│
├── docker-compose.yml
├── .env (ignored in git, stores your OPENAI_API_KEY)
└── README.md
```

---

## Contributing

1. **Fork** the repository.  
2. **Create** a new branch (`git checkout -b feature/my-new-feature`).  
3. **Commit** your changes (`git commit -am 'Add some feature'`).  
4. **Push** to the branch (`git push origin feature/my-new-feature`).  
5. **Open** a Pull Request on GitHub.

---

**Enjoy your LLM-Enhanced ETL System!**  