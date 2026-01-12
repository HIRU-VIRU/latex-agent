# LaTeX Resume Agent

A **JD-Aware, GitHub-Grounded LaTeX Resume Generation** system. Generate ATS-friendly LaTeX resumes that highlight your real projects and match them perfectly to job descriptions. 

**No hallucinations - everything is grounded to your actual stored data.**

## 🚀 Features

- **GitHub OAuth Integration**: Authenticate with GitHub and import projects automatically
- **Job Description Ranking**: Projects are ranked by relevance to job description keywords
- **Smart Project Selection**: Automatically selects top 3 most relevant projects per resume
- **AI-Powered LaTeX Generation**: Uses Google Gemini to generate professional LaTeX resumes
- **Online LaTeX Compilation**: Cloud-based compilation (no Docker required!)
- **One-Page Optimization**: AI enforces single-page resumes with concise bullet points
- **Full Profile Integration**: Auto-populates user profile data (education, contact, skills)
- **Anti-Hallucination**: Strict grounding rules - removes sections with placeholders

## 🏗️ Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Next.js 14    │────▶│   FastAPI       │────▶│   SQLite DB     │
│   Frontend      │     │   Backend       │     │   + ChromaDB    │
└─────────────────┘     └────────┬────────┘     └─────────────────┘
                                 │
                    ┌────────────┼────────────┐
                    ▼            ▼            ▼
              ┌──────────┐ ┌──────────┐ ┌──────────────┐
              │ Gemini   │ │  GitHub  │ │ latex.ytotech│
              │ 2.5 Flash│ │   API    │ │ .com (LaTeX) │
              └──────────┘ └──────────┘ └──────────────┘
```

## 📋 Prerequisites

- Python 3.10+ with `venv` support
- Node.js 18+ and npm
- Docker & Docker Compose (for production)
- Git
- Google Gemini API key (free tier works!)
- GitHub OAuth App (for authentication)

## 🚀 Quick Start

### Development Setup

#### 1. Clone the Repository

```bash
git clone https://github.com/HIRU-VIRU/latex-agent.git
cd latex-agent
```

### 2. Setup Backend

```bash
cd backend
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt
```

Create `backend/.env` file:

```env
# Database
DATABASE_URL=sqlite:///./latex_agent.db

# JWT Secret (generate with: python -c "import secrets; print(secrets.token_urlsafe(32))")
JWT_SECRET=your-super-secret-jwt-key-here

# Gemini API (get free key from: https://makersuite.google.com/app/apikey)
GEMINI_API_KEY=your-gemini-api-key

# GitHub OAuth (create app at: https://github.com/settings/developers)
GITHUB_CLIENT_ID=your-github-client-id
GITHUB_CLIENT_SECRET=your-github-client-secret
GITHUB_CALLBACK_URL=http://localhost:3000/api/auth/callback/github

# Encryption key for storing GitHub tokens
FERNET_KEY=generate-with-python-cryptography-fernet
```

Start the backend:

```bash
uvicorn app.main:app --reload --port 8000
```

### 3. Setup Frontend

The backend uses:
- **FastAPI**: Modern Python web framework
- **SQLAlchemy**: ORM with async support
- **SQLite**: Lightweight database (stored at `backend/latex_agent.db`)
- **ChromaDB**: Vector database for embeddings (stored at `backend/chroma_data/`)
- **aiohttp**: Async HTTP client for online LaTeX compilation
- **Google Gemini**: AI for resume generation

Key backend files:
- [`app/main.py`](backend/app/main.py) - FastAPI application entry point
- [`app/api/routes/resumes.py`](backend/app/api/routes/resumes.py) - Resume generation endpoint with project ranking
- [`app/services/resume_agent.py`](backend/app/services/resume_agent.py) - AI-powered resume generation
- [`app/services/latex_service.py`](backend/app/services/latex_service.py) - Online LaTeX compilation
- [`app/models/user.py`](backend/app/models/user.py) - User model with full profile fields

### Frontend Development

The frontend uses:
- **Next.js 14**: React framework with App Router
- **TypeScript**: Type-safe JavaScript
- **TailwindCSS**: Utility-first CSS
- **Shadcn/ui**: Beautiful UI components

Key frontend files:
- [`src/app/page.tsx`](frontend/src/app/page.tsx) - Landing page
- [`src/app/dashboard/page.tsx`](frontend/src/app/dashboard/page.tsx) - Main dashboard
- [`src/app/dashboard/profile/page.tsx`](frontend/src/app/dashboard/profile/page.tsx) - User profile editor
- [`src/lib/api.ts`](frontend/src/lib/api.ts) - API client with authentication 5. First Time Usage

1. Go to http://localhost:3000
2. Click "Sign in with GitHub"
3. Authorize the application
4. Your profile will be created automatically
5. Go to Profile page to complete your information
6. Import your GitHub projects
7. Create a job description
8. Generate your first resume!

## 🛠️ Development

### Backend Development

```bash
cd backend
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend Development

