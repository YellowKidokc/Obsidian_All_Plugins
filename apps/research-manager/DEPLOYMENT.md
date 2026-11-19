# Deployment Guide - Theophysics Backend

Complete guide for deploying the Theophysics Backend API to GitHub and running it.

## 📦 Pre-Deployment Checklist

- [x] Definition processor system created
- [x] Fruits of Spirit API created
- [x] Flask app configured
- [x] Requirements.txt updated
- [x] Documentation complete
- [x] Example files created

## 🚀 Deploying to GitHub

### Step 1: Prepare Local Repository

```bash
cd d:\GitHub\Python-Backend-Dashboards\python_backend

# Initialize git if not already done
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit: Definition Processor + Fruits of Spirit API"
```

### Step 2: Connect to GitHub Repository

```bash
# Add remote (replace with your repo URL)
git remote add origin https://github.com/YellowKidokc/LOWES-BACKEND-CLAUDE.git

# Push to GitHub
git branch -M main
git push -u origin main
```

### Step 3: Verify Upload

Visit: https://github.com/YellowKidokc/LOWES-BACKEND-CLAUDE

You should see:

- ✅ All Python files
- ✅ README_GITHUB.md
- ✅ requirements.txt
- ✅ Data files (fruits_of_spirit.json)
- ✅ Templates
- ✅ Documentation

## 🔧 Local Installation & Testing

### Install Dependencies

```bash
# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Install Ollama (for AI features)

```bash
# Visit https://ollama.ai/ and download installer
# Or use command line:

# Windows: Download from website
# Mac:
curl https://ollama.ai/install.sh | sh

# Pull a model
ollama pull llama2
```

### Start Ollama Server

```bash
# In a separate terminal
ollama serve
```

### Run the Backend Server

```bash
# Start Flask server
python app.py
```

Server will start at: `http://localhost:5000`

## 🧪 Testing the API

### Test Health Endpoint

```bash
curl http://localhost:5000/health
```

Expected response:

```json
{
  "status": "healthy",
  "service": "theophysics-backend",
  "version": "1.0.0"
}
```

### Test Fruits of Spirit API

```bash
# Get all fruits
curl http://localhost:5000/api/fruits-of-spirit/

# Get specific fruit
curl http://localhost:5000/api/fruits-of-spirit/name/Love

# Get physics mappings
curl http://localhost:5000/api/fruits-of-spirit/physics-mapping

# Get random fruit
curl http://localhost:5000/api/fruits-of-spirit/random
```

### Test Definition API

```bash
# Check status
curl http://localhost:5000/api/definitions/status

# Get template
curl http://localhost:5000/api/definitions/template

# Chat (requires Ollama running)
curl -X POST http://localhost:5000/api/definitions/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is coherence?"}'
```

### Test CLI Tools

```bash
# Interactive chat
python scripts/definition_cli.py chat

# Extract definitions
python scripts/definition_cli.py extract sample.md

# Run examples
python examples/definition_example.py
```

## 🌐 Production Deployment Options

### Option 1: Heroku

```bash
# Install Heroku CLI
# Create Procfile
echo "web: python app.py" > Procfile

# Create runtime.txt
echo "python-3.11.0" > runtime.txt

# Deploy
heroku create theophysics-backend
git push heroku main
```

### Option 2: Railway

1. Visit https://railway.app
2. Connect GitHub repository
3. Deploy automatically
4. Set environment variables:
   - `PORT=5000`
   - `FLASK_ENV=production`

### Option 3: DigitalOcean App Platform

1. Visit https://cloud.digitalocean.com/apps
2. Create new app from GitHub
3. Select repository
4. Configure:
   - Build Command: `pip install -r requirements.txt`
   - Run Command: `python app.py`

### Option 4: Docker

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "app.py"]
```

Build and run:

```bash
docker build -t theophysics-backend .
docker run -p 5000:5000 theophysics-backend
```

## 🔐 Environment Variables

Create `.env` file:

```bash
# Flask
FLASK_ENV=production
PORT=5000

# Ollama
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=llama2

# CORS (if needed)
CORS_ORIGINS=*
```

## 📊 Monitoring & Logs

### View Logs

```bash
# Local development
# Logs appear in terminal

# Production (Heroku)
heroku logs --tail

# Production (Railway)
# View in Railway dashboard

# Docker
docker logs <container_id>
```

### Health Checks

Set up monitoring to ping:

- `GET /health` - Every 5 minutes
- Expected: 200 OK with `{"status": "healthy"}`

## 🔄 Updating the Deployment

```bash
# Make changes locally
git add .
git commit -m "Update: description of changes"
git push origin main

# For Heroku
git push heroku main

# For Railway/DigitalOcean
# Automatic deployment on push
```

## 🐛 Troubleshooting

### Issue: Ollama not connecting

```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Restart Ollama
ollama serve
```

### Issue: Port already in use

```bash
# Change port
export PORT=5001
python app.py

# Or kill process on port 5000
# Windows:
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Mac/Linux:
lsof -ti:5000 | xargs kill
```

### Issue: Module not found

```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Issue: CORS errors

```bash
# Install flask-cors
pip install flask-cors

# Already configured in app.py
```

## 📈 Performance Optimization

### Enable Caching

```python
# Add to app.py
from flask_caching import Cache

cache = Cache(app, config={'CACHE_TYPE': 'simple'})

@app.route('/api/fruits-of-spirit/')
@cache.cached(timeout=300)
def get_fruits():
    # ...
```

### Use Production Server

```bash
# Install gunicorn
pip install gunicorn

# Run with gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Database for Definitions

Consider moving from JSON to PostgreSQL for large datasets:

```python
# Use existing db_engine from main.py
# Store definitions in database instead of files
```

## 🎯 Next Steps After Deployment

1. **Test all endpoints** - Use Postman or curl
2. **Set up monitoring** - Use UptimeRobot or similar
3. **Configure domain** - Point custom domain to deployment
4. **Add authentication** - If needed for private API
5. **Enable HTTPS** - Most platforms do this automatically
6. **Document API** - Consider Swagger/OpenAPI
7. **Set up CI/CD** - Automated testing on push

## 📞 Support

If you encounter issues:

1. Check logs first
2. Verify all dependencies installed
3. Ensure Ollama is running (for AI features)
4. Check GitHub Issues
5. Review documentation

## ✅ Deployment Complete!

Your Theophysics Backend is now live and ready to serve:

- ✅ Definition processing with AI
- ✅ Fruits of Spirit API
- ✅ Cross-domain mappings
- ✅ Full REST API
- ✅ CLI tools

**API Base URL**: `http://your-deployment-url.com`

Test it:

```bash
curl http://your-deployment-url.com/health
curl http://your-deployment-url.com/api/fruits-of-spirit/
```

🎉 **Congratulations!** Your backend is deployed and operational.
