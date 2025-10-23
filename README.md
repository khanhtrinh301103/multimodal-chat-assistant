# Multi-Modal Chat Assistant

A full-stack application that provides conversational AI capabilities for text, image, and CSV data analysis. Built with FastAPI backend and Next.js frontend.

## Features

- **Text Chat**: Multi-turn conversational AI for text-based interactions (API from gemini-2.5-flash)
- **Image Analysis**: Upload images and get AI-powered descriptions and Q&A (API from claude-sonnet-4-5)
- **CSV Analysis**: Upload CSV files or provide URLs for data analysis and insights (API from claude-3-5-haiku-latest helped by Claude 3.5 Sonnet to retry when overloading)
- **Authentication**: JWT-based authentication system
- **Conversation History**: Track and retrieve chat history
- **Vector Database**: Qdrant integration for RAG (Retrieval-Augmented Generation)
- **Database**: Supabase PostgreSQL for data persistence

## Tech Stack

### Backend
- **FastAPI**: Python web framework
- **Supabase**: PostgreSQL database and authentication
- **Qdrant**: Vector database for embeddings
- **Pydantic**: Data validation and serialization
- **JWT**: Authentication tokens
- **Uvicorn**: ASGI server

### Frontend
- **Next.js 14**: React framework
- **TypeScript**: Type safety
- **Tailwind CSS**: Styling
- **Axios**: HTTP client
- **Supabase Client**: Frontend database integration

## Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.8+**: [Download Python](https://www.python.org/downloads/)
- **Node.js 18+**: [Download Node.js](https://nodejs.org/)
- **Git**: [Download Git](https://git-scm.com/)
- **Supabase Account**: [Sign up for Supabase](https://supabase.com/)
- **Qdrant Account** (Optional): [Sign up for Qdrant](https://cloud.qdrant.io/)

## Installation

### 1. Clone the Repository

```bash
git clone <your-repository-url>
cd multimodal-chat-assistant
```

### 2. Backend Setup

#### Create Python Virtual Environment

```bash
cd backend
python -m venv .venv
```

#### Activate Virtual Environment

**Windows (Command Prompt):**
```cmd
.venv\Scripts\activate.bat
```

**Windows (PowerShell):**
```powershell
.venv\Scripts\Activate.ps1
```

**macOS/Linux:**
```bash
source .venv/bin/activate
```

#### Install Dependencies

```bash
pip install -r requirements.txt
```

#### Environment Variables

Create a `.env` file in the `backend` directory:

```env
# Supabase Configuration
SUPABASE_URL=your_supabase_project_url
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key

# Qdrant Configuration (Optional)
QDRANT_URL=your_qdrant_url
QDRANT_API_KEY=your_qdrant_api_key

# JWT Configuration
JWT_SECRET_KEY=your_jwt_secret_key
JWT_ALGORITHM=HS256

# API Keys (Optional)
ANTHROPIC_API_KEY=your_anthropic_api_key
GOOGLE_API_KEY=your_google_api_key
```

### 3. Frontend Setup

#### Install Dependencies

```bash
cd frontend
npm install
```

#### Environment Variables

Create a `.env.local` file in the `frontend` directory:

```env
# Supabase Configuration
NEXT_PUBLIC_SUPABASE_URL=your_supabase_project_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key

# Backend API
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Running Locally

### Option B: Command Prompt (Recommended - No restrictions)

#### Start Backend Server

Open Command Prompt and run:

```cmd
cd backend
.venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000
```

The backend will be available at `http://localhost:8000`

#### Start Frontend Development Server

Open a new Command Prompt and run:

```cmd
cd frontend
npm run dev
```

The frontend will be available at `http://localhost:3000`

### Alternative: PowerShell

If you prefer PowerShell:

```powershell
# If script execution is restricted, run this first (one-time):
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process

# Backend
cd backend
.\.venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --reload --port 8000

# Frontend (new terminal)
cd frontend
npm run dev
```

## Project Structure

```
multimodal-chat-assistant/
│
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                   # FastAPI entrypoint
│   │   ├── database/                 # Database connections
│   │   │   ├── __init__.py
│   │   │   ├── supabase_client.py   # PostgreSQL connection
│   │   │   └── qdrant_client.py     # Vector DB connection
│   │   ├── routers/                 # API endpoints
│   │   │   ├── __init__.py
│   │   │   ├── auth.py              # Authentication
│   │   │   ├── chat.py              # Text chat
│   │   │   ├── csv.py               # CSV analysis
│   │   │   ├── history.py           # Conversation history
│   │   │   └── image.py             # Image analysis
│   │   ├── services/                # Business logic
│   │   │   ├── __init__.py
│   │   │   ├── chat_service.py      # Chat logic
│   │   │   ├── csv_service.py       # CSV analysis
│   │   │   ├── image_service.py     # Image processing
│   │   │   ├── rag_service.py       # RAG logic
│   │   │   └── storage_service.py   # File uploads
│   │   ├── models/                  # Data models
│   │   │   ├── __init__.py
│   │   │   └── dto.py               # Pydantic models
│   │   └── utils/                   # Utilities
│   │       ├── __init__.py
│   │       ├── jwt_verify.py        # JWT verification
│   │       └── plots.py             # Plot generation
│   └── requirements.txt             # Python dependencies
│
├── frontend/
│   ├── app/                         # Next.js app directory
│   │   ├── auth/
│   │   │   └── page.tsx             # Authentication page
│   │   ├── favicon.ico              # Site favicon
│   │   ├── globals.css              # Global styles
│   │   ├── layout.tsx               # Root layout
│   │   └── page.tsx                 # Main page
│   ├── src/
│   │   ├── components/              # React components
│   │   │   ├── Auth/
│   │   │   │   ├── AuthProvider.tsx # Authentication provider
│   │   │   │   ├── LoginForm.tsx    # Login form component
│   │   │   │   └── RegisterForm.tsx # Registration form component
│   │   │   ├── ChatBox.tsx          # Text chat interface
│   │   │   ├── CsvPanel.tsx         # CSV analysis component
│   │   │   ├── ImageUpload.tsx      # Image upload component
│   │   │   └── ProtectedRoute.tsx   # Route protection component
│   │   ├── hooks/
│   │   │   └── useAuth.ts           # Authentication hook
│   │   ├── lib/
│   │   │   ├── api.ts               # API client
│   │   │   └── supabase.ts          # Supabase client
│   │   └── types/
│   │       └── user.ts              # User type definitions
│   ├── public/                      # Static assets
│   │   ├── file.svg
│   │   ├── globe.svg
│   │   ├── next.svg
│   │   ├── vercel.svg
│   │   └── window.svg
│   ├── package.json                 # Node.js dependencies
│   ├── package-lock.json            # Dependency lock file
│   ├── next.config.js               # Next.js configuration
│   ├── next-env.d.ts                # Next.js TypeScript declarations
│   ├── tailwind.config.ts           # Tailwind CSS configuration
│   ├── postcss.config.js            # PostCSS configuration
│   ├── postcss.config.mjs           # PostCSS configuration (ESM)
│   ├── tsconfig.json                # TypeScript configuration
│   └── README.md                    # Frontend documentation
│
├── project_structure.txt            # Project structure documentation
└── README.md                        # This file
```

## API Documentation

Once the backend is running, you can access the interactive API documentation at:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## Development

### Backend Development

The backend uses FastAPI with automatic reloading. When you make changes to Python files, the server will automatically restart.

### Frontend Development

The frontend uses Next.js with hot reloading. Changes to React components will be reflected immediately in the browser.

### Database Setup

1. **Supabase**: Create a new project at [supabase.com](https://supabase.com)
2. **Qdrant** (Optional): Set up a cloud instance at [cloud.qdrant.io](https://cloud.qdrant.io/)