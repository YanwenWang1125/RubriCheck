# RubriCheck Local Development Setup

This guide will help you run the RubriCheck application locally on your machine.

## Prerequisites

1. **Python 3.8+** with conda environment activated
2. **Node.js 16+** and npm
3. **OpenAI API Key** (get one from [OpenAI Platform](https://platform.openai.com/account/api-keys))

## Quick Start

### Option 1: Automated Setup (Recommended)

```bash
# 1. Make sure you're in the project root directory
cd /path/to/RubriCheck

# 2. Create your environment file
cp env.example .env
# Edit .env and add your OpenAI API key:
# OPENAI_API_KEY=your_actual_api_key_here

# 3. Run the automated startup script
python start_local.py
```

This will:
- ✅ Check all requirements
- ✅ Install missing dependencies
- ✅ Start the backend API server (http://localhost:8000)
- ✅ Start the frontend development server (http://localhost:5173)

### Option 2: Manual Setup

#### Backend Setup

```bash
# 1. Navigate to backend directory
cd rubricheck-backend

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Set up environment variables
# Create .env file with your OpenAI API key
echo "OPENAI_API_KEY=your_actual_api_key_here" > .env

# 4. Start the backend server
python app.py
```

The backend will start on http://localhost:8000

#### Frontend Setup

```bash
# 1. Open a new terminal and navigate to frontend directory
cd rubricheck-frontend

# 2. Install Node.js dependencies
npm install

# 3. Create environment file
cp env.example .env
# The .env file should contain:
# VITE_API_BASE_URL=http://localhost:8000

# 4. Start the frontend development server
npm run dev
```

The frontend will start on http://localhost:5173

## What You'll See

1. **Backend API Server** (http://localhost:8000)
   - Health check: http://localhost:8000/health
   - Main evaluation endpoint: http://localhost:8000/evaluate
   - Rubric parsing endpoint: http://localhost:8000/rubric/parse

2. **Frontend Web App** (http://localhost:5173)
   - Upload rubric (JSON format)
   - Paste or upload essay text
   - Get AI-powered grading results

## API Endpoints

### POST /evaluate
Main endpoint for essay evaluation.

**Request:**
```json
{
  "rubric": {
    "id": "essay-v1",
    "title": "Argumentative Essay Rubric",
    "criteria": [
      {
        "id": "thesis",
        "name": "Thesis Statement",
        "weight": 0.25,
        "levels": [
          {"name": "Excellent", "description": "Clear, arguable thesis.", "points": 4},
          {"name": "Good", "description": "Mostly clear thesis.", "points": 3},
          {"name": "Fair", "description": "Unclear or weak.", "points": 2},
          {"name": "Poor", "description": "Missing.", "points": 1}
        ]
      }
    ]
  },
  "essayText": "Your essay text here..."
}
```

**Response:**
```json
{
  "overall": {
    "numeric": 85.5,
    "letter": "A",
    "confidence": 0.85
  },
  "items": [
    {
      "criterionId": "thesis",
      "level": "Good",
      "justification": "The thesis is present but could be more specific...",
      "evidenceSpans": [{"text": "renewable energy is essential", "paraIndex": 0}],
      "suggestion": "Make your thesis more specific and arguable",
      "confidence": 0.8
    }
  ],
  "meta": {
    "essay_insights": {...},
    "essay_metadata": {...}
  }
}
```

### POST /rubric/parse
Parse rubric from uploaded file (PDF, DOCX, etc.).

**Request:** Multipart form data with file upload

**Response:** Parsed rubric in frontend format

## Troubleshooting

### Common Issues

1. **"conda activate not recognized"**
   ```bash
   conda init powershell  # For PowerShell
   # Restart terminal, then:
   conda activate rubriCheck
   ```

2. **"Flask not found"**
   ```bash
   cd rubricheck-backend
   pip install -r requirements.txt
   ```

3. **"npm not found"**
   - Install Node.js from [nodejs.org](https://nodejs.org/)

4. **"OpenAI API key not working"**
   - Check your API key in the .env file
   - Ensure you have credits in your OpenAI account
   - Verify the key format: `sk-...`

5. **Frontend can't connect to backend**
   - Make sure backend is running on port 8000
   - Check VITE_API_BASE_URL in frontend/.env
   - Try http://localhost:8000/health in browser

### Port Conflicts

If ports 8000 or 5173 are in use:

**Backend (change port 8000):**
```bash
# In .env file:
FLASK_PORT=8001
```

**Frontend (change port 5173):**
```bash
# In frontend/.env file:
VITE_API_BASE_URL=http://localhost:8001
# Then run:
npm run dev -- --port 3000
```

## Development Tips

1. **Backend Logs**: Check the terminal where you started the backend for detailed logs
2. **Frontend Hot Reload**: The frontend automatically reloads when you make changes
3. **API Testing**: Use tools like Postman or curl to test API endpoints directly
4. **Debug Mode**: Backend runs in debug mode by default (FLASK_DEBUG=True)

## File Structure

```
RubriCheck/
├── rubricheck-backend/
│   ├── app.py              # Flask API server
│   ├── requirements.txt    # Python dependencies
│   ├── rubriCheck_pipeline.py  # Main pipeline logic
│   ├── grading_engine.py   # AI grading logic
│   ├── essay_preprocessor.py  # Essay processing
│   └── rubric_parser_prompt.py  # Rubric parsing
├── rubricheck-frontend/
│   ├── src/
│   │   ├── App.tsx         # Main React app
│   │   ├── lib/api.ts      # API client
│   │   └── types.ts        # TypeScript types
│   ├── package.json        # Node.js dependencies
│   └── env.example         # Environment template
├── .env                    # Environment variables
├── .gitignore             # Git ignore rules
└── start_local.py         # Automated startup script
```

## Next Steps

Once everything is running:

1. **Test the API**: Visit http://localhost:8000/health
2. **Open the App**: Visit http://localhost:5173
3. **Upload a Rubric**: Use the JSON format shown in the frontend README
4. **Paste an Essay**: Try with sample text to see the AI grading in action
5. **Check Results**: Review the detailed feedback and scores

Happy grading! 🎓✨
