# Ultra Backend

This directory contains the backend server code for the Ultra AI Framework.

## Directory Structure

- **api/**: API endpoints and routing
  - `main.py`: FastAPI application and route definitions
  - `error_handler.py`: Error handling middleware

- **services/**: Business logic and services
  - `pricing_*.py`: Token usage calculation and pricing services
  - `interactive_pricing.py`: Interactive pricing models
  - `manage_parameters.py`: Parameter management system
  - `parameter_editor.py`: Parameter editing interface
  - `parameter_glossary_generator.py`: Documentation generation for parameters

- **middleware/**: Request processing middleware
  - Authentication, logging, etc.

- **db/**: Database models and connections
  - Data persistence and storage

## Configuration

Backend configuration is managed through environment variables. Create a `.env` file in the backend directory with the following variables:

```
PORT=8080
ENV=development
LOG_LEVEL=info
```

## Running the Backend

To run the backend server:

```bash
cd backend
pip install -r requirements.txt
python -m api.main
```

## API Documentation

Once running, API documentation is available at:

- Swagger UI: <http://localhost:8080/docs>
- ReDoc: <http://localhost:8080/redoc>

## Technologies

- FastAPI
- Pydantic
- SQLAlchemy (for database operations)
- Uvicorn (ASGI server)
