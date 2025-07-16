# JobScryper - Hybrid Web Application

## Overview
JobScryper has been converted from a Streamlit application to a modern hybrid web app with:
- **Frontend**: Next.js + React + Tailwind CSS + Shadcn/UI
- **Backend**: FastAPI + Python (existing JobScryper logic)
- **Architecture**: Frontend calls backend via HTTP API

## Project Structure
```
Auto Applyer/
├── job-frontend/          # Next.js React frontend
│   ├── src/
│   │   ├── app/          # Next.js app routes
│   │   │   ├── page.tsx  # Dashboard
│   │   │   ├── upload/   # Resume upload
│   │   │   ├── match/    # Job matching
│   │   │   ├── analytics/# Analytics
│   │   │   └── settings/ # Settings
│   │   ├── components/   # Reusable components
│   │   └── lib/          # API client & utilities
│   ├── package.json
│   └── .env.local
├── backend/              # FastAPI backend
│   ├── main.py          # FastAPI application
│   ├── start.py         # Backend startup script
│   └── requirements.txt
├── start_app.py         # Run both frontend & backend
└── [existing files]     # Original JobScryper modules
```

## Quick Start

### 1. Install Dependencies

**Frontend:**
```bash
cd job-frontend
npm install
```

**Backend:**
```bash
cd backend
pip install -r requirements.txt
```

### 2. Start the Application

**Option 1: Start both services at once**
```bash
python start_app.py
```

**Option 2: Start services separately**

Backend:
```bash
cd backend
python start.py
# or
python -m uvicorn main:app --reload --port 8000
```

Frontend:
```bash
cd job-frontend
npm run dev
```

### 3. Access the Application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## Features

### Pages
- **Dashboard**: Overview with metrics and quick actions
- **Upload Resume**: Drag & drop resume analysis with ATS scoring
- **Job Matching**: Search jobs with filters and match scoring
- **Analytics**: Charts and metrics for job application tracking
- **Settings**: User preferences and theme settings

### API Endpoints
- `POST /api/resume` - Analyze resume for ATS optimization
- `GET /api/match` - Search for job matches
- `GET /api/applications` - Get user's job applications
- `POST /api/applications` - Create new job application
- `GET /api/analytics` - Get user analytics data

### Modern UI Features
- Responsive design (mobile-first)
- Dark/light mode toggle
- Professional SaaS-style interface
- Interactive charts (Recharts)
- Modern component library (Shadcn/UI)
- Icon support (Lucide React)

## Development

### Frontend Development
```bash
cd job-frontend
npm run dev      # Start development server
npm run build    # Build for production
npm run lint     # Run linting
```

### Backend Development
```bash
cd backend
python main.py   # Start with auto-reload
```

### Environment Variables
Create `job-frontend/.env.local`:
```
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME=JobScryper
NEXT_PUBLIC_APP_VERSION=2.0.0
```

## Integration with Existing Code

The FastAPI backend integrates with existing JobScryper modules:
- `resume_parser.py` - Resume parsing functionality
- `jobspy_wrapper.py` - Job search via JobSpy
- `alternative_sources.py` - Alternative job sources
- `matcher.py` - Job matching logic
- `database/` - Database operations

## API Client

The frontend uses a centralized API client (`src/lib/api.ts`) that handles:
- HTTP requests with axios
- Authentication tokens
- Error handling
- Type safety with TypeScript

## CORS Configuration

The backend includes CORS middleware to allow requests from:
- http://localhost:3000 (Next.js dev server)
- http://localhost:3001 (alternative port)

## Deployment

### Production Build
```bash
# Frontend
cd job-frontend
npm run build
npm start

# Backend
cd backend
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Docker (Optional)
Create `docker-compose.yml` for containerized deployment with both services.

## Troubleshooting

### Common Issues
1. **Port conflicts**: Change ports in startup scripts if needed
2. **CORS errors**: Ensure backend CORS settings include frontend URL
3. **Module import errors**: Check Python path and dependencies
4. **Build errors**: Verify Node.js version and dependencies

### Logs
- Backend logs: Console output from uvicorn
- Frontend logs: Browser console and terminal output

## Next Steps

1. **Authentication**: Add user authentication system
2. **Database**: Connect to actual database instead of mock data
3. **Testing**: Add unit and integration tests
4. **Deployment**: Set up CI/CD pipeline
5. **Monitoring**: Add logging and monitoring
6. **Performance**: Optimize API responses and caching 