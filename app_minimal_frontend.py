"""Minimal app focused on serving frontend"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

# FastAPI app
app = FastAPI(title="UltraAI Frontend", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health():
    return {"status": "ok", "frontend": "active"}

@app.get("/")
async def serve_frontend():
    """Serve cyberpunk-styled frontend"""
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Ultra AI</title>
        <style>
            body { 
                margin: 0; 
                font-family: 'Orbitron', 'Arial', monospace; 
                background: linear-gradient(135deg, #0a0f1c 0%, #1a2332 100%);
                color: #00FFFF;
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                overflow: hidden;
            }
            .grid-bg {
                position: absolute;
                inset: 0;
                opacity: 0.1;
                background-image: 
                    linear-gradient(rgba(0, 255, 255, 0.5) 1px, transparent 1px),
                    linear-gradient(90deg, rgba(0, 255, 255, 0.5) 1px, transparent 1px);
                background-size: 50px 50px;
                animation: pulse 4s ease-in-out infinite;
            }
            @keyframes pulse {
                0%, 100% { opacity: 0.1; }
                50% { opacity: 0.3; }
            }
            .container {
                text-align: center;
                padding: 2rem;
                z-index: 10;
                position: relative;
            }
            h1 {
                font-size: clamp(3rem, 8vw, 6rem);
                text-shadow: 
                    0 0 10px #00FFFF,
                    0 0 20px #00FFFF,
                    0 0 30px #00FFFF;
                margin-bottom: 1rem;
                letter-spacing: 0.1em;
                animation: neon-pulse 2s ease-in-out infinite;
            }
            @keyframes neon-pulse {
                0%, 100% {
                    text-shadow: 
                        0 0 10px #00FFFF,
                        0 0 20px #00FFFF,
                        0 0 30px #00FFFF;
                }
                50% {
                    text-shadow: 
                        0 0 20px #00FFFF,
                        0 0 30px #00FFFF,
                        0 0 40px #00FFFF,
                        0 0 50px #00FFFF;
                }
            }
            .tagline {
                font-size: clamp(1rem, 3vw, 1.5rem);
                color: #FF6B35;
                text-shadow: 
                    0 0 10px #FF6B35,
                    0 0 20px #FF6B35;
                margin-bottom: 2rem;
                letter-spacing: 0.05em;
            }
            .status {
                color: #00FF00;
                font-size: 1.2rem;
                margin-bottom: 2rem;
                text-shadow: 0 0 10px #00FF00;
            }
            .links {
                display: flex;
                gap: 2rem;
                justify-content: center;
                flex-wrap: wrap;
            }
            .link {
                color: #00FFFF;
                text-decoration: none;
                padding: 0.8rem 1.5rem;
                border: 2px solid #00FFFF;
                border-radius: 8px;
                transition: all 0.3s ease;
                background: rgba(0, 255, 255, 0.1);
                backdrop-filter: blur(10px);
            }
            .link:hover {
                background: rgba(0, 255, 255, 0.2);
                box-shadow: 
                    0 0 20px rgba(0, 255, 255, 0.4),
                    inset 0 0 20px rgba(0, 255, 255, 0.1);
                transform: translateY(-2px);
            }
            @media (max-width: 768px) {
                .links { flex-direction: column; align-items: center; }
                .container { padding: 1rem; }
            }
        </style>
    </head>
    <body>
        <div class="grid-bg"></div>
        <div class="container">
            <h1>ULTRA AI</h1>
            <div class="tagline">MULTIPLY YOUR AI!</div>
            <div class="status">✅ Frontend Successfully Deployed</div>
            <div class="links">
                <a href="/health" class="link">Health Check</a>
                <a href="/docs" class="link">API Documentation</a>
            </div>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)