```bash
cd frontend
npm install
npm run dev
```

## 📚 API Endpoints

### Authentication
- `POST /api/auth/register` - Create account
- `POST /api/auth/login` - Login
- `GET /api/auth/me` - Get profile
- `GET /api/auth/github` - GitHub OAuth

### Projects
- `GET /api/projects` - List projects
- `POST /api/projects` - Create project
- `POST /api/projects/import/github` - Import from GitHub
- `POST /api/projects/{id}/sync` - Sync with GitHub

### Job Descriptions
- `GET /api/jobs` - List JDs
- `POST /api/jobs` - Create JD
- `POST /api/jobs/{id}/analyze` - Analyze and match projects

### Templates
- `GET /api/templates` - List templates
- `GET /api/templates/system` - Get system templates
- `POST /api/templates` - Create template

### Resumes
- `GET /api/resumes` - List resumes
- `POSTI-Powered Resume Generation

### Anti-Hallucination System

The resume agent enforces strict grounding rules:

1. **Projects**: Only top 3 projects ranked by JD relevance
2. **Skills**: Only from your stored profile data
3. **Experience**: Auto-removed if no work experience data exists
4. **Placeholders**: Automatically removed from final LaTeX
5. **One-Page Constraint**: AI enforces single-page format
6. **Concise Bullets**: Exactly 3 bullet points per project (max 80-100 chars each)

### How Project Ranking Works

When you generate a resume:
1. System loads job description keywords
2. Compares JD keywords with project descriptions, titles, and technologies
3. Scores each project by keyword overlap
4. Selects top 3 highest-scoring projects
5. AI tailors descriptions to highlight relevant skills

### LaTeX Compilation

- Uses **latex.ytotech.com** API for cloud compilation
- No Docker or local TeX installation required
- Validates LaTeX syntax (balanced braces, proper escaping)
- Returns compilation errors with detailed logs for debugging
- Sandboxed LaTeX compilation
- Rate limiting
- Input validation

## 🤖 Anti-Hallucination Guarantees

The resume agent enforces strict grounding rules:

1. **Projects**: Only sourced from your GitHub or manual uploads
2. **Skills**: Extracted from your actual codebase
3. **Descriptions**: Reworded but never fabricated
4. **Metrics**: Only stated if provided in source data
5. **Traceability**: Full audit trail to source documents

## 📁 Project Structure

```
latex-agent/
├── backend/
│   ├── app/
│   Backend Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `DATABASE_URL` | SQLite database path | Yes | `sqlite:///./latex_agent.db` |
| `JWT_SECRET` | JWT signing key | Yes | - |
| `GEMINI_API_KEY` | Google Gemini API key | Yes | - |
| `GITHUB_CLIENT_ID` | GitHub OAuth app ID | Yes | - |
| `GITHUB_CLIENT_SECRET` | GitHub OAuth secret | Yes | - |
| `GITHUB_CALLBACK_URL` | OAuth callback URL | Yes | `http://localhost:3000/api/auth/callback/github` |
| `FERNET_KEY` | Encryption key for tokens | Yes | - |

### Frontend Environment Variables

Create `frontend/.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
GITHUB_CLIENT_ID=your-github-client-id
GITHUB_CLIENT_SECRET=your-github-client-secret
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=your-nextauth-secret
```
│   │   ├── hooks/           # Custom hooks
│   │ Project Ranking Algorithm

The system uses keyword-based relevance scoring:

