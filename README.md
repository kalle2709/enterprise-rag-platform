# Enterprise RAG Platform

A production style multi agent AI platform that orchestrates specialized agents for document search, meeting summarization, and task automation, backed by persistent memory, role based access, and Dockerized AWS deployment.

## Overview

This platform combines Retrieval Augmented Generation (RAG) with multi agent orchestration to handle three core workflows: searching and answering questions from stored documents, summarizing meeting transcripts into key points and action items, and extracting structured task lists from natural language requests. A supervisor agent classifies incoming requests and routes them to the correct specialist agent automatically.

## Features

- RAG powered document search using semantic similarity over stored content
- Multi agent orchestration with a supervisor agent that routes requests to the right specialist
- Meeting summarization agent that extracts key points, decisions, and action items
- Task automation agent that converts natural language requests into prioritized task lists
- Persistent memory that stores conversation history across sessions in PostgreSQL
- Role based access control with admin and user level permissions
- Dockerized services for consistent local development and cloud deployment
- Deployed on AWS EC2 using Docker Compose

## Tech Stack

- **Backend:** FastAPI, Python
- **Agent Orchestration:** LangGraph, LangChain
- **LLM:** Google Gemini (gemini-2.5-flash)
- **Embeddings:** Google Gemini (gemini-embedding-001)
- **Vector Database:** ChromaDB
- **Relational Database:** PostgreSQL, SQLAlchemy
- **Containerization:** Docker, Docker Compose
- **Deployment:** AWS EC2

## Architecture

Incoming requests are classified by a supervisor agent built with LangGraph, which determines whether the request belongs to document search, meeting summarization, or task automation. The relevant agent then processes the request: the document search agent retrieves relevant chunks from ChromaDB using semantic similarity and generates a grounded answer, while the meeting summary and task automation agents use structured prompts to produce their outputs directly. Every interaction is persisted to PostgreSQL for long term conversational memory. Access to sensitive routes, such as document ingestion, is restricted using API key based role checks.

## Getting Started

### Prerequisites

- Python 3.11+
- Docker and Docker Compose
- A Google Gemini API key ([get one here](https://aistudio.google.com/apikey))

### Local Setup

1. Clone the repository

```bash
git clone https://github.com/<your-username>/enterprise-rag-platform.git
cd enterprise-rag-platform
```

2. Create your environment file

```bash
cp .env.example .env
```

Then edit `.env` and add your Gemini API key.

3. Start all services

```bash
docker compose up --build
```

4. Verify the app is running

```
http://localhost:8000/health
```

5. Explore the API

```
http://localhost:8000/docs
```

## API Endpoints

| Method | Endpoint                    | Description                                           | Access |
| ------ | --------------------------- | ----------------------------------------------------- | ------ |
| POST   | `/documents/`               | Ingest a new document                                 | Admin  |
| POST   | `/documents/search`         | Semantic search over stored documents                 | User   |
| POST   | `/documents/ask`            | Ask a question, answered using RAG                    | User   |
| POST   | `/agents/summarize-meeting` | Summarize a meeting transcript                        | User   |
| POST   | `/agents/extract-tasks`     | Extract tasks from a request                          | User   |
| POST   | `/agents/route`             | Supervisor agent, auto routes to the right specialist | User   |

## Authentication

Requests must include an `x-api-key` header. Two roles are supported:

- **Admin:** full access, including document ingestion
- **User:** access to search, ask, and agent routes

## Environment Variables

| Variable         | Description                  |
| ---------------- | ---------------------------- |
| `DATABASE_URL`   | PostgreSQL connection string |
| `CHROMA_HOST`    | ChromaDB host                |
| `CHROMA_PORT`    | ChromaDB port                |
| `GOOGLE_API_KEY` | Google Gemini API key        |

## Project Structure

```
enterprise-rag-platform/
├── app/
│   ├── main.py                  # FastAPI app entrypoint
│   ├── config.py                # Environment settings
│   ├── auth.py                  # Role based access control
│   ├── agents/
│   │   ├── document_search_agent.py
│   │   ├── meeting_summary_agent.py
│   │   ├── task_automation_agent.py
│   │   └── supervisor_agent.py
│   ├── models/
│   │   ├── document.py
│   │   ├── conversation.py
│   │   └── schemas.py
│   ├── routes/
│   │   ├── documents.py
│   │   └── agents.py
│   └── db/
│       ├── __init__.py
│       └── vectorstore.py
├── requirements.txt
├── docker-compose.yml
├── Dockerfile
├── .env.example
└── README.md
```

## Deployment

The platform is deployed on AWS EC2 using Docker Compose, running FastAPI, PostgreSQL, and ChromaDB as separate containers on a single instance.
