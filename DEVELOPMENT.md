# Development Guide

This guide helps developers get started with AgentHire development.

## 🚀 Quick Start

### Automated Setup
```bash
# Unix/Linux/macOS
./setup.sh

# Windows
setup.bat
```

### Manual Setup
```bash
# 1. Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Install frontend dependencies
cd frontend && npm install && cd ..

# 4. Install root dependencies
npm install
```

## 🏃‍♂️ Running the Application

### Development Mode
```bash
# Option 1: Run all services with one command
npm run dev

# Option 2: Run services separately
npm run backend    # Python backend
npm run frontend   # React frontend
npm run sandbox    # Job portal (optional)
```

### Individual Services
```bash
# Backend only
python run.py

# Frontend only
cd frontend && npm run dev

# Sandbox portal
python sandbox/job_portal.py
```

## 🏗️ Project Architecture

### Backend Structure
```
backend/
├── app.py              # FastAPI main application
├── auth.py             # Authentication & JWT
├── database.py         # Database models & connection
├── models.py           # Data models
├── ai_agents.py        # AI job matching logic
├── engine.py           # Core application engine
├── scheduler.py        # Background tasks
└── artifact_services.py # File handling
```

### Frontend Structure
```
frontend/src/
├── components/         # Reusable components
│   ├── AuthContext.jsx # Authentication context
│   └── ui/            # UI components
├── pages/             # Page components
│   ├── Dashboard.jsx  # Main dashboard
│   ├── EditProfile.jsx # Profile management
│   ├── JobListings.jsx # Job browsing
│   ├── Login.jsx      # Authentication
│   └── ...
├── api.js             # API client
├── App.jsx            # Main app component
└── index.css          # Global styles
```

### Core Modules
```
core/
├── generator.py       # Profile generation
├── scorer.py          # Job scoring algorithms
├── tracker.py         # Application tracking
└── validator.py       # Data validation
```

## 🔧 Development Workflow

### Making Changes

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Backend: Modify Python files in `backend/` or `core/`
   - Frontend: Modify React components in `frontend/src/`
   - Styles: Update `frontend/src/index.css`

3. **Test your changes**
   ```bash
   # Test backend
   python -m pytest

   # Test frontend
   cd frontend && npm test
   ```

4. **Commit and push**
   ```bash
   git add .
   git commit -m "feat: add your feature description"
   git push origin feature/your-feature-name
   ```

### Code Style

#### Python
- Follow PEP 8
- Use type hints
- Write docstrings
- Use meaningful names

#### JavaScript/React
- Use ES6+ features
- Follow React best practices
- Use hooks over class components
- Keep components small and focused

#### CSS
- Use Tailwind CSS utilities
- Follow the design system in `index.css`
- Maintain responsive design

## 🧪 Testing

### Backend Testing
```bash
# Run all tests
python -m pytest

# Run specific test file
python -m pytest tests/test_auth.py

# Run with coverage
python -m pytest --cov=backend
```

### Frontend Testing
```bash
cd frontend

# Run tests
npm test

# Run tests with coverage
npm run test:coverage
```

## 🐛 Debugging

### Backend Debugging
- Use `print()` statements or `logging`
- Check logs in console output
- Use Python debugger: `import pdb; pdb.set_trace()`

### Frontend Debugging
- Use browser developer tools
- Check console for errors
- Use React Developer Tools extension

### Common Issues

1. **Port conflicts**: Change ports in configuration
2. **Database issues**: Delete database files and restart
3. **Node modules**: Delete `node_modules` and reinstall
4. **Python environment**: Recreate virtual environment

## 📊 Database

### Schema
- SQLite database stored in `data/` directory
- Models defined in `backend/models.py`
- Database operations in `backend/database.py`

### Migrations
```bash
# Reset database (development only)
rm -rf data/
python run.py  # Will recreate tables
```

## 🔌 API Endpoints

### Authentication
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `POST /api/auth/logout` - User logout

### Profile Management
- `GET /api/profile/get` - Get user profile
- `POST /api/profile/save` - Save user profile
- `POST /api/profile/upload-resume` - Upload resume

### Job Management
- `GET /api/jobs/list` - Get job listings
- `GET /api/jobs/ai-ranked` - Get AI-ranked jobs

### Autopilot
- `POST /api/autopilot/start` - Start AI job applications
- `GET /api/autopilot/status/{run_id}` - Get run status

## 🎨 Design System

### Colors
- Primary: Purple to Indigo gradient
- Secondary: Pink to Red gradient
- Success: Blue to Cyan gradient
- Warning: Green to Teal gradient
- Danger: Pink to Yellow gradient

### Components
- Cards: White background with soft shadows
- Buttons: Gradient backgrounds with hover effects
- Inputs: Modern styling with focus states
- Badges: Colored backgrounds for status indicators

## 📱 Responsive Design

### Breakpoints
- `sm`: 640px and up
- `md`: 768px and up
- `lg`: 1024px and up
- `xl`: 1280px and up

### Mobile-First Approach
- Design for mobile first
- Use responsive utilities
- Test on different screen sizes

## 🚀 Deployment

### Production Build
```bash
# Build frontend
npm run build

# Frontend files will be in frontend/dist/
```

### Environment Variables
Create `.env` file:
```env
DATABASE_URL=sqlite:///./data/app.db
JWT_SECRET_KEY=your-secret-key
API_HOST=0.0.0.0
API_PORT=8000
FRONTEND_URL=http://localhost:5173
```

## 📚 Resources

- [React Documentation](https://reactjs.org/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)

## 🤝 Getting Help

- Check existing issues on GitHub
- Ask questions in discussions
- Review the codebase for examples
- Reach out to maintainers

Happy coding! 🚀