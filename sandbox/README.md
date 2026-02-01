# Sandbox Job Portal

This directory contains the sandbox job portal components for testing and demonstration.

## Files

### `job_portal.py` - Full Web Portal
A comprehensive Flask-based job portal with:
- **100+ realistic job postings** across 13+ companies
- **Complete web interface** with job browsing, detailed job pages, and application forms
- **Company profiles** with benefits, culture info, and detailed descriptions
- **Application management** with tracking and receipts
- **RESTful API** for automation and integration
- **Responsive design** that works on all devices

**Usage:**
```bash
# Install dependencies
pip install flask flask-cors

# Run the portal
python sandbox/job_portal.py
```

**Access:**
- Web Interface: http://localhost:5001
- API Endpoints: http://localhost:5001/api/*

### `portal.py` - Simple API Simulator
A lightweight Python class for basic job application simulation:
- Simple application submission API
- Deterministic receipt generation
- 5% random failure rate for testing
- Used by the backend for integration testing

**Usage:**
```python
from sandbox.portal import SandboxJobPortal

portal = SandboxJobPortal()
result = portal.submit_application({
    "job_id": "job-001",
    "student_id": "user123",
    "content": {"name": "John Doe", "email": "john@example.com"}
})
```

## Features

### Job Portal Features
- **Realistic Job Data**: 100+ jobs with detailed descriptions, requirements, and company info
- **Advanced Search**: Filter by job type, location, experience level, and keywords
- **Application Forms**: Comprehensive forms with validation and file upload
- **Company Profiles**: Detailed company information with benefits and culture
- **Application Tracking**: View and manage all submitted applications
- **Mobile Responsive**: Works perfectly on desktop, tablet, and mobile

### API Endpoints
- `GET /api/jobs` - List all jobs
- `GET /api/jobs/<job_id>` - Get job details
- `POST /api/jobs/<job_id>/apply` - Submit application
- `GET /api/applications` - List applications
- `GET /api/companies` - List companies
- `GET /api/portal/status` - Portal status

## Integration

The sandbox portal integrates with the main AgentHire application:
1. **Backend Integration**: The main backend calls the sandbox API for job data
2. **AI Job Matching**: AI agents analyze jobs from the sandbox portal
3. **Automated Applications**: The autopilot system submits applications to the sandbox
4. **Status Tracking**: Application status is tracked and displayed in the main dashboard

## Development

The sandbox portal is designed to:
- **Simulate Real Job Portals**: Provides realistic job data and application flows
- **Test AI Agents**: Allows testing of job matching and application automation
- **Demo Purposes**: Showcases the complete job application workflow
- **Development Testing**: Provides a controlled environment for testing features

## Data

All data is stored in memory and resets when the portal restarts. This includes:
- Job listings and details
- Company profiles and information
- Application submissions and tracking
- Portal statistics and metrics

Perfect for development and demonstration without persistent storage concerns.