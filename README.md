# LLM-Enhanced ETL Application (Enhanced Version)

This project ingests messy text files containing notes on media targeting and advertisement, uses a Large Language Model (OpenAI) to parse them into standardized records, and stores them in a MongoDB database. A React-based frontend allows you to upload new notes, view and filter results, and see simple data visualizations.

## Table of Contents
1. [What's New](#whats-new)
2. [Features](#features)
3. [Architecture Overview](#architecture-overview)
4. [Prerequisites](#prerequisites)
5. [Installation & Setup](#installation--setup)
6. [Usage](#usage)
7. [Configuration](#configuration)
8. [Folder Structure](#folder-structure)
9. [Enhancements](#enhancements)
10. [Contributing](#contributing)
11. [License](#license)

## What's New
1. **Enhanced Prompting**  
   - The LLM prompt has been improved to identify multiple separate sets of data within a single text file, returning each set as its own record.  
   - Fallbacks are used: if a field can’t be found, "NOT FOUND" is inserted to ensure consistency.

2. **Multiple Record Insertion**  
   - If the LLM sees multiple campaigns or clients in the same file, we now split them into multiple documents.

3. **Refined UI**  
   - The React frontend is styled with a modern approach (e.g., Bootstrap) and includes a simple bar chart visualization (powered by `recharts`) to illustrate notes by client.

## Features
- **File Upload**: Upload raw text files through a React UI.  
- **LLM Parsing**: GPT-3.5-turbo (OpenAI) extracts structured data from messy notes.  
- **Multiple Record Storage**: Automatically create multiple entries if multiple clients/campaigns are found.  
- **Data Browsing**: View structured notes in a card layout.  
- **Data Visualization**: Simple bar chart showing the count of notes by client.  
- **MongoDB Storage**: Stores documents in `notes_db.notes_collection`.  
- **Containerized**: The entire app (backend, frontend, database) runs on Docker Compose.

## Architecture Overview
               +--------------+
               |   React UI   |
               |  (Frontend)  |
               +------+------+  
                      |  
                      v
    +------------------------+
    |      FastAPI API      |
    | (LLM Parsing Logic)   | ----> Calls OpenAI
    +----------+------------+
               |
               |  (MongoDB)
               v
          +-------------+
          |   MongoDB   |
          +-------------+

## Prerequisites
- **Docker & Docker Compose**  
- **OpenAI API Key**

## Installation & Setup
1. **Clone the Repo** or put this code in your own repo, then `cd` to the project root.
2. **Set Your OpenAI API Key**  
   - Create a `.env` file or export in your shell:  
     `export OPENAI_API_KEY=sk-xxxxx`
3. **Run**  
   - `docker-compose up --build`

## Usage
- **Frontend**: [http://localhost:3000](http://localhost:3000)  
- **Backend**: [http://localhost:8000](http://localhost:8000)

## Configuration
- **OPENAI_API_KEY**  
- **MONGO_URI** (optional)

## Folder Structure
. ├── backend/ │ ├── main.py │ ├── requirements.txt │ ├── Dockerfile │ ├── frontend/ │ ├── public/ │ │ └── index.html │ ├── src/ │ │ ├── App.js │ │ ├── api.js │ └── Dockerfile │ ├── db/ │ └── Dockerfile ├── docker-compose.yml └── README.md

## Enhancements
- **Advanced Prompting** with structured fallback fields.
- **Multiple Document Parsing** per file.
- **Bootstrap** & **Recharts** for a clean UI and simple visualization.

## Contributing
1. **Fork** the repo
2. **Create** a new branch
3. **Make** changes, commit, push, and open a Pull Request


Enjoy your enhanced LLM-ETL system!