1. **Extract Keywords**: From job description (title, description, required_skills)
2. **Project Keywords**: From project (title, description, technologies)
3. **Overlap Calculation**: Count matching keywords (case-insensitive)
4. **Sort by Score**: Highest overlap = most relevant
5. **Top 3 Selection**: Only top 3 projects included in resume

Example:
```python
JD Keywords: ["python", "fastapi", "react", "typescript", "docker"]
Project A: ["python", "fastapi", "postgresql"] → Score: 2
Project B: ["react", "typescript", "nextjs"] → Score: 2
Project C: ["java", "spring", "mongodb"] → Score: 0
Result: Projects A and B ranked highest
```

## 🎨 LaTeX Templates

One built-in system template:

1. **Base Professional** - Comprehensive ATS-optimized resume template with all sections

Users can create and upload their own custom templates as needed.

Templates use placeholder syntax: `{{placeholder_name}}`

## 🔧 Configuration

##**Unbalanced braces**: System validates and logs brace count
- **Special characters**: Ensure proper LaTeX escaping (`&`, `%`, `$`, etc.)
- **Review logs**: Check backend terminal for detailed compilation errors
- **Online compiler down**: latex.ytotech.com may be temporarily unavailable

### GitHub OAuth Not Working
1. Verify `GITHUB_CLIENT_ID` and `GITHUB_CLIENT_SECRET` are correct
2. Check callback URL matches GitHub app settings: `http://localhost:3000/api/auth/callback/github`
3. Ensure GitHub app has correct scopes: `read:user`, `user:email`, `repo`

### "Missing required field" Errors
- These indicate AI tried to generate placeholders for missing data
- System automatically removes sections with placeholders
- Update your profile with complete information to avoid empty sections

### Database Issues
```bash
# Reset database (WARNING: deletes all data)
rm backend/latex_agent.db
rm -rf backend/chroma_data/

# Restart backend - database will be recreated
cd backend
uvicorn app.main:app --reload
```

### Port Already in Use
```bash
# Find process using port 8000
netstat -ano | findstr :8000  # Windows
lsof -i :8000                 # macOS/Linux

# Kill the process or change port
uvicorn app.main:app --reload --port 8001
## 📈 Matching Engine

The matching engine uses multi-signal scoring:

- **50%** Semantic similarity (embeddings)
- **30%** Technology overlap
- **15%** Keyword matching
- **5%** Recency boost

## � Production Deployment

### Using Docker (Recommended)

```bash
# 1. Setup environment files
./setup_production.sh  # or manually copy .env.example files

# 2. Build and run with Docker Compose
docker-compose up --build -d

# 3. Check logs
docker-compose logs -f backend
docker-compose logs -f frontend

# 4. Stop services
docker-compose down
```

### Hosting Platform Recommendations

**Best Free Options:**
1. **Railway.app** ⭐ (Recommended)
   - Supports Docker Compose natively
   - 500 hours/month free tier
   - Auto-deploy from GitHub
   - Built-in environment variables

2. **Render.com**
   - Free web services
   - Auto-deploy from GitHub
   - Built-in PostgreSQL

3. **Fly.io**
   - Docker-first platform
   - Generous free tier
   - Global edge network

### Deployment Checklist

- [ ] Generate secure JWT secret: `python -c "import secrets; print(secrets.token_urlsafe(32))"`
- [ ] Update GitHub OAuth callback URL to production domain
- [ ] Set all environment variables in hosting platform
- [ ] Update `NEXT_PUBLIC_API_URL` and `NEXT_PUBLIC_APP_URL` in frontend
- [ ] Test Docker build locally: `docker-compose up --build`
- [ ] Verify `.env` is in `.gitignore`

**📖 For detailed deployment instructions, see [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)**

---

## �🐛 Troubleshooting

### LaTeX Compilation Fails
- Check for special characters in text
- Verify template syntax
- Review compilation log in response

### API Rate Limits
- The system rotates through 6 API keys automatically
- If all are exhausted, wait and retry

### Database Connection
```bash
docker-compose logs postgres
```

## 📄 License

MIT License - see LICENSE file

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

Built with ❤️ using FastAPI, Next.js, and Gemini AI
