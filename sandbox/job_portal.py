#!/usr/bin/env python3
"""
Sandbox Job Portal - Realistic Job Board for Demo Environment
Simulates a real job portal with comprehensive features:
- Job listings with detailed descriptions
- Application forms with validation
- Submission receipts and tracking
- Company profiles and job categories
"""
import json
import time
import uuid
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# In-memory storage for the sandbox portal
JOBS_DB = []
APPLICATIONS_DB = []
COMPANIES_DB = []
PORTAL_STATS = {
    "total_jobs": 0,
    "total_applications": 0,
    "active_jobs": 0,
    "companies": 0
}

def initialize_sandbox_companies():
    """Initialize realistic company profiles."""
    
    companies = [
        {
            "company_id": "tech-corp-001",
            "name": "TechCorp Innovations",
            "industry": "Technology",
            "size": "500-1000 employees",
            "location": "San Francisco, CA",
            "description": "Leading technology company specializing in cloud solutions and AI.",
            "website": "https://techcorp-sandbox.com",
            "logo": "https://via.placeholder.com/100x100?text=TC",
            "benefits": ["Health Insurance", "401k", "Remote Work", "Stock Options"],
            "culture": "Fast-paced, innovative, collaborative environment"
        },
        {
            "company_id": "data-flow-002",
            "name": "DataFlow Analytics",
            "industry": "Data Science",
            "size": "100-500 employees",
            "location": "Austin, TX",
            "description": "Data analytics company helping businesses make data-driven decisions.",
            "website": "https://dataflow-sandbox.com",
            "logo": "https://via.placeholder.com/100x100?text=DF",
            "benefits": ["Health Insurance", "Flexible Hours", "Learning Budget"],
            "culture": "Data-driven, analytical, growth-focused"
        },
        {
            "company_id": "web-dev-003",
            "name": "WebDev Solutions",
            "industry": "Web Development",
            "size": "50-100 employees",
            "location": "Remote",
            "description": "Full-service web development agency creating modern web applications.",
            "website": "https://webdev-sandbox.com",
            "logo": "https://via.placeholder.com/100x100?text=WD",
            "benefits": ["Remote Work", "Flexible Schedule", "Professional Development"],
            "culture": "Creative, collaborative, client-focused"
        },
        {
            "company_id": "startup-hub-004",
            "name": "StartupHub",
            "industry": "Startup Incubator",
            "size": "10-50 employees",
            "location": "New York, NY",
            "description": "Startup incubator helping early-stage companies grow and scale.",
            "website": "https://startuphub-sandbox.com",
            "logo": "https://via.placeholder.com/100x100?text=SH",
            "benefits": ["Equity", "Mentorship", "Networking", "Flexible Hours"],
            "culture": "Entrepreneurial, fast-paced, innovative"
        },
        {
            "company_id": "cloud-tech-005",
            "name": "CloudTech Systems",
            "industry": "Cloud Computing",
            "size": "1000+ employees",
            "location": "Seattle, WA",
            "description": "Enterprise cloud infrastructure and services provider.",
            "website": "https://cloudtech-sandbox.com",
            "logo": "https://via.placeholder.com/100x100?text=CT",
            "benefits": ["Health Insurance", "401k", "Stock Options", "Gym Membership"],
            "culture": "Enterprise-focused, stable, growth-oriented"
        }
    ]
    
    global COMPANIES_DB, PORTAL_STATS
    COMPANIES_DB = companies
    PORTAL_STATS["companies"] = len(companies)
    
    print(f"✅ Initialized {len(companies)} company profiles")

def generate_additional_companies():
    """Generate more companies to support 100+ jobs."""
    
    additional_companies = [
        {
            "company_id": "fintech-solutions-006",
            "name": "FinTech Solutions",
            "industry": "Financial Technology",
            "size": "200-500 employees",
            "location": "Boston, MA",
            "description": "Revolutionary fintech company building the future of digital payments and banking.",
            "website": "https://fintech-sandbox.com",
            "logo": "https://via.placeholder.com/100x100?text=FT",
            "benefits": ["Health Insurance", "Stock Options", "401k", "Flexible Hours"],
            "culture": "Innovation-driven, fast-paced, results-oriented"
        },
        {
            "company_id": "green-energy-007",
            "name": "GreenEnergy Corp",
            "industry": "Renewable Energy",
            "size": "300-800 employees",
            "location": "Denver, CO",
            "description": "Leading renewable energy company focused on solar and wind power solutions.",
            "website": "https://greenenergy-sandbox.com",
            "logo": "https://via.placeholder.com/100x100?text=GE",
            "benefits": ["Health Insurance", "Environmental Impact", "Remote Work", "Learning Budget"],
            "culture": "Mission-driven, sustainable, collaborative"
        },
        {
            "company_id": "mobile-first-008",
            "name": "MobileFirst Apps",
            "industry": "Mobile Development",
            "size": "50-150 employees",
            "location": "Los Angeles, CA",
            "description": "Mobile app development studio creating innovative iOS and Android applications.",
            "website": "https://mobilefirst-sandbox.com",
            "logo": "https://via.placeholder.com/100x100?text=MF",
            "benefits": ["Remote Work", "Flexible Schedule", "Device Allowance", "Health Insurance"],
            "culture": "Creative, mobile-first, user-focused"
        },
        {
            "company_id": "ai-research-009",
            "name": "AI Research Labs",
            "industry": "Artificial Intelligence",
            "size": "100-300 employees",
            "location": "Palo Alto, CA",
            "description": "Cutting-edge AI research company developing next-generation machine learning solutions.",
            "website": "https://airesearch-sandbox.com",
            "logo": "https://via.placeholder.com/100x100?text=AI",
            "benefits": ["Research Budget", "Conference Attendance", "Stock Options", "Health Insurance"],
            "culture": "Research-focused, innovative, academic"
        },
        {
            "company_id": "ecommerce-plus-010",
            "name": "ECommerce Plus",
            "industry": "E-commerce",
            "size": "500-1000 employees",
            "location": "Chicago, IL",
            "description": "Major e-commerce platform serving millions of customers worldwide.",
            "website": "https://ecommerceplus-sandbox.com",
            "logo": "https://via.placeholder.com/100x100?text=EC",
            "benefits": ["Health Insurance", "Employee Discounts", "401k", "Gym Membership"],
            "culture": "Customer-focused, data-driven, scalable"
        },
        {
            "company_id": "cyber-security-011",
            "name": "CyberShield Security",
            "industry": "Cybersecurity",
            "size": "150-400 employees",
            "location": "Washington, DC",
            "description": "Cybersecurity firm protecting businesses from digital threats and vulnerabilities.",
            "website": "https://cybershield-sandbox.com",
            "logo": "https://via.placeholder.com/100x100?text=CS",
            "benefits": ["Security Clearance Bonus", "Health Insurance", "Professional Development", "Remote Work"],
            "culture": "Security-first, detail-oriented, mission-critical"
        },
        {
            "company_id": "game-studio-012",
            "name": "Pixel Game Studio",
            "industry": "Gaming",
            "size": "80-200 employees",
            "location": "Portland, OR",
            "description": "Independent game studio creating immersive gaming experiences for PC and console.",
            "website": "https://pixelgames-sandbox.com",
            "logo": "https://via.placeholder.com/100x100?text=PG",
            "benefits": ["Game Library", "Flexible Hours", "Health Insurance", "Creative Freedom"],
            "culture": "Creative, passionate, player-focused"
        },
        {
            "company_id": "health-tech-013",
            "name": "HealthTech Innovations",
            "industry": "Healthcare Technology",
            "size": "200-600 employees",
            "location": "Minneapolis, MN",
            "description": "Healthcare technology company improving patient outcomes through digital solutions.",
            "website": "https://healthtech-sandbox.com",
            "logo": "https://via.placeholder.com/100x100?text=HT",
            "benefits": ["Health Insurance", "HSA", "Wellness Programs", "Remote Work"],
            "culture": "Patient-focused, innovative, impactful"
        }
    ]
    
    return additional_companies

