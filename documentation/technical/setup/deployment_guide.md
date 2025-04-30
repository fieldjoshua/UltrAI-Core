# Ultra MVP Deployment Guide

This guide explains how to deploy the Ultra MVP to various hosting services. The system consists of a backend API and a frontend application that can be deployed separately or together.

## Deployment Options

You can deploy Ultra MVP in several ways:

1. **Vercel (easiest)**: Deploy both frontend and backend with minimal configuration
2. **Traditional VPS**: Full control but more complex setup
3. **Docker**: Containerized deployment for consistency across environments
4. **Separate Services**: Deploy frontend and backend on different platforms

## Prerequisites

Before deploying, ensure you have:

- A production-ready codebase with working local setup
- API keys for required LLM services (OpenAI, Anthropic, Google)
- A GitHub account (for Vercel and similar services)
- (Optional) Docker installed if using containerized deployment

## 1. Vercel Deployment (Recommended)

Vercel is the simplest deployment option for Ultra MVP.

### Backend on Vercel

1. **Prepare your repository**:
   - Make sure `vercel.json` is properly configured:

   ```json
   {
     "version": 2,
     "builds": [
       { "src": "backend/app.py", "use": "@vercel/python" }
     ],
     "routes": [
       { "src": "/api/(.*)", "dest": "backend/app.py" }
     ],
     "env": {
       "PYTHONPATH": "."
     }
   }
   ```

2. **Add environment variables**:
   - Go to Vercel Dashboard > Project Settings > Environment Variables
   - Add all variables from your `.env` file including API keys

3. **Deploy to Vercel**:

   ```bash
   # Install Vercel CLI
   npm i -g vercel

   # Login and deploy
   vercel login
   vercel
   ```

4. **Verify backend deployment**:
   - Test the `/api/available-models` endpoint to ensure everything is working
   - Check Vercel logs if issues arise

### Frontend on Vercel

1. **Configure build settings**:
   - Update `frontend/.env.production` with backend URL:

   ```
   REACT_APP_API_URL=https://your-backend-url.vercel.app/api
   ```

2. **Deploy frontend**:

   ```bash
   cd frontend
   vercel
   ```

3. **Link frontend and backend** (optional):
   - On Vercel Dashboard, you can link both deployments for easier management

## 2. Docker Deployment

For more control or self-hosted options, Docker provides a consistent deployment environment.

1. **Build the Docker image**:

   ```bash
   docker build -t ultra-mvp .
   ```

2. **Run the container**:

   ```bash
   docker run -p 8000:8000 --env-file .env ultra-mvp
   ```

3. **Docker Compose** (for development or simple production):

   ```yaml
   # docker-compose.yml
   version: '3'
   services:
     backend:
       build: .
       ports:
         - "8000:8000"
       env_file: .env
     frontend:
       build: ./frontend
       ports:
         - "3000:3000"
       environment:
         - REACT_APP_API_URL=http://backend:8000/api
   ```

   Run with: `docker-compose up`

## 3. Traditional VPS Deployment

For complete control, deploy to a VPS provider like DigitalOcean, Linode, or AWS EC2.

1. **Provision a server**:
   - Ubuntu 20.04+ recommended
   - At least 2GB RAM
   - Configure SSH access

2. **Configure server**:

   ```bash
   # Install dependencies
   sudo apt update
   sudo apt install python3-pip python3-venv nginx

   # Clone repository
   git clone https://github.com/yourusername/Ultra.git
   cd Ultra

   # Setup Python environment
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt

   # Configure environment
   cp env.example .env
   # Edit .env with your production settings
   ```

3. **Configure Nginx**:

   ```
   # /etc/nginx/sites-available/ultra
   server {
       listen 80;
       server_name your-domain.com;

       location /api {
           proxy_pass http://localhost:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }

       location / {
           root /path/to/Ultra/frontend/build;
           try_files $uri /index.html;
       }
   }
   ```

4. **Setup systemd service**:

   ```
   # /etc/systemd/system/ultra.service
   [Unit]
   Description=Ultra MVP API
   After=network.target

   [Service]
   User=ubuntu
   WorkingDirectory=/path/to/Ultra
   ExecStart=/path/to/Ultra/.venv/bin/python backend/run.py
   Restart=always
   Environment=PYTHONPATH=/path/to/Ultra

   [Install]
   WantedBy=multi-user.target
   ```

5. **Start services**:

   ```bash
   sudo systemctl enable nginx
   sudo systemctl start nginx
   sudo systemctl enable ultra
   sudo systemctl start ultra
   ```

## 4. Serverless Deployment (AWS Lambda / Azure Functions)

For serverless deployment, some modifications are needed:

1. **Modify the backend**:
   - Create serverless handlers (`lambda_handler.py` for AWS)
   - Use appropriate wrappers (Mangum for FastAPI on Lambda)

2. **Configure API Gateway**:
   - Set up routes to point to your Lambda function
   - Configure CORS if needed

3. **Deploy with serverless framework**:

   ```bash
   # Install serverless
   npm install -g serverless

   # Deploy
   serverless deploy
   ```

## SSL Configuration

For production deployment, always use HTTPS:

1. **With Vercel**: SSL is automatically configured
2. **With VPS**: Use Certbot with Let's Encrypt:

   ```bash
   sudo apt install certbot python3-certbot-nginx
   sudo certbot --nginx -d your-domain.com
   ```

## Environment Considerations

### Timeout Settings

LLM API calls can be slow. Configure appropriate timeouts:

- Lambda/Serverless: Increase timeout to 60+ seconds
- Nginx: Configure proxy timeouts

  ```
  proxy_read_timeout 300;
  proxy_connect_timeout 300;
  proxy_send_timeout 300;
  ```

### Scaling Considerations

- **Rate Limiting**: Implement rate limiting to avoid excessive API costs
- **Caching**: Configure response caching for repeated queries
- **Connection Pooling**: For database connections if applicable

## Monitoring and Maintenance

1. **Logging**:
   - Configure structured logging with appropriate log levels
   - Consider a service like Sentry for error tracking

2. **Health Checks**:
   - Implement a `/health` endpoint
   - Set up uptime monitoring

3. **Backup**:
   - Regular database backups if applicable
   - Configuration backups

## Troubleshooting Deployment Issues

### Common Issues

1. **CORS Errors**:
   - Ensure CORS headers are properly configured
   - Check frontend API URL matches backend exactly

2. **API Key Issues**:
   - Verify all environment variables are set
   - Check API key permissions and quotas

3. **Memory Limitations**:
   - Increase server resources if needed
   - Monitor memory usage during LLM calls

## Updating the Deployment

For updates to the deployed application:

1. **With Vercel**:
   - Push to GitHub and Vercel will automatically redeploy

2. **With VPS**:

   ```bash
   cd /path/to/Ultra
   git pull
   source .venv/bin/activate
   pip install -r requirements.txt
   sudo systemctl restart ultra
   ```

## Security Considerations

1. **API Key Security**:
   - Never commit API keys to version control
   - Use environment variables or secrets management

2. **Rate Limiting**:
   - Implement API rate limiting to prevent abuse

3. **Input Validation**:
   - Validate all user inputs
   - Sanitize prompts if needed

## Cost Considerations

Remember that LLM API calls can be expensive:

- Implement caching for repeated queries
- Monitor usage to avoid unexpected costs
- Consider usage quotas for users

## Support Resources

If you encounter deployment issues:

- Check the project GitHub repository issues
- Consult documentation for your hosting provider
- Reach out to the Ultra development team
