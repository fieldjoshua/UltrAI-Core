# Ultra MVP Setup Guide

This guide will help you set up and run the Ultra MVP, which allows you to connect to multiple LLMs, conduct queries, and observe differences in analyses between models.

## Prerequisites

- Node.js (v16+)
- Python (v3.9+)
- npm or yarn
- Git

## Environment Setup

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/ultra.git
cd ultra
```

### 2. Set Up Environment Variables

Copy the example environment file and update it with your API keys:

```bash
cp env.example .env
```

Edit the `.env` file and add your API keys for the LLM providers you want to use:

- **OpenAI API Key**: Required for GPT models
- **Anthropic API Key**: Required for Claude models
- **Google API Key**: Required for Gemini models

You can enable the mock LLM service for testing without real API keys by setting:

```
ENABLE_MOCK_LLM=true
```

### 3. Install Backend Dependencies

```bash
pip install -r requirements.txt
```

### 4. Install Frontend Dependencies

```bash
cd frontend
npm install
cd ..
```

## Quick Start for Development

### Running the Backend

Start the backend server:

```bash
python backend/run.py
```

This will start the API server on `http://localhost:8000` by default.

### Running the Frontend

In a new terminal, start the frontend development server:

```bash
cd frontend
npm run dev
```

The frontend will be available at `http://localhost:5173`.

## Usage

1. Open your browser and navigate to `http://localhost:5173`
2. Enter a prompt in the input field
3. Select which LLM models to use for comparison
4. Choose an analysis pattern
5. Submit the query and view the results

## Deployment

### Docker Deployment

You can use Docker and Docker Compose to deploy Ultra:

```bash
docker-compose up -d
```

This will start both the frontend and backend services.

### Manual Deployment

#### Backend

For production deployment of the backend:

```bash
cd backend
python start.py --production
```

#### Frontend

Build the frontend for production:

```bash
cd frontend
npm run build
```

Then serve the built files using a web server like Nginx or Vercel.

## API Key Setup Guide

### OpenAI API Key

1. Go to [OpenAI API](https://platform.openai.com/signup)
2. Create an account or log in
3. Navigate to API Keys section
4. Create a new secret key
5. Copy the key to your `.env` file as `OPENAI_API_KEY`

### Anthropic API Key

1. Go to [Anthropic Console](https://console.anthropic.com/)
2. Sign up or log in
3. Navigate to API Keys
4. Create a new API key
5. Copy the key to your `.env` file as `ANTHROPIC_API_KEY`

### Google API Key (Gemini)

1. Go to [Google AI Studio](https://aistudio.google.com/)
2. Sign in with your Google account
3. Navigate to API Keys section
4. Create a new API key
5. Copy the key to your `.env` file as `GOOGLE_API_KEY`

## Troubleshooting

### API Connection Issues

- Verify that your API keys are correctly set in the `.env` file
- Check that the backend server is running
- Check the backend logs for any error messages

### Frontend Connection Issues

- Ensure the `REACT_APP_API_URL` in your `.env` file points to your backend server
- Check browser console for any error messages
- Verify that CORS settings are correctly configured in the backend

## Advanced Configuration

For advanced configuration options, see:

- [Backend Configuration Guide](./backend-configuration.md)
- [Frontend Configuration Guide](./frontend-configuration.md)
- [Performance Tuning Guide](./performance-tuning.md)

## Support

If you encounter any issues, please open an issue on the GitHub repository or contact the development team at <support@ultra-ai.com>.