def initialize_sandbox_jobs():
    """Initialize the sandbox portal with 100+ realistic job postings."""
    
    global COMPANIES_DB, JOBS_DB, PORTAL_STATS
    
    # Ensure companies are initialized first
    if not COMPANIES_DB:
        initialize_sandbox_companies()
    
    # Add more companies for diversity
    additional_companies = generate_additional_companies()
    COMPANIES_DB.extend(additional_companies)
    
    sandbox_jobs = [
        {
            "job_id": "job-001",
            "company_id": "tech-corp-001",
            "company": "TechCorp Innovations",
            "role": "Software Engineer Intern",
            "department": "Engineering",
            "location": "San Francisco, CA (Remote Available)",
            "job_type": "internship",
            "experience_level": "Entry Level",
            "salary_range": "$25-30/hour",
            "posted_date": (datetime.now() - timedelta(days=2)).isoformat(),
            "deadline": (datetime.now() + timedelta(days=28)).isoformat(),
            "status": "active",
            "description": """
Join our engineering team as a Software Engineer Intern and work on cutting-edge cloud solutions.

**What you'll do:**
• Develop and maintain web applications using modern frameworks
• Collaborate with senior engineers on real-world projects
• Participate in code reviews and agile development processes
• Learn about cloud architecture and scalable systems

**What we're looking for:**
• Currently pursuing a degree in Computer Science or related field
• Experience with Python, JavaScript, or similar programming languages
• Understanding of web development fundamentals
• Strong problem-solving skills and attention to detail
• Excellent communication and teamwork abilities

**Bonus points:**
• Experience with React, Node.js, or cloud platforms
• Previous internship or project experience
• Open source contributions
            """,
            "required_skills": ["python", "javascript", "git", "web development"],
            "preferred_skills": ["react", "node.js", "aws", "docker"],
            "min_experience_years": 0,
            "application_url": "http://localhost:5001/api/jobs/job-001/apply",
            "views": random.randint(50, 200),
            "applications_count": random.randint(5, 25)
        },
        {
            "job_id": "job-002",
            "company_id": "data-flow-002", 
            "company": "DataFlow Analytics",
            "role": "Data Science Intern",
            "department": "Data Science",
            "location": "Austin, TX (Hybrid)",
            "job_type": "internship",
            "experience_level": "Entry Level", 
            "salary_range": "$22-28/hour",
            "posted_date": (datetime.now() - timedelta(days=1)).isoformat(),
            "deadline": (datetime.now() + timedelta(days=25)).isoformat(),
            "status": "active",
            "description": """
Exciting opportunity to work with big data and machine learning in a fast-paced analytics environment.

**What you'll do:**
• Analyze large datasets to extract meaningful insights
• Build predictive models using machine learning techniques
• Create data visualizations and reports for stakeholders
• Work with cross-functional teams to solve business problems

**What we're looking for:**
• Currently pursuing a degree in Data Science, Statistics, or related field
• Experience with Python and data analysis libraries (pandas, numpy)
• Understanding of statistical concepts and machine learning basics
• Strong analytical and problem-solving skills
• Ability to communicate complex findings to non-technical audiences

**Bonus points:**
• Experience with SQL and database systems
• Knowledge of machine learning frameworks (scikit-learn, TensorFlow)
• Previous data analysis projects or internships
            """,
            "required_skills": ["python", "pandas", "machine learning", "sql", "statistics"],
            "preferred_skills": ["tensorflow", "tableau", "r", "spark"],
            "min_experience_years": 0,
            "application_url": "http://localhost:5001/api/jobs/job-002/apply",
            "views": random.randint(75, 250),
            "applications_count": random.randint(8, 30)
        },
        {
            "job_id": "job-003",
            "company_id": "web-dev-003",
            "company": "WebDev Solutions",
            "role": "Frontend Developer Intern",
            "department": "Development",
            "location": "Remote",
            "job_type": "internship",
            "experience_level": "Entry Level",
            "salary_range": "$20-25/hour",
            "posted_date": (datetime.now() - timedelta(days=3)).isoformat(),
            "deadline": (datetime.now() + timedelta(days=22)).isoformat(),
            "status": "active",
            "description": """
Build amazing user interfaces with React and modern web technologies in a fully remote environment.

**What you'll do:**
• Develop responsive web applications using React and modern CSS
• Collaborate with designers to implement pixel-perfect UI/UX designs
• Optimize applications for maximum speed and scalability
• Participate in code reviews and maintain high code quality standards

**What we're looking for:**
• Currently pursuing a degree in Computer Science, Web Development, or related field
• Strong proficiency in HTML, CSS, and JavaScript
• Experience with React or similar frontend frameworks
• Understanding of responsive design principles
• Eye for design and attention to detail

**Bonus points:**
• Experience with TypeScript, Next.js, or Vue.js
• Knowledge of CSS preprocessors (Sass, Less)
• Familiarity with design tools (Figma, Adobe XD)
            """,
            "required_skills": ["javascript", "react", "html", "css", "responsive design"],
            "preferred_skills": ["typescript", "nextjs", "sass", "figma"],
            "min_experience_years": 0,
            "application_url": "http://localhost:5001/api/jobs/job-003/apply",
            "views": random.randint(60, 180),
            "applications_count": random.randint(10, 35)
        },
        {
            "job_id": "job-004",
            "company_id": "startup-hub-004",
            "company": "StartupHub",
            "role": "Full Stack Developer",
            "department": "Engineering",
            "location": "New York, NY (Hybrid)",
            "job_type": "full-time",
            "experience_level": "Junior",
            "salary_range": "$70k-90k",
            "posted_date": (datetime.now() - timedelta(days=5)).isoformat(),
            "deadline": (datetime.now() + timedelta(days=30)).isoformat(),
            "status": "active",
            "description": """
Join our startup and help build the next generation of web applications from the ground up.

**What you'll do:**
• Develop both frontend and backend components of web applications
• Work directly with founders and product team to define features
• Build scalable APIs and database architectures
• Deploy and maintain applications in cloud environments

**What we're looking for:**
• 1-2 years of experience in full-stack development
• Proficiency in JavaScript/TypeScript and modern frameworks
• Experience with Node.js and database systems
• Understanding of cloud platforms and deployment processes
• Startup mindset with ability to wear multiple hats

**What we offer:**
• Competitive salary plus equity
• Direct impact on product direction
• Mentorship from experienced entrepreneurs
• Flexible work arrangements
            """,
            "required_skills": ["javascript", "react", "node.js", "mongodb", "rest apis"],
            "preferred_skills": ["typescript", "aws", "docker", "graphql"],
            "min_experience_years": 1,
            "application_url": "http://localhost:5001/api/jobs/job-004/apply",
            "views": random.randint(100, 300),
            "applications_count": random.randint(15, 45)
        },
        {
            "job_id": "job-005",
            "company_id": "cloud-tech-005",
            "company": "CloudTech Systems",
            "role": "Backend Developer",
            "department": "Platform Engineering",
            "location": "Seattle, WA (Remote Available)",
            "job_type": "full-time",
            "experience_level": "Junior",
            "salary_range": "$75k-95k",
            "posted_date": (datetime.now() - timedelta(days=4)).isoformat(),
            "deadline": (datetime.now() + timedelta(days=35)).isoformat(),
            "status": "active",
            "description": """
Build scalable backend systems using Python and modern cloud technologies.

**What you'll do:**
• Design and implement RESTful APIs and microservices
• Work with cloud infrastructure (AWS, Docker, Kubernetes)
• Optimize database performance and implement caching strategies
• Collaborate with frontend teams to deliver end-to-end features

**What we're looking for:**
• 1-3 years of backend development experience
• Strong proficiency in Python and web frameworks (Flask, Django)
• Experience with SQL databases and query optimization
• Understanding of cloud platforms and containerization
• Knowledge of software engineering best practices

**What we offer:**
• Competitive salary and comprehensive benefits
• Stock options and 401k matching
• Professional development budget
• Flexible work arrangements
            """,
            "required_skills": ["python", "flask", "sql", "rest apis", "aws"],
            "preferred_skills": ["django", "docker", "kubernetes", "redis"],
            "min_experience_years": 1,
            "application_url": "http://localhost:5001/api/jobs/job-005/apply",
            "views": random.randint(80, 220),
            "applications_count": random.randint(12, 40)
        }
    ]
    
    # Add many more diverse jobs to reach 100+
    additional_jobs = []
    
    # Generate jobs for each company
    job_templates = [
        # Tech roles
        {"role": "Senior Software Engineer", "department": "Engineering", "job_type": "full-time", "experience_level": "Senior", "salary_range": "$120k-150k", "min_experience_years": 5, "required_skills": ["python", "javascript", "react", "aws", "docker"], "preferred_skills": ["kubernetes", "terraform", "graphql"]},
        {"role": "Frontend Developer", "department": "Engineering", "job_type": "full-time", "experience_level": "Mid Level", "salary_range": "$80k-110k", "min_experience_years": 2, "required_skills": ["javascript", "react", "html", "css", "typescript"], "preferred_skills": ["nextjs", "tailwind", "figma"]},
        {"role": "Backend Developer", "department": "Engineering", "job_type": "full-time", "experience_level": "Mid Level", "salary_range": "$85k-115k", "min_experience_years": 3, "required_skills": ["python", "django", "postgresql", "rest apis", "docker"], "preferred_skills": ["redis", "celery", "aws"]},
        {"role": "Product Manager", "department": "Product", "job_type": "full-time", "experience_level": "Mid Level", "salary_range": "$100k-130k", "min_experience_years": 3, "required_skills": ["product management", "agile", "user research", "analytics"], "preferred_skills": ["jira", "figma", "sql"]},
        {"role": "Data Scientist", "department": "Data Science", "job_type": "full-time", "experience_level": "Mid Level", "salary_range": "$95k-125k", "min_experience_years": 2, "required_skills": ["python", "machine learning", "pandas", "sql", "statistics"], "preferred_skills": ["tensorflow", "pytorch", "spark"]},
        {"role": "QA Engineer", "department": "Quality Assurance", "job_type": "full-time", "experience_level": "Junior", "salary_range": "$65k-85k", "min_experience_years": 1, "required_skills": ["testing", "automation", "selenium", "python"], "preferred_skills": ["cypress", "jest", "postman"]},
        {"role": "DevOps Engineer", "department": "Infrastructure", "job_type": "full-time", "experience_level": "Mid Level", "salary_range": "$90k-120k", "min_experience_years": 3, "required_skills": ["aws", "docker", "kubernetes", "terraform", "ci/cd"], "preferred_skills": ["ansible", "prometheus", "grafana"]},
        {"role": "UX Designer", "department": "Design", "job_type": "full-time", "experience_level": "Junior", "salary_range": "$70k-90k", "min_experience_years": 1, "required_skills": ["ux design", "figma", "user research", "prototyping"], "preferred_skills": ["sketch", "adobe creative suite", "usability testing"]},
        {"role": "Security Engineer", "department": "Security", "job_type": "full-time", "experience_level": "Mid Level", "salary_range": "$100k-130k", "min_experience_years": 3, "required_skills": ["cybersecurity", "penetration testing", "network security", "python"], "preferred_skills": ["aws security", "compliance", "incident response"]},
        {"role": "Mobile Developer", "department": "Mobile", "job_type": "full-time", "experience_level": "Junior", "salary_range": "$75k-95k", "min_experience_years": 1, "required_skills": ["react native", "javascript", "mobile development", "ios"], "preferred_skills": ["swift", "kotlin", "firebase"]},
        
        {"role": "Software Engineering Intern", "department": "Engineering", "job_type": "internship", "experience_level": "Entry Level", "salary_range": "$25-35/hour", "min_experience_years": 0, "required_skills": ["python", "javascript", "git"], "preferred_skills": ["react", "sql", "aws"]},
        {"role": "Data Science Intern", "department": "Data Science", "job_type": "internship", "experience_level": "Entry Level", "salary_range": "$22-30/hour", "min_experience_years": 0, "required_skills": ["python", "pandas", "statistics"], "preferred_skills": ["machine learning", "sql", "tableau"]},
        {"role": "Product Management Intern", "department": "Product", "job_type": "internship", "experience_level": "Entry Level", "salary_range": "$20-28/hour", "min_experience_years": 0, "required_skills": ["product management", "analytics", "user research"], "preferred_skills": ["figma", "jira", "sql"]},
        {"role": "UX Design Intern", "department": "Design", "job_type": "internship", "experience_level": "Entry Level", "salary_range": "$18-25/hour", "min_experience_years": 0, "required_skills": ["ux design", "figma", "prototyping"], "preferred_skills": ["user research", "sketch", "adobe creative suite"]},
        {"role": "Marketing Intern", "department": "Marketing", "job_type": "internship", "experience_level": "Entry Level", "salary_range": "$15-22/hour", "min_experience_years": 0, "required_skills": ["marketing", "social media", "content creation"], "preferred_skills": ["google analytics", "seo", "adobe creative suite"]},
    ]
    
    # Generate jobs for each company
    job_counter = 9  # Start after existing 8 jobs
    for company in COMPANIES_DB:
        # Each company gets 6-8 jobs
        num_jobs = random.randint(6, 8)
        company_jobs = random.sample(job_templates, min(num_jobs, len(job_templates)))
        
        for job_template in company_jobs:
            job_counter += 1
            
            # Customize job based on company industry
            customized_job = job_template.copy()
            
            # Industry-specific customizations
            if company["industry"] == "Financial Technology":
                if "required_skills" in customized_job:
                    customized_job["required_skills"].extend(["fintech", "compliance"])
                customized_job["salary_range"] = increase_salary_range(customized_job["salary_range"], 1.15)
            elif company["industry"] == "Artificial Intelligence":
                if "required_skills" in customized_job:
                    customized_job["required_skills"].extend(["ai", "deep learning"])
                customized_job["salary_range"] = increase_salary_range(customized_job["salary_range"], 1.20)
            elif company["industry"] == "Gaming":
                if "required_skills" in customized_job:
                    customized_job["required_skills"].extend(["game development", "unity"])
            elif company["industry"] == "Cybersecurity":
                if "required_skills" in customized_job:
                    customized_job["required_skills"].extend(["security", "compliance"])
                customized_job["salary_range"] = increase_salary_range(customized_job["salary_range"], 1.10)
            
            # Create job description based on role
            description = generate_job_description(customized_job["role"], company["name"], company["industry"])
            
            job = {
                "job_id": f"job-{job_counter:03d}",
                "company_id": company["company_id"],
                "company": company["name"],
                "role": customized_job["role"],
                "department": customized_job["department"],
                "location": f"{company['location']} (Remote Available)" if random.choice([True, False]) else company["location"],
                "job_type": customized_job["job_type"],
                "experience_level": customized_job["experience_level"],
                "salary_range": customized_job["salary_range"],
                "posted_date": (datetime.now() - timedelta(days=random.randint(1, 30))).isoformat(),
                "deadline": (datetime.now() + timedelta(days=random.randint(20, 60))).isoformat(),
                "status": "active",
                "description": description,
                "required_skills": customized_job["required_skills"],
                "preferred_skills": customized_job.get("preferred_skills", []),
                "min_experience_years": customized_job["min_experience_years"],
                "application_url": f"http://localhost:5001/api/jobs/job-{job_counter:03d}/apply",
                "views": random.randint(20, 500),
                "applications_count": random.randint(0, 50)
            }
            
            additional_jobs.append(job)
    
    # Combine all jobs
    all_jobs = sandbox_jobs + additional_jobs
    
    JOBS_DB = all_jobs
    PORTAL_STATS["total_jobs"] = len(all_jobs)
    PORTAL_STATS["active_jobs"] = len([j for j in all_jobs if j["status"] == "active"])
    PORTAL_STATS["companies"] = len(COMPANIES_DB)
    
    print(f"✅ Initialized sandbox portal with {len(all_jobs)} realistic job postings across {len(COMPANIES_DB)} companies")

def increase_salary_range(salary_range, multiplier):
    """Increase salary range by a multiplier."""
    if "/hour" in salary_range:
        # Handle hourly rates
        parts = salary_range.replace("$", "").replace("/hour", "").split("-")
        if len(parts) == 2:
            low = int(parts[0]) * multiplier
            high = int(parts[1]) * multiplier
            return f"${int(low)}-{int(high)}/hour"
    elif "k" in salary_range:
        # Handle annual salaries
        parts = salary_range.replace("$", "").replace("k", "").split("-")
        if len(parts) == 2:
            low = int(parts[0]) * multiplier
            high = int(parts[1]) * multiplier
            return f"${int(low)}k-{int(high)}k"
    return salary_range

def generate_job_description(role, company_name, industry):
    """Generate a realistic job description based on role and company."""
    
    descriptions = {
        "Software Engineer": f"""
Join {company_name} as a Software Engineer and help build cutting-edge solutions in the {industry.lower()} space.

**What you'll do:**
• Design and develop scalable software applications
• Collaborate with cross-functional teams to deliver high-quality products
• Write clean, maintainable code following best practices
• Participate in code reviews and technical discussions
• Troubleshoot and debug complex technical issues

**What we're looking for:**
• Strong programming skills in modern languages
• Experience with software development lifecycle
• Understanding of database design and optimization
• Excellent problem-solving and analytical skills
• Strong communication and teamwork abilities

**What we offer:**
• Competitive salary and comprehensive benefits
• Opportunities for professional growth and learning
• Collaborative and innovative work environment
• Flexible work arrangements
        """,
        
        "Data Scientist": f"""
{company_name} is seeking a talented Data Scientist to extract insights from complex datasets and drive data-driven decisions.

**What you'll do:**
• Analyze large datasets to identify trends and patterns
• Build predictive models using machine learning techniques
• Create data visualizations and reports for stakeholders
• Collaborate with engineering teams to deploy models
• Present findings to technical and non-technical audiences

**What we're looking for:**
• Strong background in statistics and machine learning
• Proficiency in Python and data analysis libraries
• Experience with SQL and database systems
• Excellent analytical and problem-solving skills
• Ability to communicate complex findings clearly

**What we offer:**
• Competitive compensation package
• Access to cutting-edge tools and technologies
• Opportunities to work on impactful projects
• Professional development and conference attendance
        """,
        
        "Product Manager": f"""
Lead product strategy and execution at {company_name}, driving innovation in the {industry.lower()} industry.

**What you'll do:**
• Define product roadmap and strategy
• Gather and prioritize product requirements
• Work closely with engineering and design teams
• Conduct market research and competitive analysis
• Analyze product metrics and user feedback

**What we're looking for:**
• Experience in product management or related field
• Strong analytical and strategic thinking skills
• Excellent communication and leadership abilities
• Understanding of agile development methodologies
• Customer-focused mindset with attention to detail

**What we offer:**
• Opportunity to shape product direction
• Collaborative and fast-paced environment
• Competitive salary and equity package
• Professional growth opportunities
        """
    }
    
    # Default description for roles not specifically defined
    default_description = f"""
Join {company_name} and contribute to innovative projects in the {industry.lower()} industry.

**What you'll do:**
• Work on challenging and impactful projects
• Collaborate with talented team members
• Contribute to product development and innovation
• Learn and grow in a supportive environment
• Make a meaningful impact on our customers

**What we're looking for:**
• Relevant experience and technical skills
• Strong problem-solving abilities
• Excellent communication skills
• Team player with collaborative mindset
• Passion for learning and growth

**What we offer:**
• Competitive compensation and benefits
• Professional development opportunities
• Flexible work environment
• Innovative and collaborative culture
    """
    
    # Get description based on role keywords
    for key_role, description in descriptions.items():
        if key_role.lower() in role.lower():
            return description
    
    return default_description

# ==================== WEB INTERFACE ====================

