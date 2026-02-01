# AgentHire - AI-Powered Job Application System

A modern, full-stack web application that uses AI to automatically find, analyze, and apply to jobs based on your profile and preferences.

## 🚀 Features

### ✨ Core Functionality
- **AI-Powered Job Matching**: Intelligent job analysis and ranking based on your profile
- **Automated Applications**: AI applies to suitable jobs automatically
- **Profile Management**: Comprehensive profile system with constraints and preferences
- **Resume Processing**: Upload and extract text from PDF, Word, and text files
- **Application Tracking**: Complete history and status tracking of all applications
- **Real-time Dashboard**: Monitor AI runs, application statistics, and job matches

### 🎨 Modern UI/UX
- **Beautiful Design**: Modern gradient-based design with smooth animations
- **Responsive Layout**: Works perfectly on desktop, tablet, and mobile
- **Interactive Components**: Hover effects, transitions, and micro-interactions
- **Dark/Light Themes**: Gradient backgrounds with excellent contrast
- **Accessibility**: Proper color contrast and keyboard navigation

### 🤖 AI Features
- **Smart Job Analysis**: AI evaluates job compatibility with your profile
- **Constraint Respect**: Honors your location, salary, and company preferences
- **Match Scoring**: Provides detailed match scores and reasoning
- **Automated Decision Making**: Decides which jobs to apply to automatically
- **Learning System**: Improves recommendations based on your preferences

## 🏗️ Architecture

### Frontend (React + Vite)
- **Framework**: React 18 with modern hooks
- **Styling**: Tailwind CSS with custom design system
- **Routing**: React Router for SPA navigation
- **State Management**: Context API for authentication
- **Build Tool**: Vite for fast development and building

### Backend (Python + FastAPI)
- **Framework**: FastAPI for high-performance API
- **Database**: SQLite with SQLAlchemy ORM
- **Authentication**: JWT-based secure authentication
- **AI Integration**: Custom AI agents for job matching
- **File Processing**: PDF/Word resume parsing

### Key Components
- **AI Agents**: Job analysis and application automation
- **Profile System**: Comprehensive user profile management
- **Job Portal Integration**: Sandbox job portal for testing
- **Application Engine**: Automated job application system

## 📁 Project Structure

```
├── frontend/                 # React frontend application
│   ├── src/
│   │   ├── components/      # Reusable React components
│   │   ├── pages/          # Page components
│   │   ├── api.js          # API client
│   │   └── index.css       # Global styles and design system
│   ├── package.json        # Frontend dependencies
│   └── vite.config.js      # Vite configuration
├── backend/                 # Python FastAPI backend
│   ├── app.py             # Main FastAPI application
│   ├── auth.py            # Authentication system
│   ├── database.py        # Database models and connection
│   ├── ai_agents.py       # AI job matching agents
│   └── models.py          # Data models
├── core/                   # Core business logic
│   ├── generator.py       # Profile generation
│   ├── scorer.py          # Job scoring algorithms
│   ├── tracker.py         # Application tracking
│   └── validator.py       # Data validation
├── schemas/               # Data schemas and validation
├── sandbox/               # Sandbox job portal for testing
├── requirements.txt       # Python dependencies
├── package.json          # Node.js dependencies (root)
└── README.md             # This file
```

## 🚀 Quick Start

### Prerequisites
- **Python 3.8+**
- **Node.js 16+**
- **npm or yarn**

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/agenthire.git
   cd agenthire
   ```

2. **Set up Python backend**
   ```bash
   # Create virtual environment
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   
   # Install dependencies
   pip install -r requirements.txt
   ```

3. **Set up React frontend**
   ```bash
   cd frontend
   npm install
   cd ..
   ```

4. **Install root dependencies** (for development tools)
   ```bash
   npm install
   ```

### Running the Application

1. **Start the backend server**
   ```bash
   # Activate virtual environment
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   
   # Run the backend
   python run.py
   ```
   Backend will be available at `http://localhost:8000`

2. **Start the frontend development server**
   ```bash
   cd frontend
   npm run dev
   ```
   Frontend will be available at `http://localhost:5173`

3. **Start the sandbox job portal** (optional, for testing)
   ```bash
   python sandbox/job_portal.py
   ```
   Sandbox portal will be available at `http://localhost:5001`

## 📖 Usage Guide

### 1. **Account Setup**
- Register a new account or login
- Complete your profile with skills, education, and experience
- Set your job preferences and constraints

### 2. **Resume Upload**
- Upload your resume (PDF, Word, or text format)
- AI will extract and analyze the content
- Review and edit the generated profile

### 3. **Job Matching**
- AI automatically finds and analyzes available jobs
- View match scores and AI reasoning for each job
- Browse job listings with detailed compatibility analysis

### 4. **Automated Applications**
- Set your application constraints (location, salary, etc.)
- Run the AI autopilot to apply to suitable jobs automatically
- Monitor progress in real-time

### 5. **Dashboard & Tracking**
- View application history and statistics
- Track AI run results and success rates
- Manage your profile and preferences

## 🛠️ Development

### Frontend Development
```bash
cd frontend
npm run dev          # Start development server
npm run build        # Build for production
npm run preview      # Preview production build
```

### Backend Development
```bash
# Install development dependencies
pip install -r requirements.txt

# Run with auto-reload
uvicorn backend.app:app --reload --host 0.0.0.0 --port 8000
```

### Code Style
- **Frontend**: ESLint + Prettier for JavaScript/React
- **Backend**: Black + isort for Python formatting
- **CSS**: Tailwind CSS with custom design system

## � Configuration

### Environment Variables
Create a `.env` file in the root directory:
```env
# Database
DATABASE_URL=sqlite:///./data/app.db

# JWT Secret
JWT_SECRET_KEY=your-secret-key-here

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# Frontend URL (for CORS)
FRONTEND_URL=http://localhost:5173
```

### Customization
- **Design System**: Modify `frontend/src/index.css` for colors and styling
- **AI Behavior**: Adjust parameters in `backend/ai_agents.py`
- **Database Schema**: Update models in `backend/models.py`

## 🚀 Deployment

### Production Build
```bash
# Build frontend
cd frontend
npm run build

# The built files will be in frontend/dist/
```

### Docker Deployment (Optional)
```dockerfile
# Example Dockerfile structure
FROM python:3.9-slim
# ... backend setup

FROM node:16-alpine
# ... frontend build

# Combine in final image
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines
- Follow the existing code style and conventions
- Add tests for new features
- Update documentation as needed
- Ensure all tests pass before submitting

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **React Team** for the amazing frontend framework
- **FastAPI** for the high-performance backend framework
- **Tailwind CSS** for the utility-first CSS framework
- **OpenAI** for AI capabilities inspiration

## 📞 Support

If you have any questions or need help:
- Open an issue on GitHub
- Check the documentation
- Review the code examples

---

**Built with ❤️ using React, FastAPI, and AI**