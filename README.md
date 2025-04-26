# UltraAI Prototype

A powerful document analysis platform leveraging multiple LLM integrations.

## Features

- Document upload and processing
- Multiple LLM integrations (GPT-4, Claude 3, Llama 2, Mistral, Mixtral)
- Custom prompt input
- Multiple analysis types:
  - Text summarization
  - Sentiment analysis
  - Key points extraction
  - Topic modeling
  - Entity recognition
- Modern React frontend with Material-UI
- FastAPI backend with async processing

## Setup

### Backend Setup

1. Create a Python virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate  # On Unix/macOS
# or
.venv\Scripts\activate  # On Windows
```

2. Install dependencies:

```bash
cd backend
pip install -r requirements.txt
```

3. Set up environment variables:

```bash
cp .env.example .env
# Edit .env with your API keys and configuration
```

4. Run the backend server:

```bash
uvicorn app.main:app --reload --port 8085
```

### Frontend Setup

1. Install Node.js dependencies:

```bash
cd frontend
npm install
```

2. Set up environment variables:

```bash
cp .env.example .env
# Edit .env with your configuration
```

3. Run the development server:

```bash
npm run dev
```

## Project Structure

```
ultraai/
├── backend/
│   ├── app/
│   │   ├── routes/      # API endpoints
│   │   ├── services/    # Business logic
│   │   ├── utils/       # Utility functions
│   │   └── database/    # Database models
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/  # React components
│   │   ├── services/    # API services
│   │   ├── hooks/       # Custom hooks
│   │   └── utils/       # Utility functions
│   └── package.json
└── README.md
```

## API Documentation

The API documentation is available at `http://localhost:8085/docs` when the backend server is running.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License - see LICENSE file for details