@app.route('/')
def home():
    """Main job portal homepage."""
    html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sandbox Job Portal - Find Your Dream Job</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 1200px; margin: 0 auto; padding: 0 20px; }
        
        /* Header */
        header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 1rem 0; }
        .header-content { display: flex; justify-content: space-between; align-items: center; }
        .logo { font-size: 1.8rem; font-weight: bold; }
        .nav { display: flex; gap: 2rem; }
        .nav a { color: white; text-decoration: none; transition: opacity 0.3s; }
        .nav a:hover { opacity: 0.8; }
        
        /* Hero Section */
        .hero { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white; padding: 4rem 0; text-align: center; }
        .hero h1 { font-size: 3rem; margin-bottom: 1rem; }
        .hero p { font-size: 1.2rem; margin-bottom: 2rem; }
        .search-box { max-width: 600px; margin: 0 auto; display: flex; gap: 1rem; }
        .search-box input { flex: 1; padding: 1rem; border: none; border-radius: 5px; font-size: 1rem; }
        .search-box button { padding: 1rem 2rem; background: #333; color: white; border: none; border-radius: 5px; cursor: pointer; }
        
        /* Stats */
        .stats { background: #f8f9fa; padding: 3rem 0; }
        .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 2rem; text-align: center; }
        .stat-card { background: white; padding: 2rem; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .stat-number { font-size: 2.5rem; font-weight: bold; color: #667eea; }
        .stat-label { color: #666; margin-top: 0.5rem; }
        
        /* Jobs Section */
        .jobs-section { padding: 4rem 0; }
        .section-title { text-align: center; font-size: 2.5rem; margin-bottom: 3rem; }
        .jobs-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(350px, 1fr)); gap: 2rem; }
        .job-card { background: white; border-radius: 10px; padding: 2rem; box-shadow: 0 4px 15px rgba(0,0,0,0.1); transition: transform 0.3s; }
        .job-card:hover { transform: translateY(-5px); }
        .job-header { display: flex; justify-content: space-between; align-items: start; margin-bottom: 1rem; }
        .job-title { font-size: 1.3rem; font-weight: bold; color: #333; }
        .job-type { background: #e3f2fd; color: #1976d2; padding: 0.3rem 0.8rem; border-radius: 20px; font-size: 0.8rem; }
        .company-name { color: #667eea; font-weight: 600; margin-bottom: 0.5rem; }
        .job-location { color: #666; margin-bottom: 1rem; }
        .job-salary { font-weight: bold; color: #4caf50; margin-bottom: 1rem; }
        .job-skills { display: flex; flex-wrap: wrap; gap: 0.5rem; margin-bottom: 1rem; }
        .skill-tag { background: #f5f5f5; padding: 0.3rem 0.8rem; border-radius: 15px; font-size: 0.8rem; color: #666; }
        .job-meta { display: flex; justify-content: space-between; color: #999; font-size: 0.9rem; margin-bottom: 1rem; }
        .apply-btn { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 0.8rem 2rem; border: none; border-radius: 5px; cursor: pointer; width: 100%; font-size: 1rem; transition: opacity 0.3s; }
        .apply-btn:hover { opacity: 0.9; }
        
        /* Footer */
        footer { background: #333; color: white; padding: 2rem 0; text-align: center; }
        
        /* Responsive */
        @media (max-width: 768px) {
            .hero h1 { font-size: 2rem; }
            .search-box { flex-direction: column; }
            .jobs-grid { grid-template-columns: 1fr; }
        }
    </style>
</head>
<body>
    <header>
        <div class="container">
            <div class="header-content">
                <div class="logo">🚀 Sandbox Jobs</div>
                <nav class="nav">
                    <a href="/">Home</a>
                    <a href="/jobs">Browse Jobs</a>
                    <a href="/companies">Companies</a>
                    <a href="/applications">Applications</a>
                    <a href="/company/post-job">Post Job</a>
                    <a href="/api/portal/status">API Status</a>
                </nav>
            </div>
        </div>
    </header>

    <section class="hero">
        <div class="container">
            <h1>Find Your Dream Job</h1>
            <p>Discover amazing opportunities at top companies in our sandbox environment</p>
            <div class="search-box">
                <input type="text" placeholder="Job title, skills, or company..." id="searchInput">
                <button onclick="searchJobs()">Search Jobs</button>
            </div>
        </div>
    </section>

    <section class="stats">
        <div class="container">
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-number" id="totalJobs">{{ stats.total_jobs }}</div>
                    <div class="stat-label">Active Jobs</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number" id="totalCompanies">{{ stats.companies }}</div>
                    <div class="stat-label">Companies</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number" id="totalApplications">{{ stats.total_applications }}</div>
                    <div class="stat-label">Applications</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">100%</div>
                    <div class="stat-label">Success Rate</div>
                </div>
            </div>
        </div>
    </section>

    <section class="jobs-section">
        <div class="container">
            <h2 class="section-title">Featured Jobs</h2>
            <div class="jobs-grid" id="jobsGrid">
                <!-- Jobs will be loaded here -->
            </div>
        </div>
    </section>

    <footer>
        <div class="container">
            <p>&copy; 2026 Sandbox Job Portal. Built for demonstration purposes.</p>
        </div>
    </footer>

    <script>
        // Load jobs on page load
        document.addEventListener('DOMContentLoaded', loadJobs);

        async function loadJobs() {
            try {
                const response = await fetch('/api/jobs?limit=6');
                const data = await response.json();
                displayJobs(data.jobs);
            } catch (error) {
                console.error('Error loading jobs:', error);
            }
        }

        function displayJobs(jobs) {
            const jobsGrid = document.getElementById('jobsGrid');
            jobsGrid.innerHTML = jobs.map(job => `
                <div class="job-card">
                    <div class="job-header">
                        <div>
                            <div class="job-title">${job.role}</div>
                            <div class="company-name">${job.company}</div>
                        </div>
                        <div class="job-type">${job.job_type}</div>
                    </div>
                    <div class="job-location">📍 ${job.location}</div>
                    <div class="job-salary">💰 ${job.salary_range}</div>
                    <div class="job-skills">
                        ${job.required_skills.slice(0, 4).map(skill => 
                            `<span class="skill-tag">${skill}</span>`
                        ).join('')}
                    </div>
                    <div class="job-meta">
                        <span>👁️ ${job.views} views</span>
                        <span>📝 ${job.applications_count} applications</span>
                    </div>
                    <button class="apply-btn" onclick="viewJob('${job.job_id}')">View Details</button>
                </div>
            `).join('');
        }

        function viewJob(jobId) {
            window.open(`/jobs/${jobId}`, '_blank');
        }

        function searchJobs() {
            const query = document.getElementById('searchInput').value;
            if (query.trim()) {
                window.location.href = `/jobs?search=${encodeURIComponent(query)}`;
            }
        }

        // Allow Enter key to search
        document.getElementById('searchInput').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                searchJobs();
            }
        });
    </script>
</body>
</html>
    """
    return render_template_string(html_template, stats=PORTAL_STATS)

@app.route('/jobs')
def jobs_page():
    """Jobs listing page."""
    html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Browse Jobs - Sandbox Job Portal</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; background: #f8f9fa; }
        .container { max-width: 1200px; margin: 0 auto; padding: 0 20px; }
        
        /* Header */
        header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 1rem 0; }
        .header-content { display: flex; justify-content: space-between; align-items: center; }
        .logo { font-size: 1.8rem; font-weight: bold; }
        .nav { display: flex; gap: 2rem; }
        .nav a { color: white; text-decoration: none; transition: opacity 0.3s; }
        .nav a:hover { opacity: 0.8; }
        
        /* Main Content */
        .main-content { padding: 2rem 0; }
        .page-title { font-size: 2.5rem; margin-bottom: 2rem; text-align: center; }
        
        /* Filters */
        .filters { background: white; padding: 2rem; border-radius: 10px; margin-bottom: 2rem; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .filters-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; }
        .filter-group label { display: block; margin-bottom: 0.5rem; font-weight: 600; }
        .filter-group select, .filter-group input { width: 100%; padding: 0.8rem; border: 1px solid #ddd; border-radius: 5px; }
        
        /* Job Cards */
        .jobs-container { display: grid; grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); gap: 2rem; }
        .job-card { background: white; border-radius: 10px; padding: 2rem; box-shadow: 0 4px 15px rgba(0,0,0,0.1); transition: transform 0.3s; }
        .job-card:hover { transform: translateY(-5px); }
        .job-header { display: flex; justify-content: space-between; align-items: start; margin-bottom: 1rem; }
        .job-title { font-size: 1.4rem; font-weight: bold; color: #333; }
        .job-type { background: #e3f2fd; color: #1976d2; padding: 0.3rem 0.8rem; border-radius: 20px; font-size: 0.8rem; }
        .company-name { color: #667eea; font-weight: 600; margin-bottom: 0.5rem; }
        .job-location { color: #666; margin-bottom: 1rem; }
        .job-salary { font-weight: bold; color: #4caf50; margin-bottom: 1rem; }
        .job-description { color: #666; margin-bottom: 1rem; line-height: 1.5; }
        .job-skills { display: flex; flex-wrap: wrap; gap: 0.5rem; margin-bottom: 1rem; }
        .skill-tag { background: #f5f5f5; padding: 0.3rem 0.8rem; border-radius: 15px; font-size: 0.8rem; color: #666; }
        .job-meta { display: flex; justify-content: space-between; color: #999; font-size: 0.9rem; margin-bottom: 1rem; }
        .job-actions { display: flex; gap: 1rem; }
        .btn { padding: 0.8rem 1.5rem; border: none; border-radius: 5px; cursor: pointer; font-size: 0.9rem; transition: opacity 0.3s; }
        .btn-primary { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }
        .btn-secondary { background: #f5f5f5; color: #333; }
        .btn:hover { opacity: 0.9; }
        
        /* Loading */
        .loading { text-align: center; padding: 2rem; }
        
        /* No results */
        .no-results { text-align: center; padding: 4rem; color: #666; }
    </style>
</head>
<body>
    <header>
        <div class="container">
            <div class="header-content">
                <div class="logo">🚀 Sandbox Jobs</div>
                <nav class="nav">
                    <a href="/">Home</a>
                    <a href="/jobs">Browse Jobs</a>
                    <a href="/companies">Companies</a>
                    <a href="/applications">Applications</a>
                    <a href="/company/post-job">Post Job</a>
                    <a href="/api/portal/status">API Status</a>
                </nav>
            </div>
        </div>
    </header>

    <main class="main-content">
        <div class="container">
            <h1 class="page-title">Browse Jobs</h1>
            
            <div class="filters">
                <div class="filters-grid">
                    <div class="filter-group">
                        <label for="searchInput">Search</label>
                        <input type="text" id="searchInput" placeholder="Job title, skills, company...">
                    </div>
                    <div class="filter-group">
                        <label for="jobTypeFilter">Job Type</label>
                        <select id="jobTypeFilter">
                            <option value="">All Types</option>
                            <option value="internship">Internship</option>
                            <option value="full-time">Full-time</option>
                            <option value="part-time">Part-time</option>
                            <option value="contract">Contract</option>
                        </select>
                    </div>
                    <div class="filter-group">
                        <label for="locationFilter">Location</label>
                        <select id="locationFilter">
                            <option value="">All Locations</option>
                            <option value="remote">Remote</option>
                            <option value="san francisco">San Francisco</option>
                            <option value="austin">Austin</option>
                            <option value="new york">New York</option>
                            <option value="seattle">Seattle</option>
                        </select>
                    </div>
                    <div class="filter-group">
                        <label for="experienceFilter">Experience Level</label>
                        <select id="experienceFilter">
                            <option value="">All Levels</option>
                            <option value="entry level">Entry Level</option>
                            <option value="junior">Junior</option>
                            <option value="mid level">Mid Level</option>
                            <option value="senior">Senior</option>
                        </select>
                    </div>
                </div>
            </div>
            
            <div id="jobsContainer" class="jobs-container">
                <div class="loading">Loading jobs...</div>
            </div>
        </div>
    </main>

    <script>
        let allJobs = [];
        
        // Load jobs on page load
        document.addEventListener('DOMContentLoaded', loadJobs);
        
        // Add event listeners for filters
        document.getElementById('searchInput').addEventListener('input', filterJobs);
        document.getElementById('jobTypeFilter').addEventListener('change', filterJobs);
        document.getElementById('locationFilter').addEventListener('change', filterJobs);
        document.getElementById('experienceFilter').addEventListener('change', filterJobs);

        async function loadJobs() {
            try {
                const response = await fetch('/api/jobs');
                const data = await response.json();
                allJobs = data.jobs;
                displayJobs(allJobs);
            } catch (error) {
                console.error('Error loading jobs:', error);
                document.getElementById('jobsContainer').innerHTML = '<div class="no-results">Error loading jobs. Please try again.</div>';
            }
        }

        function filterJobs() {
            const search = document.getElementById('searchInput').value.toLowerCase();
            const jobType = document.getElementById('jobTypeFilter').value;
            const location = document.getElementById('locationFilter').value.toLowerCase();
            const experience = document.getElementById('experienceFilter').value.toLowerCase();

            const filteredJobs = allJobs.filter(job => {
                const matchesSearch = !search || 
                    job.role.toLowerCase().includes(search) ||
                    job.company.toLowerCase().includes(search) ||
                    job.required_skills.some(skill => skill.toLowerCase().includes(search));
                
                const matchesType = !jobType || job.job_type === jobType;
                const matchesLocation = !location || job.location.toLowerCase().includes(location);
                const matchesExperience = !experience || job.experience_level.toLowerCase().includes(experience);

                return matchesSearch && matchesType && matchesLocation && matchesExperience;
            });

            displayJobs(filteredJobs);
        }

        function displayJobs(jobs) {
            const container = document.getElementById('jobsContainer');
            
            if (jobs.length === 0) {
                container.innerHTML = '<div class="no-results">No jobs found matching your criteria.</div>';
                return;
            }

            container.innerHTML = jobs.map(job => `
                <div class="job-card">
                    <div class="job-header">
                        <div>
                            <div class="job-title">${job.role}</div>
                            <div class="company-name">${job.company}</div>
                        </div>
                        <div class="job-type">${job.job_type}</div>
                    </div>
                    <div class="job-location">📍 ${job.location}</div>
                    <div class="job-salary">💰 ${job.salary_range}</div>
                    <div class="job-description">${job.description.substring(0, 150)}...</div>
                    <div class="job-skills">
                        ${job.required_skills.slice(0, 5).map(skill => 
                            `<span class="skill-tag">${skill}</span>`
                        ).join('')}
                    </div>
                    <div class="job-meta">
                        <span>👁️ ${job.views} views</span>
                        <span>📝 ${job.applications_count} applications</span>
                        <span>📅 ${new Date(job.posted_date).toLocaleDateString()}</span>
                    </div>
                    <div class="job-actions">
                        <button class="btn btn-primary" onclick="viewJob('${job.job_id}')">View Details</button>
                        <button class="btn btn-secondary" onclick="applyToJob('${job.job_id}')">Quick Apply</button>
                    </div>
                </div>
            `).join('');
        }

        function viewJob(jobId) {
            window.open(`/jobs/${jobId}`, '_blank');
        }

        function applyToJob(jobId) {
            window.open(`/jobs/${jobId}/apply`, '_blank');
        }
    </script>
</body>
</html>
    """
    return render_template_string(html_template)

@app.route('/jobs/<job_id>')
def job_details(job_id):
    """Individual job details page."""
    job = next((j for j in JOBS_DB if j['job_id'] == job_id), None)
    
    if not job:
        return "Job not found", 404
    
    # Get company details
    company = next((c for c in COMPANIES_DB if c['company_id'] == job.get('company_id')), None)
    
    html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ job.role }} at {{ job.company }} - Sandbox Job Portal</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; background: #f8f9fa; }
        .container { max-width: 1000px; margin: 0 auto; padding: 0 20px; }
        
        /* Header */
        header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 1rem 0; }
        .header-content { display: flex; justify-content: space-between; align-items: center; }
        .logo { font-size: 1.8rem; font-weight: bold; }
        .nav { display: flex; gap: 2rem; }
        .nav a { color: white; text-decoration: none; transition: opacity 0.3s; }
        .nav a:hover { opacity: 0.8; }
        
        /* Main Content */
        .main-content { padding: 2rem 0; }
        .job-header { background: white; padding: 2rem; border-radius: 10px; margin-bottom: 2rem; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .job-title { font-size: 2.5rem; margin-bottom: 1rem; }
        .company-info { display: flex; align-items: center; gap: 1rem; margin-bottom: 1rem; }
        .company-logo { width: 60px; height: 60px; border-radius: 10px; background: #f0f0f0; display: flex; align-items: center; justify-content: center; font-size: 1.5rem; }
        .company-name { font-size: 1.3rem; color: #667eea; font-weight: 600; }
        .job-meta { display: flex; flex-wrap: wrap; gap: 2rem; margin-bottom: 2rem; }
        .meta-item { display: flex; align-items: center; gap: 0.5rem; }
        .job-type { background: #e3f2fd; color: #1976d2; padding: 0.5rem 1rem; border-radius: 20px; font-size: 0.9rem; }
        .apply-section { text-align: center; margin-bottom: 2rem; }
        .apply-btn { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 1rem 3rem; border: none; border-radius: 5px; cursor: pointer; font-size: 1.1rem; transition: opacity 0.3s; }
        .apply-btn:hover { opacity: 0.9; }
        
        /* Content Sections */
        .content-section { background: white; padding: 2rem; border-radius: 10px; margin-bottom: 2rem; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .section-title { font-size: 1.5rem; margin-bottom: 1rem; color: #333; }
        .description { white-space: pre-line; line-height: 1.8; }
        .skills-grid { display: flex; flex-wrap: wrap; gap: 0.5rem; }
        .skill-tag { background: #f5f5f5; padding: 0.5rem 1rem; border-radius: 20px; font-size: 0.9rem; color: #666; }
        .required { background: #e8f5e8; color: #2e7d32; }
        .preferred { background: #fff3e0; color: #f57c00; }
        
        /* Company Section */
        .company-section { display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; }
        .company-details h3 { margin-bottom: 1rem; }
        .company-details p { margin-bottom: 0.5rem; }
        .benefits-list { list-style: none; }
        .benefits-list li { padding: 0.3rem 0; }
        .benefits-list li:before { content: "✓ "; color: #4caf50; font-weight: bold; }
        
        /* Responsive */
        @media (max-width: 768px) {
            .job-title { font-size: 2rem; }
            .job-meta { flex-direction: column; gap: 1rem; }
            .company-section { grid-template-columns: 1fr; }
        }
    </style>
</head>
<body>
    <header>
        <div class="container">
            <div class="header-content">
                <div class="logo">🚀 Sandbox Jobs</div>
                <nav class="nav">
                    <a href="/">Home</a>
                    <a href="/jobs">Browse Jobs</a>
                    <a href="/companies">Companies</a>
                    <a href="/applications">Applications</a>
                    <a href="/company/post-job">Post Job</a>
                    <a href="/api/portal/status">API Status</a>
                </nav>
            </div>
        </div>
    </header>

    <main class="main-content">
        <div class="container">
            <div class="job-header">
                <h1 class="job-title">{{ job.role }}</h1>
                <div class="company-info">
                    <div class="company-logo">{{ job.company[0] }}</div>
                    <div>
                        <div class="company-name">{{ job.company }}</div>
                        <div>{{ job.department }}</div>
                    </div>
                </div>
                <div class="job-meta">
                    <div class="meta-item">
                        <span>📍</span>
                        <span>{{ job.location }}</span>
                    </div>
                    <div class="meta-item">
                        <span>💰</span>
                        <span>{{ job.salary_range }}</span>
                    </div>
                    <div class="meta-item">
                        <span>📅</span>
                        <span>Posted {{ (datetime.now() - datetime.fromisoformat(job.posted_date.replace('Z', '+00:00'))).days }} days ago</span>
                    </div>
                    <div class="meta-item">
                        <span>👁️</span>
                        <span>{{ job.views }} views</span>
                    </div>
                    <div class="meta-item">
                        <span>📝</span>
                        <span>{{ job.applications_count }} applications</span>
                    </div>
                </div>
                <div class="job-type">{{ job.job_type.title() }} • {{ job.experience_level }}</div>
                <div class="apply-section">
                    <button class="apply-btn" onclick="applyToJob('{{ job.job_id }}')">Apply Now</button>
                </div>
            </div>

            <div class="content-section">
                <h2 class="section-title">Job Description</h2>
                <div class="description">{{ job.description }}</div>
            </div>

            <div class="content-section">
                <h2 class="section-title">Required Skills</h2>
                <div class="skills-grid">
                    {% for skill in job.required_skills %}
                    <span class="skill-tag required">{{ skill }}</span>
                    {% endfor %}
                </div>
            </div>

            {% if job.preferred_skills %}
            <div class="content-section">
                <h2 class="section-title">Preferred Skills</h2>
                <div class="skills-grid">
                    {% for skill in job.preferred_skills %}
                    <span class="skill-tag preferred">{{ skill }}</span>
                    {% endfor %}
                </div>
            </div>
            {% endif %}

            {% if company %}
            <div class="content-section">
                <h2 class="section-title">About {{ company.name }}</h2>
                <div class="company-section">
                    <div class="company-details">
                        <h3>Company Overview</h3>
                        <p><strong>Industry:</strong> {{ company.industry }}</p>
                        <p><strong>Size:</strong> {{ company.size }}</p>
                        <p><strong>Location:</strong> {{ company.location }}</p>
                        <p><strong>Website:</strong> <a href="{{ company.website }}" target="_blank">{{ company.website }}</a></p>
                        <br>
                        <p>{{ company.description }}</p>
                        <br>
                        <p><strong>Culture:</strong> {{ company.culture }}</p>
                    </div>
                    <div>
                        <h3>Benefits & Perks</h3>
                        <ul class="benefits-list">
                            {% for benefit in company.benefits %}
                            <li>{{ benefit }}</li>
                            {% endfor %}
                        </ul>
                    </div>
                </div>
            </div>
            {% endif %}
        </div>
    </main>

    <script>
        function applyToJob(jobId) {
            window.open(`/jobs/${jobId}/apply`, '_blank');
        }
    </script>
</body>
</html>
    """
    return render_template_string(html_template, job=job, company=company, datetime=datetime)

@app.route('/jobs/<job_id>/apply')
def application_form(job_id):
    """Application form page."""
    job = next((j for j in JOBS_DB if j['job_id'] == job_id), None)
    
    if not job:
        return "Job not found", 404
    
    html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Apply for {{ job.role }} at {{ job.company }}</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; background: #f8f9fa; }
        .container { max-width: 800px; margin: 0 auto; padding: 2rem 20px; }
        
        /* Header */
        .header { background: white; padding: 2rem; border-radius: 10px; margin-bottom: 2rem; box-shadow: 0 2px 10px rgba(0,0,0,0.1); text-align: center; }
        .job-title { font-size: 2rem; margin-bottom: 0.5rem; }
        .company-name { color: #667eea; font-size: 1.2rem; }
        
        /* Form */
        .application-form { background: white; padding: 2rem; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .form-section { margin-bottom: 2rem; }
        .section-title { font-size: 1.3rem; margin-bottom: 1rem; color: #333; border-bottom: 2px solid #f0f0f0; padding-bottom: 0.5rem; }
        .form-group { margin-bottom: 1.5rem; }
        .form-group label { display: block; margin-bottom: 0.5rem; font-weight: 600; }
        .form-group input, .form-group textarea, .form-group select { width: 100%; padding: 0.8rem; border: 1px solid #ddd; border-radius: 5px; font-size: 1rem; }
        .form-group textarea { height: 120px; resize: vertical; }
        .form-group.large textarea { height: 200px; }
        .required { color: #e74c3c; }
        .form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
        .skills-input { display: flex; flex-wrap: wrap; gap: 0.5rem; margin-top: 0.5rem; }
        .skill-tag { background: #e3f2fd; color: #1976d2; padding: 0.3rem 0.8rem; border-radius: 15px; font-size: 0.9rem; }
        .file-upload { border: 2px dashed #ddd; padding: 2rem; text-align: center; border-radius: 5px; cursor: pointer; transition: border-color 0.3s; }
        .file-upload:hover { border-color: #667eea; }
        .file-upload.dragover { border-color: #667eea; background: #f8f9ff; }
        
        /* Buttons */
        .form-actions { display: flex; gap: 1rem; justify-content: center; margin-top: 2rem; }
        .btn { padding: 1rem 2rem; border: none; border-radius: 5px; cursor: pointer; font-size: 1rem; transition: opacity 0.3s; }
        .btn-primary { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }
        .btn-secondary { background: #f5f5f5; color: #333; }
        .btn:hover { opacity: 0.9; }
        .btn:disabled { opacity: 0.6; cursor: not-allowed; }
        
        /* Success Message */
        .success-message { background: #d4edda; color: #155724; padding: 1rem; border-radius: 5px; margin-bottom: 1rem; display: none; }
        .error-message { background: #f8d7da; color: #721c24; padding: 1rem; border-radius: 5px; margin-bottom: 1rem; display: none; }
        
        /* Loading */
        .loading { display: none; text-align: center; padding: 2rem; }
        
        /* Responsive */
        @media (max-width: 768px) {
            .form-row { grid-template-columns: 1fr; }
            .form-actions { flex-direction: column; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1 class="job-title">{{ job.role }}</h1>
            <div class="company-name">{{ job.company }}</div>
        </div>

        <div class="application-form">
            <div id="successMessage" class="success-message"></div>
            <div id="errorMessage" class="error-message"></div>
            
            <form id="applicationForm">
                <div class="form-section">
                    <h2 class="section-title">Personal Information</h2>
                    <div class="form-row">
                        <div class="form-group">
                            <label for="firstName">First Name <span class="required">*</span></label>
                            <input type="text" id="firstName" name="firstName" required>
                        </div>
                        <div class="form-group">
                            <label for="lastName">Last Name <span class="required">*</span></label>
                            <input type="text" id="lastName" name="lastName" required>
                        </div>
                    </div>
                    <div class="form-row">
                        <div class="form-group">
                            <label for="email">Email Address <span class="required">*</span></label>
                            <input type="email" id="email" name="email" required>
                        </div>
                        <div class="form-group">
                            <label for="phone">Phone Number</label>
                            <input type="tel" id="phone" name="phone">
                        </div>
                    </div>
                    <div class="form-group">
                        <label for="location">Current Location</label>
                        <input type="text" id="location" name="location" placeholder="City, State/Country">
                    </div>
                </div>

                <div class="form-section">
                    <h2 class="section-title">Professional Information</h2>
                    <div class="form-group">
                        <label for="experience">Years of Experience</label>
                        <select id="experience" name="experience">
                            <option value="">Select experience level</option>
                            <option value="0">No experience</option>
                            <option value="1">Less than 1 year</option>
                            <option value="2">1-2 years</option>
                            <option value="3">3-5 years</option>
                            <option value="5">5+ years</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="skills">Relevant Skills <span class="required">*</span></label>
                        <input type="text" id="skills" name="skills" placeholder="Enter skills separated by commas" required>
                        <div class="skills-input" id="skillsDisplay"></div>
                    </div>
                    <div class="form-group">
                        <label for="currentRole">Current Role/Position</label>
                        <input type="text" id="currentRole" name="currentRole" placeholder="e.g., Software Engineer, Student">
                    </div>
                    <div class="form-group">
                        <label for="education">Education</label>
                        <input type="text" id="education" name="education" placeholder="e.g., BS Computer Science, University Name">
                    </div>
                </div>

                <div class="form-section">
                    <h2 class="section-title">Application Details</h2>
                    <div class="form-group large">
                        <label for="coverLetter">Cover Letter <span class="required">*</span></label>
                        <textarea id="coverLetter" name="coverLetter" placeholder="Tell us why you're interested in this position and what makes you a great fit..." required></textarea>
                    </div>
                    <div class="form-group">
                        <label for="availability">Availability</label>
                        <select id="availability" name="availability">
                            <option value="">Select availability</option>
                            <option value="immediate">Immediate</option>
                            <option value="2weeks">2 weeks notice</option>
                            <option value="1month">1 month</option>
                            <option value="flexible">Flexible</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="salaryExpectation">Salary Expectation</label>
                        <input type="text" id="salaryExpectation" name="salaryExpectation" placeholder="e.g., $70,000 or Negotiable">
                    </div>
                </div>

                <div class="form-section">
                    <h2 class="section-title">Resume Upload</h2>
                    <div class="form-group">
                        <div class="file-upload" id="fileUpload">
                            <p>📄 Click to upload your resume or drag and drop</p>
                            <p style="color: #666; font-size: 0.9rem;">Supported formats: PDF, DOC, DOCX (Max 5MB)</p>
                            <input type="file" id="resume" name="resume" accept=".pdf,.doc,.docx" style="display: none;">
                        </div>
                        <div id="fileName" style="margin-top: 0.5rem; color: #667eea;"></div>
                    </div>
                </div>

                <div class="form-actions">
                    <button type="button" class="btn btn-secondary" onclick="window.close()">Cancel</button>
                    <button type="submit" class="btn btn-primary" id="submitBtn">Submit Application</button>
                </div>
            </form>

            <div id="loading" class="loading">
                <p>Submitting your application...</p>
            </div>
        </div>
    </div>

    <script>
        // Skills input handling
        document.getElementById('skills').addEventListener('input', function() {
            const skills = this.value.split(',').map(s => s.trim()).filter(s => s);
            const display = document.getElementById('skillsDisplay');
            display.innerHTML = skills.map(skill => `<span class="skill-tag">${skill}</span>`).join('');
        });

        // File upload handling
        const fileUpload = document.getElementById('fileUpload');
        const fileInput = document.getElementById('resume');
        const fileName = document.getElementById('fileName');

        fileUpload.addEventListener('click', () => fileInput.click());
        
        fileUpload.addEventListener('dragover', (e) => {
            e.preventDefault();
            fileUpload.classList.add('dragover');
        });
        
        fileUpload.addEventListener('dragleave', () => {
            fileUpload.classList.remove('dragover');
        });
        
        fileUpload.addEventListener('drop', (e) => {
            e.preventDefault();
            fileUpload.classList.remove('dragover');
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                fileInput.files = files;
                handleFileSelect();
            }
        });

        fileInput.addEventListener('change', handleFileSelect);

        function handleFileSelect() {
            const file = fileInput.files[0];
            if (file) {
                fileName.textContent = `Selected: ${file.name} (${(file.size / 1024 / 1024).toFixed(2)} MB)`;
            }
        }

        // Form submission
        document.getElementById('applicationForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const submitBtn = document.getElementById('submitBtn');
            const loading = document.getElementById('loading');
            const form = document.getElementById('applicationForm');
            
            // Show loading
            submitBtn.disabled = true;
            loading.style.display = 'block';
            form.style.display = 'none';
            
            // Prepare form data
            const formData = new FormData();
            formData.append('applicant_name', `${document.getElementById('firstName').value} ${document.getElementById('lastName').value}`);
            formData.append('email', document.getElementById('email').value);
            formData.append('phone', document.getElementById('phone').value);
            formData.append('location', document.getElementById('location').value);
            formData.append('experience_years', document.getElementById('experience').value);
            formData.append('skills', document.getElementById('skills').value.split(',').map(s => s.trim()).filter(s => s));
            formData.append('current_role', document.getElementById('currentRole').value);
            formData.append('education', document.getElementById('education').value);
            formData.append('cover_letter', document.getElementById('coverLetter').value);
            formData.append('availability', document.getElementById('availability').value);
            formData.append('salary_expectation', document.getElementById('salaryExpectation').value);
            
            if (fileInput.files[0]) {
                formData.append('resume', fileInput.files[0]);
            }

            try {
                const response = await fetch(`/api/jobs/{{ job.job_id }}/apply`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        applicant_name: `${document.getElementById('firstName').value} ${document.getElementById('lastName').value}`,
                        email: document.getElementById('email').value,
                        phone: document.getElementById('phone').value,
                        location: document.getElementById('location').value,
                        experience_years: document.getElementById('experience').value,
                        skills: document.getElementById('skills').value.split(',').map(s => s.trim()).filter(s => s),
                        current_role: document.getElementById('currentRole').value,
                        education: document.getElementById('education').value,
                        cover_letter: document.getElementById('coverLetter').value,
                        availability: document.getElementById('availability').value,
                        salary_expectation: document.getElementById('salaryExpectation').value
                    })
                });

                const result = await response.json();
                
                loading.style.display = 'none';
                
                if (result.success) {
                    document.getElementById('successMessage').innerHTML = `
                        <strong>Application Submitted Successfully!</strong><br>
                        Application ID: ${result.application_id}<br>
                        ${result.message}<br>
                        ${result.next_steps}
                    `;
                    document.getElementById('successMessage').style.display = 'block';
                    
                    // Show success and hide form
                    setTimeout(() => {
                        if (confirm('Application submitted successfully! Would you like to close this window?')) {
                            window.close();
                        }
                    }, 2000);
                } else {
                    throw new Error(result.error || 'Application submission failed');
                }
                
            } catch (error) {
                loading.style.display = 'none';
                form.style.display = 'block';
                submitBtn.disabled = false;
                
                document.getElementById('errorMessage').innerHTML = `
                    <strong>Application Failed:</strong> ${error.message}
                `;
                document.getElementById('errorMessage').style.display = 'block';
            }
        });
    </script>
</body>
</html>
    """
    return render_template_string(html_template, job=job)

@app.route('/company/post-job')
def company_post_job_page():
    """Company job posting page."""
    html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Post a Job - Sandbox Job Portal</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; background: #f8f9fa; }
        .container { max-width: 800px; margin: 0 auto; padding: 0 20px; }
        
        /* Header */
        header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 1rem 0; }
        .header-content { display: flex; justify-content: space-between; align-items: center; }
        .logo { font-size: 1.8rem; font-weight: bold; }
        .nav { display: flex; gap: 2rem; }
        .nav a { color: white; text-decoration: none; transition: opacity 0.3s; }
        .nav a:hover { opacity: 0.8; }
        
        /* Main Content */
        .main-content { padding: 2rem 0; }
        .page-header { background: white; padding: 2rem; border-radius: 10px; margin-bottom: 2rem; box-shadow: 0 2px 10px rgba(0,0,0,0.1); text-align: center; }
        .page-title { font-size: 2.5rem; margin-bottom: 1rem; }
        .page-subtitle { color: #666; font-size: 1.1rem; }
        
        /* Form */
        .job-form { background: white; padding: 2rem; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .form-section { margin-bottom: 2rem; }
        .section-title { font-size: 1.3rem; margin-bottom: 1rem; color: #333; border-bottom: 2px solid #f0f0f0; padding-bottom: 0.5rem; }
        .form-group { margin-bottom: 1.5rem; }
        .form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
        .form-group label { display: block; margin-bottom: 0.5rem; font-weight: 600; }
        .form-group input, .form-group textarea, .form-group select { width: 100%; padding: 0.8rem; border: 1px solid #ddd; border-radius: 5px; font-size: 1rem; }
        .form-group textarea { height: 120px; resize: vertical; }
        .form-group.large textarea { height: 200px; }
        .required { color: #e74c3c; }
        .skills-input { display: flex; flex-wrap: wrap; gap: 0.5rem; margin-top: 0.5rem; }
        .skill-tag { background: #e3f2fd; color: #1976d2; padding: 0.3rem 0.8rem; border-radius: 15px; font-size: 0.9rem; position: relative; }
        .skill-tag .remove { margin-left: 0.5rem; cursor: pointer; color: #666; }
        .skill-tag .remove:hover { color: #e74c3c; }
        
        /* Buttons */
        .form-actions { display: flex; gap: 1rem; justify-content: center; margin-top: 2rem; }
        .btn { padding: 1rem 2rem; border: none; border-radius: 5px; cursor: pointer; font-size: 1rem; transition: opacity 0.3s; }
        .btn-primary { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }
        .btn-secondary { background: #f5f5f5; color: #333; }
        .btn:hover { opacity: 0.9; }
        .btn:disabled { opacity: 0.6; cursor: not-allowed; }
        
        /* Messages */
        .success-message { background: #d4edda; color: #155724; padding: 1rem; border-radius: 5px; margin-bottom: 1rem; display: none; }
        .error-message { background: #f8d7da; color: #721c24; padding: 1rem; border-radius: 5px; margin-bottom: 1rem; display: none; }
        
        /* Loading */
        .loading { display: none; text-align: center; padding: 2rem; }
        
        /* Responsive */
        @media (max-width: 768px) {
            .form-row { grid-template-columns: 1fr; }
            .form-actions { flex-direction: column; }
        }
    </style>
</head>
<body>
    <header>
        <div class="container">
            <div class="header-content">
                <div class="logo">🚀 Sandbox Jobs</div>
                <nav class="nav">
                    <a href="/">Home</a>
                    <a href="/jobs">Browse Jobs</a>
                    <a href="/companies">Companies</a>
                    <a href="/applications">Applications</a>
                    <a href="/company/post-job">Post Job</a>
                    <a href="/api/portal/status">API Status</a>
                </nav>
            </div>
        </div>
    </header>

    <main class="main-content">
        <div class="container">
            <div class="page-header">
                <h1 class="page-title">Post a New Job</h1>
                <p class="page-subtitle">Add your job opening to our portal and reach talented candidates</p>
            </div>

            <div class="job-form">
                <div id="successMessage" class="success-message"></div>
                <div id="errorMessage" class="error-message"></div>
                
                <form id="jobForm">
                    <div class="form-section">
                        <h2 class="section-title">Company Information</h2>
                        <div class="form-row">
                            <div class="form-group">
                                <label for="companyName">Company Name <span class="required">*</span></label>
                                <input type="text" id="companyName" name="companyName" required>
                            </div>
                            <div class="form-group">
                                <label for="industry">Industry <span class="required">*</span></label>
                                <select id="industry" name="industry" required>
                                    <option value="">Select Industry</option>
                                    <option value="Technology">Technology</option>
                                    <option value="Financial Technology">Financial Technology</option>
                                    <option value="Data Science">Data Science</option>
                                    <option value="Web Development">Web Development</option>
                                    <option value="Mobile Development">Mobile Development</option>
                                    <option value="Artificial Intelligence">Artificial Intelligence</option>
                                    <option value="Cybersecurity">Cybersecurity</option>
                                    <option value="Gaming">Gaming</option>
                                    <option value="Healthcare Technology">Healthcare Technology</option>
                                    <option value="E-commerce">E-commerce</option>
                                    <option value="Cloud Computing">Cloud Computing</option>
                                    <option value="Renewable Energy">Renewable Energy</option>
                                </select>
                            </div>
                        </div>
                        <div class="form-row">
                            <div class="form-group">
                                <label for="companySize">Company Size</label>
                                <select id="companySize" name="companySize">
                                    <option value="">Select Size</option>
                                    <option value="1-10 employees">1-10 employees</option>
                                    <option value="10-50 employees">10-50 employees</option>
                                    <option value="50-100 employees">50-100 employees</option>
                                    <option value="100-500 employees">100-500 employees</option>
                                    <option value="500-1000 employees">500-1000 employees</option>
                                    <option value="1000+ employees">1000+ employees</option>
                                </select>
                            </div>
                            <div class="form-group">
                                <label for="companyLocation">Company Location <span class="required">*</span></label>
                                <input type="text" id="companyLocation" name="companyLocation" placeholder="e.g., San Francisco, CA" required>
                            </div>
                        </div>
                    </div>

                    <div class="form-section">
                        <h2 class="section-title">Job Details</h2>
                        <div class="form-group">
                            <label for="jobTitle">Job Title <span class="required">*</span></label>
                            <input type="text" id="jobTitle" name="jobTitle" placeholder="e.g., Software Engineer, Data Scientist" required>
                        </div>
                        <div class="form-row">
                            <div class="form-group">
                                <label for="department">Department</label>
                                <input type="text" id="department" name="department" placeholder="e.g., Engineering, Marketing">
                            </div>
                            <div class="form-group">
                                <label for="jobType">Job Type <span class="required">*</span></label>
                                <select id="jobType" name="jobType" required>
                                    <option value="">Select Type</option>
                                    <option value="full-time">Full-time</option>
                                    <option value="part-time">Part-time</option>
                                    <option value="internship">Internship</option>
                                    <option value="contract">Contract</option>
                                </select>
                            </div>
                        </div>
                        <div class="form-row">
                            <div class="form-group">
                                <label for="experienceLevel">Experience Level <span class="required">*</span></label>
                                <select id="experienceLevel" name="experienceLevel" required>
                                    <option value="">Select Level</option>
                                    <option value="Entry Level">Entry Level</option>
                                    <option value="Junior">Junior</option>
                                    <option value="Mid Level">Mid Level</option>
                                    <option value="Senior">Senior</option>
                                    <option value="Lead">Lead</option>
                                </select>
                            </div>
                            <div class="form-group">
                                <label for="minExperience">Minimum Experience (years)</label>
                                <input type="number" id="minExperience" name="minExperience" min="0" max="20" placeholder="0">
                            </div>
                        </div>
                        <div class="form-row">
                            <div class="form-group">
                                <label for="salaryRange">Salary Range <span class="required">*</span></label>
                                <input type="text" id="salaryRange" name="salaryRange" placeholder="e.g., $70k-90k, $25-30/hour" required>
                            </div>
                            <div class="form-group">
                                <label for="jobLocation">Job Location <span class="required">*</span></label>
                                <input type="text" id="jobLocation" name="jobLocation" placeholder="e.g., Remote, San Francisco, CA" required>
                            </div>
                        </div>
                    </div>

                    <div class="form-section">
                        <h2 class="section-title">Job Description</h2>
                        <div class="form-group large">
                            <label for="jobDescription">Job Description <span class="required">*</span></label>
                            <textarea id="jobDescription" name="jobDescription" placeholder="Describe the role, responsibilities, and what you're looking for..." required></textarea>
                        </div>
                    </div>

                    <div class="form-section">
                        <h2 class="section-title">Skills & Requirements</h2>
                        <div class="form-group">
                            <label for="requiredSkills">Required Skills <span class="required">*</span></label>
                            <input type="text" id="requiredSkills" name="requiredSkills" placeholder="Enter skills separated by commas" required>
                            <div class="skills-input" id="requiredSkillsDisplay"></div>
                        </div>
                        <div class="form-group">
                            <label for="preferredSkills">Preferred Skills</label>
                            <input type="text" id="preferredSkills" name="preferredSkills" placeholder="Enter preferred skills separated by commas">
                            <div class="skills-input" id="preferredSkillsDisplay"></div>
                        </div>
                    </div>

                    <div class="form-actions">
                        <button type="button" class="btn btn-secondary" onclick="resetForm()">Reset Form</button>
                        <button type="submit" class="btn btn-primary" id="submitBtn">Post Job</button>
                    </div>
                </form>

                <div id="loading" class="loading">
                    <p>Posting your job...</p>
                </div>
            </div>
        </div>
    </main>

    <script>
        // Skills input handling
        document.getElementById('requiredSkills').addEventListener('input', function() {
            updateSkillsDisplay('requiredSkills', 'requiredSkillsDisplay');
        });
        
        document.getElementById('preferredSkills').addEventListener('input', function() {
            updateSkillsDisplay('preferredSkills', 'preferredSkillsDisplay');
        });

        function updateSkillsDisplay(inputId, displayId) {
            const input = document.getElementById(inputId);
            const display = document.getElementById(displayId);
            const skills = input.value.split(',').map(s => s.trim()).filter(s => s);
            
            display.innerHTML = skills.map(skill => 
                `<span class="skill-tag">${skill}</span>`
            ).join('');
        }

        // Form submission
        document.getElementById('jobForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const submitBtn = document.getElementById('submitBtn');
            const loading = document.getElementById('loading');
            const form = document.getElementById('jobForm');
            
            // Show loading
            submitBtn.disabled = true;
            loading.style.display = 'block';
            form.style.display = 'none';
            
            // Prepare job data
            const formData = new FormData(e.target);
            const jobData = {
                company: formData.get('companyName'),
                industry: formData.get('industry'),
                company_size: formData.get('companySize'),
                company_location: formData.get('companyLocation'),
                role: formData.get('jobTitle'),
                department: formData.get('department') || 'General',
                job_type: formData.get('jobType'),
                experience_level: formData.get('experienceLevel'),
                min_experience_years: parseInt(formData.get('minExperience')) || 0,
                salary_range: formData.get('salaryRange'),
                location: formData.get('jobLocation'),
                description: formData.get('jobDescription'),
                required_skills: formData.get('requiredSkills').split(',').map(s => s.trim()).filter(s => s),
                preferred_skills: formData.get('preferredSkills').split(',').map(s => s.trim()).filter(s => s)
            };

            try {
                const response = await fetch('/api/company/post-job', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(jobData)
                });

                const result = await response.json();
                
                loading.style.display = 'none';
                
                if (result.success) {
                    document.getElementById('successMessage').innerHTML = `
                        <strong>Job Posted Successfully!</strong><br>
                        Job ID: ${result.job_id}<br>
                        Your job "${result.job.role}" at "${result.job.company}" has been posted and is now live.
                    `;
                    document.getElementById('successMessage').style.display = 'block';
                    
                    // Reset form after success
                    setTimeout(() => {
                        resetForm();
                        document.getElementById('successMessage').style.display = 'none';
                    }, 5000);
                } else {
                    throw new Error(result.error || 'Job posting failed');
                }
                
            } catch (error) {
                loading.style.display = 'none';
                form.style.display = 'block';
                submitBtn.disabled = false;
                
                document.getElementById('errorMessage').innerHTML = `
                    <strong>Job Posting Failed:</strong> ${error.message}
                `;
                document.getElementById('errorMessage').style.display = 'block';
            }
        });

        function resetForm() {
            document.getElementById('jobForm').reset();
            document.getElementById('requiredSkillsDisplay').innerHTML = '';
            document.getElementById('preferredSkillsDisplay').innerHTML = '';
            document.getElementById('successMessage').style.display = 'none';
            document.getElementById('errorMessage').style.display = 'none';
            document.getElementById('loading').style.display = 'none';
            document.getElementById('jobForm').style.display = 'block';
            document.getElementById('submitBtn').disabled = false;
        }
    </script>
</body>
</html>
    """
    return render_template_string(html_template)

@app.route('/api/company/post-job', methods=['POST'])
def post_job_api():
    """API endpoint for companies to post new jobs."""
    
    try:
        job_data = request.get_json()
        
        if not job_data:
            return jsonify({
                "success": False,
                "error": "Job data is required"
            }), 400
        
        # Validate required fields
        required_fields = ['company', 'role', 'job_type', 'experience_level', 'salary_range', 'location', 'description', 'required_skills']
        missing_fields = [field for field in required_fields if not job_data.get(field)]
        
        if missing_fields:
            return jsonify({
                "success": False,
                "error": f"Missing required fields: {missing_fields}"
            }), 400
        
        # Generate job ID
        job_counter = len(JOBS_DB) + 1
        job_id = f"job-{job_counter:03d}"
        
        # Create company if it doesn't exist
        company_id = f"company-{len(COMPANIES_DB) + 1:03d}"
        existing_company = next((c for c in COMPANIES_DB if c['name'].lower() == job_data['company'].lower()), None)
        
        if not existing_company:
            new_company = {
                "company_id": company_id,
                "name": job_data['company'],
                "industry": job_data.get('industry', 'Technology'),
                "size": job_data.get('company_size', '50-100 employees'),
                "location": job_data.get('company_location', job_data['location']),
                "description": f"{job_data['company']} is a growing company in the {job_data.get('industry', 'technology')} industry.",
                "website": f"https://{job_data['company'].lower().replace(' ', '')}-sandbox.com",
                "logo": f"https://via.placeholder.com/100x100?text={job_data['company'][:2].upper()}",
                "benefits": ["Health Insurance", "Flexible Hours", "Professional Development"],
                "culture": "Innovative, collaborative, growth-focused"
            }
            COMPANIES_DB.append(new_company)
            company_id = new_company["company_id"]
        else:
            company_id = existing_company["company_id"]
        
        # Create job posting
        new_job = {
            "job_id": job_id,
            "company_id": company_id,
            "company": job_data['company'],
            "role": job_data['role'],
            "department": job_data.get('department', 'General'),
            "location": job_data['location'],
            "job_type": job_data['job_type'],
            "experience_level": job_data['experience_level'],
            "salary_range": job_data['salary_range'],
            "posted_date": datetime.now().isoformat(),
            "deadline": (datetime.now() + timedelta(days=30)).isoformat(),
            "status": "active",
            "description": job_data['description'],
            "required_skills": job_data['required_skills'],
            "preferred_skills": job_data.get('preferred_skills', []),
            "min_experience_years": job_data.get('min_experience_years', 0),
            "application_url": f"http://localhost:5001/api/jobs/{job_id}/apply",
            "views": 0,
            "applications_count": 0
        }
        
        # Add to jobs database
        JOBS_DB.append(new_job)
        
        # Update portal stats
        global PORTAL_STATS
        PORTAL_STATS["total_jobs"] = len(JOBS_DB)
        PORTAL_STATS["active_jobs"] = len([j for j in JOBS_DB if j["status"] == "active"])
        PORTAL_STATS["companies"] = len(COMPANIES_DB)
        
        return jsonify({
            "success": True,
            "job_id": job_id,
            "message": f"Job '{job_data['role']}' posted successfully",
            "job": new_job
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/applications')
def applications_page():
    """Applications listing page - view all submitted applications."""
    html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Applications - Sandbox Job Portal</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; background: #f8f9fa; }
        .container { max-width: 1400px; margin: 0 auto; padding: 0 20px; }
        
        /* Header */
        header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 1rem 0; }
        .header-content { display: flex; justify-content: space-between; align-items: center; }
        .logo { font-size: 1.8rem; font-weight: bold; }
        .nav { display: flex; gap: 2rem; }
        .nav a { color: white; text-decoration: none; transition: opacity 0.3s; }
        .nav a:hover { opacity: 0.8; }
        
        /* Main Content */
        .main-content { padding: 2rem 0; }
        .page-title { font-size: 2.5rem; margin-bottom: 2rem; text-align: center; }
        
        /* Stats */
        .stats-bar { background: white; padding: 1.5rem; border-radius: 10px; margin-bottom: 2rem; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 2rem; text-align: center; }
        .stat-item { }
        .stat-number { font-size: 2rem; font-weight: bold; color: #667eea; }
        .stat-label { color: #666; margin-top: 0.3rem; }
        
        /* Filters */
        .filters { background: white; padding: 2rem; border-radius: 10px; margin-bottom: 2rem; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .filters-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; }
        .filter-group label { display: block; margin-bottom: 0.5rem; font-weight: 600; }
        .filter-group select, .filter-group input { width: 100%; padding: 0.8rem; border: 1px solid #ddd; border-radius: 5px; }
        
        /* Applications Table */
        .applications-container { background: white; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); overflow: hidden; }
        .table-header { background: #f8f9fa; padding: 1rem 2rem; border-bottom: 1px solid #dee2e6; }
        .applications-table { width: 100%; }
        .applications-table th, .applications-table td { padding: 1rem; text-align: left; border-bottom: 1px solid #dee2e6; }
        .applications-table th { background: #f8f9fa; font-weight: 600; }
        .applications-table tr:hover { background: #f8f9fa; }
        .status-badge { padding: 0.3rem 0.8rem; border-radius: 20px; font-size: 0.8rem; font-weight: 600; }
        .status-submitted { background: #d4edda; color: #155724; }
        .status-reviewed { background: #d1ecf1; color: #0c5460; }
        .status-rejected { background: #f8d7da; color: #721c24; }
        .applicant-name { font-weight: 600; color: #333; }
        .job-title { color: #667eea; }
        .company-name { color: #666; font-size: 0.9rem; }
        .application-date { color: #666; font-size: 0.9rem; }
        .view-btn { background: #667eea; color: white; padding: 0.5rem 1rem; border: none; border-radius: 5px; cursor: pointer; font-size: 0.8rem; text-decoration: none; margin-right: 0.5rem; }
        .view-btn:hover { opacity: 0.9; }
        .delete-btn { background: #dc3545; color: white; padding: 0.5rem 1rem; border: none; border-radius: 5px; cursor: pointer; font-size: 0.8rem; }
        .delete-btn:hover { background: #c82333; }
        .action-buttons { display: flex; gap: 0.5rem; }
        
        /* Loading */
        .loading { text-align: center; padding: 2rem; }
        
        /* No results */
        .no-results { text-align: center; padding: 4rem; color: #666; }
        
        /* Responsive */
        @media (max-width: 768px) {
            .applications-table { font-size: 0.9rem; }
            .applications-table th, .applications-table td { padding: 0.5rem; }
        }
    </style>
</head>
<body>
    <header>
        <div class="container">
            <div class="header-content">
                <div class="logo">🚀 Sandbox Jobs</div>
                <nav class="nav">
                    <a href="/">Home</a>
                    <a href="/jobs">Browse Jobs</a>
                    <a href="/companies">Companies</a>
                    <a href="/applications">Applications</a>
                    <a href="/api/portal/status">API Status</a>
                </nav>
            </div>
        </div>
    </header>

    <main class="main-content">
        <div class="container">
            <h1 class="page-title">Application Management</h1>
            
            <div class="stats-bar">
                <div class="stats-grid">
                    <div class="stat-item">
                        <div class="stat-number" id="totalApplications">0</div>
                        <div class="stat-label">Total Applications</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-number" id="submittedApplications">0</div>
                        <div class="stat-label">Submitted</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-number" id="reviewedApplications">0</div>
                        <div class="stat-label">Under Review</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-number" id="uniqueApplicants">0</div>
                        <div class="stat-label">Unique Applicants</div>
                    </div>
                </div>
            </div>
            
            <div class="filters">
                <div class="filters-grid">
                    <div class="filter-group">
                        <label for="searchInput">Search Applicant</label>
                        <input type="text" id="searchInput" placeholder="Name or email...">
                    </div>
                    <div class="filter-group">
                        <label for="statusFilter">Status</label>
                        <select id="statusFilter">
                            <option value="">All Statuses</option>
                            <option value="submitted">Submitted</option>
                            <option value="reviewed">Under Review</option>
                            <option value="rejected">Rejected</option>
                        </select>
                    </div>
                    <div class="filter-group">
                        <label for="companyFilter">Company</label>
                        <select id="companyFilter">
                            <option value="">All Companies</option>
                        </select>
                    </div>
                    <div class="filter-group">
                        <label for="jobFilter">Job Role</label>
                        <select id="jobFilter">
                            <option value="">All Roles</option>
                        </select>
                    </div>
                    <div class="filter-group">
                        <label for="sortFilter">Sort By</label>
                        <select id="sortFilter">
                            <option value="date_desc">Latest First</option>
                            <option value="date_asc">Oldest First</option>
                            <option value="name_asc">Name A-Z</option>
                            <option value="name_desc">Name Z-A</option>
                            <option value="company_asc">Company A-Z</option>
                            <option value="status_asc">Status</option>
                        </select>
                    </div>
                </div>
            </div>
            
            <div class="applications-container">
                <div class="table-header">
                    <h3>All Applications</h3>
                </div>
                <div id="applicationsTable">
                    <div class="loading">Loading applications...</div>
                </div>
            </div>
        </div>
    </main>

    <script>
        let allApplications = [];
        
        // Load applications on page load
        document.addEventListener('DOMContentLoaded', loadApplications);
        
        // Add event listeners for filters
        document.getElementById('searchInput').addEventListener('input', filterApplications);
        document.getElementById('statusFilter').addEventListener('change', filterApplications);
        document.getElementById('companyFilter').addEventListener('change', filterApplications);
        document.getElementById('jobFilter').addEventListener('change', filterApplications);
        document.getElementById('sortFilter').addEventListener('change', filterApplications);

        async function loadApplications() {
            try {
                const response = await fetch('/api/applications');
                const data = await response.json();
                allApplications = data.applications;
                
                updateStats();
                populateFilters();
                displayApplications(allApplications);
            } catch (error) {
                console.error('Error loading applications:', error);
                document.getElementById('applicationsTable').innerHTML = '<div class="no-results">Error loading applications. Please try again.</div>';
            }
        }

        function updateStats() {
            const totalApps = allApplications.length;
            const submittedApps = allApplications.filter(app => app.status === 'submitted').length;
            const reviewedApps = allApplications.filter(app => app.status === 'reviewed').length;
            const uniqueApplicants = new Set(allApplications.map(app => app.email)).size;
            
            document.getElementById('totalApplications').textContent = totalApps;
            document.getElementById('submittedApplications').textContent = submittedApps;
            document.getElementById('reviewedApplications').textContent = reviewedApps;
            document.getElementById('uniqueApplicants').textContent = uniqueApplicants;
        }

        function populateFilters() {
            // Populate company filter
            const companies = [...new Set(allApplications.map(app => app.company))].sort();
            const companyFilter = document.getElementById('companyFilter');
            companies.forEach(company => {
                const option = document.createElement('option');
                option.value = company;
                option.textContent = company;
                companyFilter.appendChild(option);
            });

            // Populate job filter
            const roles = [...new Set(allApplications.map(app => app.role))].sort();
            const jobFilter = document.getElementById('jobFilter');
            roles.forEach(role => {
                const option = document.createElement('option');
                option.value = role;
                option.textContent = role;
                jobFilter.appendChild(option);
            });
        }

        function filterApplications() {
            const search = document.getElementById('searchInput').value.toLowerCase();
            const status = document.getElementById('statusFilter').value;
            const company = document.getElementById('companyFilter').value;
            const job = document.getElementById('jobFilter').value;
            const sort = document.getElementById('sortFilter').value;

            let filteredApps = allApplications.filter(app => {
                const matchesSearch = !search || 
                    app.applicant_name.toLowerCase().includes(search) ||
                    app.email.toLowerCase().includes(search);
                
                const matchesStatus = !status || app.status === status;
                const matchesCompany = !company || app.company === company;
                const matchesJob = !job || app.role === job;

                return matchesSearch && matchesStatus && matchesCompany && matchesJob;
            });

            // Apply sorting
            filteredApps.sort((a, b) => {
                switch(sort) {
                    case 'date_desc':
                        return new Date(b.applied_at) - new Date(a.applied_at);
                    case 'date_asc':
                        return new Date(a.applied_at) - new Date(b.applied_at);
                    case 'name_asc':
                        return a.applicant_name.localeCompare(b.applicant_name);
                    case 'name_desc':
                        return b.applicant_name.localeCompare(a.applicant_name);
                    case 'company_asc':
                        return a.company.localeCompare(b.company);
                    case 'status_asc':
                        return a.status.localeCompare(b.status);
                    default:
                        return new Date(b.applied_at) - new Date(a.applied_at);
                }
            });

            displayApplications(filteredApps);
        }

        function displayApplications(applications) {
            const container = document.getElementById('applicationsTable');
            
            if (applications.length === 0) {
                container.innerHTML = '<div class="no-results">No applications found matching your criteria.</div>';
                return;
            }

            const tableHTML = `
                <table class="applications-table">
                    <thead>
                        <tr>
                            <th>Applicant</th>
                            <th>Job</th>
                            <th>Company</th>
                            <th>Applied Date</th>
                            <th>Status</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${applications.map(app => `
                            <tr>
                                <td>
                                    <div class="applicant-name">${app.applicant_name}</div>
                                    <div style="color: #666; font-size: 0.9rem;">${app.email}</div>
                                </td>
                                <td>
                                    <div class="job-title">${app.role}</div>
                                </td>
                                <td>
                                    <div class="company-name">${app.company}</div>
                                </td>
                                <td>
                                    <div class="application-date">${new Date(app.applied_at).toLocaleDateString()}</div>
                                    <div style="color: #999; font-size: 0.8rem;">${new Date(app.applied_at).toLocaleTimeString()}</div>
                                </td>
                                <td>
                                    <span class="status-badge status-${app.status}">${app.status.charAt(0).toUpperCase() + app.status.slice(1)}</span>
                                </td>
                                <td>
                                    <div class="action-buttons">
                                        <a href="/applications/${app.application_id}" class="view-btn" target="_blank">View Details</a>
                                        <button class="delete-btn" onclick="deleteApplication('${app.application_id}', '${app.applicant_name}')">Delete</button>
                                    </div>
                                </td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            `;

            container.innerHTML = tableHTML;
        }

        async function deleteApplication(applicationId, applicantName) {
            if (!confirm(`Are you sure you want to delete the application from ${applicantName}?\\n\\nThis action cannot be undone.`)) {
                return;
            }

            try {
                const response = await fetch(`/api/applications/${applicationId}`, {
                    method: 'DELETE'
                });

                const result = await response.json();

                if (result.success) {
                    // Remove from local array
                    allApplications = allApplications.filter(app => app.application_id !== applicationId);
                    
                    // Update display
                    updateStats();
                    filterApplications();
                    
                    alert('Application deleted successfully!');
                } else {
                    alert(`Error deleting application: ${result.error}`);
                }
            } catch (error) {
                console.error('Error deleting application:', error);
                alert('Error deleting application. Please try again.');
            }
        }
    </script>
</body>
</html>
    """
    return render_template_string(html_template)

@app.route('/applications/<application_id>')
def application_details(application_id):
    """Individual application details page."""
    application = next((a for a in APPLICATIONS_DB if a['application_id'] == application_id), None)
    
    if not application:
        return "Application not found", 404
    
    # Get job details
    job = next((j for j in JOBS_DB if j['job_id'] == application['job_id']), None)
    
    html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Application Details - {{ application.applicant_name }}</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; background: #f8f9fa; }
        .container { max-width: 1000px; margin: 0 auto; padding: 0 20px; }
        
        /* Header */
        header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 1rem 0; }
        .header-content { display: flex; justify-content: space-between; align-items: center; }
        .logo { font-size: 1.8rem; font-weight: bold; }
        .nav { display: flex; gap: 2rem; }
        .nav a { color: white; text-decoration: none; transition: opacity 0.3s; }
        .nav a:hover { opacity: 0.8; }
        
        /* Main Content */
        .main-content { padding: 2rem 0; }
        
        /* Application Header */
        .app-header { background: white; padding: 2rem; border-radius: 10px; margin-bottom: 2rem; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .app-title { font-size: 2rem; margin-bottom: 1rem; }
        .app-meta { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-bottom: 1rem; }
        .meta-item { }
        .meta-label { font-weight: 600; color: #666; font-size: 0.9rem; }
        .meta-value { font-size: 1.1rem; }
        .status-badge { padding: 0.5rem 1rem; border-radius: 20px; font-size: 0.9rem; font-weight: 600; display: inline-block; margin-top: 0.5rem; }
        .status-submitted { background: #d4edda; color: #155724; }
        .status-reviewed { background: #d1ecf1; color: #0c5460; }
        .status-rejected { background: #f8d7da; color: #721c24; }
        
        /* Content Sections */
        .content-section { background: white; padding: 2rem; border-radius: 10px; margin-bottom: 2rem; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .section-title { font-size: 1.5rem; margin-bottom: 1rem; color: #333; border-bottom: 2px solid #f0f0f0; padding-bottom: 0.5rem; }
        .info-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1.5rem; }
        .info-item { }
        .info-label { font-weight: 600; color: #666; margin-bottom: 0.3rem; }
        .info-value { color: #333; }
        .skills-list { display: flex; flex-wrap: wrap; gap: 0.5rem; }
        .skill-tag { background: #e3f2fd; color: #1976d2; padding: 0.3rem 0.8rem; border-radius: 15px; font-size: 0.9rem; }
        .cover-letter { background: #f8f9fa; padding: 1.5rem; border-radius: 8px; border-left: 4px solid #667eea; white-space: pre-line; line-height: 1.8; }
        
        /* Job Info */
        .job-info { background: #f8f9fa; padding: 1.5rem; border-radius: 8px; border-left: 4px solid #28a745; }
        .job-title { font-size: 1.2rem; font-weight: 600; color: #333; margin-bottom: 0.5rem; }
        .job-company { color: #667eea; font-weight: 600; margin-bottom: 0.5rem; }
        .job-details { color: #666; }
        
        /* Actions */
        .actions { display: flex; gap: 1rem; justify-content: center; margin-top: 2rem; }
        .btn { padding: 1rem 2rem; border: none; border-radius: 5px; cursor: pointer; font-size: 1rem; transition: opacity 0.3s; text-decoration: none; text-align: center; }
        .btn-primary { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }
        .btn-secondary { background: #f5f5f5; color: #333; }
        .btn:hover { opacity: 0.9; }
        
        /* Responsive */
        @media (max-width: 768px) {
            .app-meta { grid-template-columns: 1fr; }
            .info-grid { grid-template-columns: 1fr; }
            .actions { flex-direction: column; }
        }
    </style>
</head>
<body>
    <header>
        <div class="container">
            <div class="header-content">
                <div class="logo">🚀 Sandbox Jobs</div>
                <nav class="nav">
                    <a href="/">Home</a>
                    <a href="/jobs">Browse Jobs</a>
                    <a href="/companies">Companies</a>
                    <a href="/applications">Applications</a>
                    <a href="/company/post-job">Post Job</a>
                    <a href="/api/portal/status">API Status</a>
                </nav>
            </div>
        </div>
    </header>

    <main class="main-content">
        <div class="container">
            <div class="app-header">
                <h1 class="app-title">Application Details</h1>
                <div class="app-meta">
                    <div class="meta-item">
                        <div class="meta-label">Application ID</div>
                        <div class="meta-value">{{ application.application_id[:8] }}...</div>
                    </div>
                    <div class="meta-item">
                        <div class="meta-label">Receipt ID</div>
                        <div class="meta-value">{{ application.receipt_id }}</div>
                    </div>
                    <div class="meta-item">
                        <div class="meta-label">Submitted</div>
                        <div class="meta-value">{{ datetime.fromisoformat(application.applied_at).strftime('%B %d, %Y at %I:%M %p') }}</div>
                    </div>
                    <div class="meta-item">
                        <div class="meta-label">Status</div>
                        <span class="status-badge status-{{ application.status }}">{{ application.status.title() }}</span>
                    </div>
                </div>
            </div>

            <div class="content-section">
                <h2 class="section-title">Job Information</h2>
                <div class="job-info">
                    <div class="job-title">{{ application.role }}</div>
                    <div class="job-company">{{ application.company }}</div>
                    {% if job %}
                    <div class="job-details">
                        📍 {{ job.location }} • 💰 {{ job.salary_range }} • 📅 {{ job.experience_level }}
                    </div>
                    {% endif %}
                </div>
            </div>

            <div class="content-section">
                <h2 class="section-title">Applicant Information</h2>
                <div class="info-grid">
                    <div class="info-item">
                        <div class="info-label">Full Name</div>
                        <div class="info-value">{{ application.applicant_name }}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">Email</div>
                        <div class="info-value">{{ application.email }}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">Phone</div>
                        <div class="info-value">{{ application.phone or 'Not provided' }}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">Location</div>
                        <div class="info-value">{{ application.location or 'Not provided' }}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">Experience</div>
                        <div class="info-value">{{ application.experience_years or 'Not specified' }} years</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">Current Role</div>
                        <div class="info-value">{{ application.current_role or 'Not provided' }}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">Education</div>
                        <div class="info-value">{{ application.education or 'Not provided' }}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">Availability</div>
                        <div class="info-value">{{ application.availability or 'Not specified' }}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">Salary Expectation</div>
                        <div class="info-value">{{ application.salary_expectation or 'Not specified' }}</div>
                    </div>
                </div>
            </div>

            <div class="content-section">
                <h2 class="section-title">Skills</h2>
                <div class="skills-list">
                    {% for skill in application.skills %}
                    <span class="skill-tag">{{ skill.strip() }}</span>
                    {% endfor %}
                </div>
            </div>

            <div class="content-section">
                <h2 class="section-title">Cover Letter</h2>
                <div class="cover-letter">{{ application.cover_letter }}</div>
            </div>

            {% if application.resume_text %}
            <div class="content-section">
                <h2 class="section-title">Resume Content</h2>
                <div class="cover-letter">{{ application.resume_text }}</div>
            </div>
            {% endif %}

            <div class="content-section">
                <h2 class="section-title">Application Status</h2>
                <div class="info-grid">
                    <div class="info-item">
                        <div class="info-label">Current Status</div>
                        <div class="info-value">{{ application.status.title() }}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">Portal Response</div>
                        <div class="info-value">{{ application.portal_response }}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">Screening Score</div>
                        <div class="info-value">{{ application.screening_score }}/100</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">Next Steps</div>
                        <div class="info-value">{{ application.next_steps }}</div>
                    </div>
                </div>
            </div>

            <div class="actions">
                <a href="/applications" class="btn btn-secondary">← Back to Applications</a>
                <a href="/jobs/{{ application.job_id }}" class="btn btn-primary" target="_blank">View Job Posting</a>
            </div>
        </div>
    </main>
</body>
</html>
    """
    return render_template_string(html_template, application=application, job=job, datetime=datetime)

@app.route('/companies')
def companies_page():
    """Companies listing page."""
    html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Companies - Sandbox Job Portal</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; background: #f8f9fa; }
        .container { max-width: 1200px; margin: 0 auto; padding: 0 20px; }
        
        /* Header */
        header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 1rem 0; }
        .header-content { display: flex; justify-content: space-between; align-items: center; }
        .logo { font-size: 1.8rem; font-weight: bold; }
        .nav { display: flex; gap: 2rem; }
        .nav a { color: white; text-decoration: none; transition: opacity 0.3s; }
        .nav a:hover { opacity: 0.8; }
        
        /* Main Content */
        .main-content { padding: 2rem 0; }
        .page-title { font-size: 2.5rem; margin-bottom: 2rem; text-align: center; }
        
        /* Companies Grid */
        .companies-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(350px, 1fr)); gap: 2rem; }
        .company-card { background: white; border-radius: 10px; padding: 2rem; box-shadow: 0 4px 15px rgba(0,0,0,0.1); transition: transform 0.3s; }
        .company-card:hover { transform: translateY(-5px); }
        .company-header { display: flex; align-items: center; gap: 1rem; margin-bottom: 1rem; }
        .company-logo { width: 60px; height: 60px; border-radius: 10px; background: #f0f0f0; display: flex; align-items: center; justify-content: center; font-size: 1.5rem; }
        .company-info h3 { font-size: 1.3rem; margin-bottom: 0.3rem; }
        .company-industry { color: #667eea; font-weight: 600; }
        .company-description { color: #666; margin-bottom: 1rem; line-height: 1.5; }
        .company-meta { display: flex; justify-content: space-between; margin-bottom: 1rem; color: #999; font-size: 0.9rem; }
        .company-benefits { margin-bottom: 1rem; }
        .benefits-list { display: flex; flex-wrap: wrap; gap: 0.5rem; }
        .benefit-tag { background: #f5f5f5; padding: 0.3rem 0.8rem; border-radius: 15px; font-size: 0.8rem; color: #666; }
        .company-actions { display: flex; gap: 1rem; }
        .btn { padding: 0.8rem 1.5rem; border: none; border-radius: 5px; cursor: pointer; font-size: 0.9rem; transition: opacity 0.3s; text-decoration: none; text-align: center; }
        .btn-primary { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }
        .btn-secondary { background: #f5f5f5; color: #333; }
        .btn:hover { opacity: 0.9; }
    </style>
</head>
<body>
    <header>
        <div class="container">
            <div class="header-content">
                <div class="logo">🚀 Sandbox Jobs</div>
                <nav class="nav">
                    <a href="/">Home</a>
                    <a href="/jobs">Browse Jobs</a>
                    <a href="/companies">Companies</a>
                    <a href="/applications">Applications</a>
                    <a href="/company/post-job">Post Job</a>
                    <a href="/api/portal/status">API Status</a>
                </nav>
            </div>
        </div>
    </header>

    <main class="main-content">
        <div class="container">
            <h1 class="page-title">Featured Companies</h1>
            
            <div class="companies-grid">
                {% for company in companies %}
                <div class="company-card">
                    <div class="company-header">
                        <div class="company-logo">{{ company.name[0] }}</div>
                        <div class="company-info">
                            <h3>{{ company.name }}</h3>
                            <div class="company-industry">{{ company.industry }}</div>
                        </div>
                    </div>
                    <div class="company-description">{{ company.description }}</div>
                    <div class="company-meta">
                        <span>📍 {{ company.location }}</span>
                        <span>👥 {{ company.size }}</span>
                    </div>
                    <div class="company-benefits">
                        <div class="benefits-list">
                            {% for benefit in company.benefits[:4] %}
                            <span class="benefit-tag">{{ benefit }}</span>
                            {% endfor %}
                        </div>
                    </div>
                    <div class="company-actions">
                        <a href="/jobs?company={{ company.name }}" class="btn btn-primary">View Jobs</a>
                        <a href="{{ company.website }}" target="_blank" class="btn btn-secondary">Visit Website</a>
                    </div>
                </div>
                {% endfor %}
            </div>
        </div>
    </main>
</body>
</html>
    """
    return render_template_string(html_template, companies=COMPANIES_DB)

# ==================== ENHANCED API ENDPOINTS ====================

@app.route('/api/portal/status', methods=['GET'])
def get_portal_status():
    """Get sandbox portal status and statistics."""
    return jsonify({
        "status": "active",
        "portal_name": "Sandbox Job Portal",
        "stats": PORTAL_STATS,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/jobs', methods=['GET'])
def get_jobs():
    """Get all available jobs from the sandbox portal with enhanced filtering."""
    
    # Filter parameters
    location = request.args.get('location')
    job_type = request.args.get('job_type') 
    experience_level = request.args.get('experience_level')
    company = request.args.get('company')
    search = request.args.get('search', '').lower()
    limit = request.args.get('limit', type=int)
    skills = request.args.get('skills', '').split(',') if request.args.get('skills') else []
    
    filtered_jobs = JOBS_DB.copy()
    
    # Apply filters
    if location:
        filtered_jobs = [j for j in filtered_jobs if location.lower() in j['location'].lower()]
    
    if job_type:
        filtered_jobs = [j for j in filtered_jobs if j['job_type'] == job_type]
    
    if experience_level:
        filtered_jobs = [j for j in filtered_jobs if experience_level.lower() in j.get('experience_level', '').lower()]
    
    if company:
        filtered_jobs = [j for j in filtered_jobs if company.lower() in j['company'].lower()]
    
    if search:
        filtered_jobs = [j for j in filtered_jobs if 
            search in j['role'].lower() or 
            search in j['company'].lower() or
            search in j.get('description', '').lower() or
            any(search in skill.lower() for skill in j['required_skills'])
        ]
        
    if skills:
        skills = [s.strip().lower() for s in skills if s.strip()]
        if skills:
            filtered_jobs = [j for j in filtered_jobs 
                           if any(skill in [rs.lower() for rs in j['required_skills']] for skill in skills)]
    
    # Apply limit
    if limit:
        filtered_jobs = filtered_jobs[:limit]
    
    return jsonify({
        "success": True,
        "jobs": filtered_jobs,
        "total_count": len(filtered_jobs),
        "filters_applied": {
            "location": location,
            "job_type": job_type,
            "experience_level": experience_level,
            "company": company,
            "search": search,
            "skills": skills
        }
    })

@app.route('/api/jobs/<job_id>', methods=['GET'])
def get_job_details(job_id):
    """Get detailed information about a specific job."""
    
    job = next((j for j in JOBS_DB if j['job_id'] == job_id), None)
    
    if not job:
        return jsonify({
            "success": False,
            "error": f"Job {job_id} not found"
        }), 404
    
    # Increment view count
    job['views'] = job.get('views', 0) + 1
    
    # Get company details
    company = next((c for c in COMPANIES_DB if c['company_id'] == job.get('company_id')), None)
    
    return jsonify({
        "success": True,
        "job": job,
        "company": company
    })

@app.route('/api/companies', methods=['GET'])
def get_companies():
    """Get all companies."""
    return jsonify({
        "success": True,
        "companies": COMPANIES_DB,
        "total_count": len(COMPANIES_DB)
    })

@app.route('/api/companies/<company_id>', methods=['GET'])
def get_company_details(company_id):
    """Get detailed information about a specific company."""
    
    company = next((c for c in COMPANIES_DB if c['company_id'] == company_id), None)
    
    if not company:
        return jsonify({
            "success": False,
            "error": f"Company {company_id} not found"
        }), 404
    
    # Get company jobs
    company_jobs = [j for j in JOBS_DB if j.get('company_id') == company_id]
    
    return jsonify({
        "success": True,
        "company": company,
        "jobs": company_jobs,
        "jobs_count": len(company_jobs)
    })

@app.route('/api/jobs/<job_id>/apply', methods=['POST'])
def apply_to_job(job_id):
    """Submit an application to a specific job with comprehensive validation."""
    
    # Find the job
    job = next((j for j in JOBS_DB if j['job_id'] == job_id), None)
    
    if not job:
        return jsonify({
            "success": False,
            "error": f"Job {job_id} not found"
        }), 404
    
    if job['status'] != 'active':
        return jsonify({
            "success": False,
            "error": f"Job {job_id} is no longer accepting applications"
        }), 400
    
    # Get application data
    application_data = request.get_json()
    
    if not application_data:
        return jsonify({
            "success": False,
            "error": "Application data is required"
        }), 400
    
    # Validate required fields
    required_fields = ['applicant_name', 'email', 'cover_letter', 'skills']
    missing_fields = [field for field in required_fields if not application_data.get(field)]
    
    if missing_fields:
        return jsonify({
            "success": False,
            "error": f"Missing required fields: {missing_fields}"
        }), 400
    
    # Validate email format
    import re
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, application_data['email']):
        return jsonify({
            "success": False,
            "error": "Invalid email format"
        }), 400
    
    # Generate application ID and receipt
    application_id = str(uuid.uuid4())
    receipt_id = f"RCP-{int(time.time())}-{random.randint(1000, 9999)}"
    
    # Create comprehensive application record
    application = {
        "application_id": application_id,
        "receipt_id": receipt_id,
        "job_id": job_id,
        "company": job['company'],
        "role": job['role'],
        "applicant_name": application_data['applicant_name'],
        "email": application_data['email'],
        "phone": application_data.get('phone', ''),
        "location": application_data.get('location', ''),
        "experience_years": application_data.get('experience_years', ''),
        "skills": application_data['skills'] if isinstance(application_data['skills'], list) else application_data['skills'].split(','),
        "current_role": application_data.get('current_role', ''),
        "education": application_data.get('education', ''),
        "cover_letter": application_data['cover_letter'],
        "availability": application_data.get('availability', ''),
        "salary_expectation": application_data.get('salary_expectation', ''),
        "resume_text": application_data.get('resume_text', ''),
        "applied_at": datetime.now().isoformat(),
        "status": "submitted",
        "portal_response": "Application received and under review",
        "screening_score": random.randint(70, 95),  # Simulate screening
        "next_steps": "HR review within 3-5 business days"
    }
    
    # Store application
    APPLICATIONS_DB.append(application)
    PORTAL_STATS["total_applications"] += 1
    
    # Update job application count
    job['applications_count'] = job.get('applications_count', 0) + 1
    
    # Simulate processing delay
    time.sleep(0.2)
    
    # Generate confirmation receipt
    receipt = {
        "application_id": application_id,
        "receipt_id": receipt_id,
        "job_title": f"{job['role']} at {job['company']}",
        "applicant_name": application_data['applicant_name'],
        "submitted_at": application['applied_at'],
        "status": "submitted",
        "confirmation_message": f"Your application for {job['role']} at {job['company']} has been successfully submitted.",
        "next_steps": [
            "Your application will be reviewed by our HR team within 3-5 business days",
            "If your profile matches our requirements, we'll contact you for next steps",
            "You can check your application status using your receipt ID: " + receipt_id
        ],
        "contact_info": {
            "hr_email": f"hr@{job['company'].lower().replace(' ', '')}.com",
            "phone": "+1 (555) 123-4567"
        }
    }
    
    return jsonify({
        "success": True,
        "application_id": application_id,
        "receipt_id": receipt_id,
        "message": "Application submitted successfully",
        "status": "submitted",
        "confirmation": f"Your application for {job['role']} at {job['company']} has been received",
        "receipt": receipt,
        "next_steps": "You will receive an email confirmation within 24 hours"
    })

@app.route('/api/applications', methods=['GET'])
def get_applications():
    """Get all applications submitted through the portal with filtering."""
    
    email = request.args.get('email')
    job_id = request.args.get('job_id')
    status = request.args.get('status')
    company = request.args.get('company')
    limit = request.args.get('limit', type=int)
    
    filtered_apps = APPLICATIONS_DB.copy()
    
    if email:
        filtered_apps = [a for a in filtered_apps if a['email'].lower() == email.lower()]
    
    if job_id:
        filtered_apps = [a for a in filtered_apps if a['job_id'] == job_id]
    
    if status:
        filtered_apps = [a for a in filtered_apps if a['status'] == status]
    
    if company:
        filtered_apps = [a for a in filtered_apps if company.lower() in a['company'].lower()]
    
    if limit:
        filtered_apps = filtered_apps[:limit]
    
    return jsonify({
        "success": True,
        "applications": filtered_apps,
        "total_count": len(filtered_apps),
        "filters_applied": {
            "email": email,
            "job_id": job_id,
            "status": status,
            "company": company
        }
    })

@app.route('/api/applications/<application_id>', methods=['GET'])
def get_application_status(application_id):
    """Get the status of a specific application."""
    
    application = next((a for a in APPLICATIONS_DB if a['application_id'] == application_id), None)
    
    if not application:
        return jsonify({
            "success": False,
            "error": f"Application {application_id} not found"
        }), 404
    
    return jsonify({
        "success": True,
        "application": application
    })

@app.route('/api/applications/<application_id>', methods=['DELETE'])
def delete_application(application_id):
    """Delete a specific application."""
    
    global APPLICATIONS_DB, PORTAL_STATS
    
    application = next((a for a in APPLICATIONS_DB if a['application_id'] == application_id), None)
    
    if not application:
        return jsonify({
            "success": False,
            "error": f"Application {application_id} not found"
        }), 404
    
    # Remove application from database
    APPLICATIONS_DB = [a for a in APPLICATIONS_DB if a['application_id'] != application_id]
    PORTAL_STATS["total_applications"] = len(APPLICATIONS_DB)
    
    # Update job application count
    job = next((j for j in JOBS_DB if j['job_id'] == application['job_id']), None)
    if job and job.get('applications_count', 0) > 0:
        job['applications_count'] -= 1
    
    return jsonify({
        "success": True,
        "message": f"Application {application_id} deleted successfully"
    })

@app.route('/api/applications/receipt/<receipt_id>', methods=['GET'])
def get_application_by_receipt(receipt_id):
    """Get application details by receipt ID."""
    
    application = next((a for a in APPLICATIONS_DB if a['receipt_id'] == receipt_id), None)
    
    if not application:
        return jsonify({
            "success": False,
            "error": f"Application with receipt {receipt_id} not found"
        }), 404
    
    return jsonify({
        "success": True,
        "application": application
    })

@app.route('/api/portal/reset', methods=['POST'])
def reset_portal():
    """Reset the sandbox portal (clear all applications, reinitialize jobs)."""
    
    global APPLICATIONS_DB, PORTAL_STATS
    APPLICATIONS_DB = []
    PORTAL_STATS["total_applications"] = 0
    
    initialize_sandbox_jobs()
    
    return jsonify({
        "success": True,
        "message": "Sandbox portal reset successfully",
        "stats": PORTAL_STATS
    })

if __name__ == '__main__':
    print("🏗️  Starting Comprehensive Sandbox Job Portal...")
    print("=" * 60)
    
    # Initialize data
    initialize_sandbox_companies()
    initialize_sandbox_jobs()
    
    print("=" * 60)
    print("🌐 Sandbox Portal running on http://localhost:5001")
    print("📋 Available endpoints:")
    print("   🏠  GET  / - Homepage with job listings")
    print("   📄  GET  /jobs - Browse all jobs")
    print("   🔍  GET  /jobs/<job_id> - Job details page")
    print("   📝  GET  /jobs/<job_id>/apply - Application form")
    print("   🏢  GET  /companies - Company listings")
    print("   �  GET  /applications - View all applications")
    print("   �  GET  /applications/<app_id> - ApAplication details")
    print("   ➕  GET  /company/post-job - Company job posting form")
    print("   📊  GET  /api/portal/status - Portal status")
    print("   📋  GET  /api/jobs - List all jobs (API)")
    print("   🔍  GET  /api/jobs/<job_id> - Job details (API)")
    print("   📝  POST /api/jobs/<job_id>/apply - Submit application (API)")
    print("   📄  GET  /api/applications - List applications (API)")
    print("   🏢  GET  /api/companies - List companies (API)")
    print("   ➕  POST /api/company/post-job - Post new job (API)")
    print("   🔄  POST /api/portal/reset - Reset portal data")
    print("=" * 60)
    print("✨ Features:")
    print("   • 100+ realistic job postings with detailed descriptions")
    print("   • Company profiles with benefits and culture info")
    print("   • Comprehensive application forms with validation")
    print("   • Application receipts and tracking")
    print("   • Application management interface for viewing submissions")
    print("   • Company job posting interface")
    print("   • Advanced filtering and search")
    print("   • Responsive web interface")
    print("   • RESTful API for automation")
    print("=" * 60)
    print()
    
    app.run(host='0.0.0.0', port=5001, debug=True)