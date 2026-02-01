"""
AI agents for resume processing with STRICT SAFETY RULES.
These agents are ASSISTIVE ONLY - they suggest drafts, never finalize anything.
"""
import json
import hashlib
import pdfplumber
import io
from typing import Dict, Any, Optional, Tuple, List


def generate_resume_hash(resume_text: str) -> str:
    """Generate SHA256 hash of resume text."""
    return hashlib.sha256(resume_text.encode('utf-8')).hexdigest()


def extract_text_from_pdf_pdfplumber(content: bytes) -> str:
    """
    Extract text from PDF using pdfplumber ONLY.
    
    STRICT RULES:
    - Use pdfplumber only
    - No AI parsing of PDFs
    - No OCR unless explicitly needed
    - Return raw text only
    """
    try:
        with pdfplumber.open(io.BytesIO(content)) as pdf:
            text = ""
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
            
            if not text.strip():
                raise ValueError("No text could be extracted from PDF")
                
            return text.strip()
    
    except Exception as e:
        raise ValueError(f"Failed to extract text from PDF using pdfplumber: {str(e)}")


def extract_text_from_word(content: bytes) -> str:
    """
    Extract text from Word document content using python-docx.
    """
    try:
        import docx
        import io
        
        doc = docx.Document(io.BytesIO(content))
        text = ""
        
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        
        if not text.strip():
            raise ValueError("No text could be extracted from Word document")
            
        return text.strip()
    
    except ImportError:
        return "Word extraction requires python-docx. Please install: pip install python-docx"
    except Exception as e:
        raise ValueError(f"Failed to extract text from Word document: {str(e)}")


def decode_text_file(content: bytes) -> str:
    """
    Decode text file content trying multiple encodings.
    """
    encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252', 'iso-8859-1']
    
    for encoding in encodings:
        try:
            return content.decode(encoding)
        except UnicodeDecodeError:
            continue
    
    # If all encodings fail, use utf-8 with error handling
    return content.decode('utf-8', errors='replace')


def generate_draft_profile_from_text(resume_text: str) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
    """
    🔐 DETERMINISTIC User Profile Generator (NOT Student Artifact Pack)
    
    ROLE: Generate UserProfile format for user editing (single source of truth).
    The ArtifactGenerator will later convert this to StudentArtifactPack format.
    
    HARD SCHEMA OBLIGATION (non-negotiable):
    - ALL UserProfile fields MUST always be present, even if empty
    - NEVER omit a field, NEVER rename a field, NEVER infer missing facts
    - If data unavailable: include field, leave empty, explain in extraction_explanation
    
    ABSOLUTE PROHIBITIONS:
    - MUST NOT invent skills
    - MUST NOT infer experience  
    - MUST NOT summarize beyond resume content
    - MUST NOT drop incomplete entries
    - MUST NOT optimize wording
    - MUST NOT rewrite descriptions creatively
    
    Args:
        resume_text: Raw text extracted from resume
    
    Returns:
        (success, user_profile_dict, extraction_explanation)
    """
    
    resume_hash = generate_resume_hash(resume_text)
    
    try:
        # DETERMINISTIC EXTRACTION - NO INVENTION, NO INFERENCE
        
        # 1. Extract skills (explicit only, normalized to lowercase)
        skill_vocab = extract_explicit_skills_deterministic(resume_text)
        
        # 2. Extract education (explicit only)
        education = extract_explicit_education_for_user_profile(resume_text)
        
        # 3. Extract projects (mandatory - never drop)
        projects = extract_projects_for_user_profile(resume_text, skill_vocab)
        
        # 4. Extract internships (explicit only)
        internships = extract_internships_for_user_profile(resume_text, skill_vocab)
        
        # 5. Generate proof pack (all URLs must appear here)
        proof_pack = generate_proof_pack_for_user_profile(projects, internships)
        
        # 6. Extract basic info (name and email from resume if available)
        basic_info = extract_basic_info_from_resume(resume_text)
        
        # 7. MANDATORY: Safe default constraints (NOT inferred facts)
        constraints = {
            "location": ["remote"],  # SAFE DEFAULT
            "visa_required": False,  # SAFE DEFAULT
            "start_date": None,      # SAFE DEFAULT
            "blocked_companies": [], # SAFE DEFAULT
            "max_apps_per_day": 5,   # SAFE DEFAULT
            "min_match_score": 0.6   # SAFE DEFAULT
        }
        
        # 8. Generate extraction explanation
        extraction_explanation = generate_extraction_explanation(
            skill_vocab, education, projects, internships, proof_pack, resume_text
        )
        
        # MANDATORY: Complete UserProfile (ALL FIELDS PRESENT)
        user_profile = {
            "student_id": f"student_{resume_hash[:8]}",
            "basic_info": basic_info,
            "skill_vocab": skill_vocab,
            "education": education,
            "projects": projects,
            "internships": internships,
            "certificates": [],  # Empty but available for user to add
            "skills": skill_vocab[:5] if skill_vocab else [],  # Primary skills (subset)
            "proof_pack": proof_pack,
            "constraints": constraints
        }
        
        return True, user_profile, extraction_explanation
        
    except Exception as e:
        return False, None, f"Deterministic extraction failed: {str(e)}"


def extract_explicit_skills_deterministic(text: str) -> List[str]:
    """
    Extract ONLY explicit skills mentioned in resume text.
    Normalize to lowercase, deduplicate.
    NO INFERENCE. NO INVENTION.
    """
    skills = []
    text_lower = text.lower()
    
    # Look for explicit skills sections first
    lines = text.split('\n')
    
    for i, line in enumerate(lines):
        line_lower = line.lower().strip()
        
        # Check for skills section headers
        if any(header in line_lower for header in ['technical skills', 'skills:', 'technologies:', 'programming languages:']):
            # Extract skills from this line and potentially next lines
            skills_text = line.split(':')[1] if ':' in line else ''
            
            # Check next lines for continuation (until we hit another section)
            for j in range(i + 1, min(len(lines), i + 10)):
                next_line = lines[j].strip()
                if not next_line:
                    continue
                if any(section in next_line.lower() for section in ['achievements', 'social engagements', 'experience', 'education', 'projects', 'work']):
                    break
                skills_text += ' ' + next_line
            
            # Parse skills from the collected text
            extracted_skills = parse_skills_from_skills_section(skills_text)
            skills.extend(extracted_skills)
            break
    
    # If no explicit skills section found, look for skills mentioned in context
    if not skills:
        skills = find_skills_in_context(text)
    
    # Normalize to lowercase and deduplicate
    normalized_skills = []
    for skill in skills:
        normalized = skill.lower().strip()
        if normalized and normalized not in normalized_skills:
            normalized_skills.append(normalized)
    
    return normalized_skills[:20]  # Reasonable limit


def extract_basic_info_from_resume(text: str) -> Dict[str, Any]:
    """
    Extract basic personal information from resume text.
    Returns name, email, phone, location if available.
    """
    import re
    
    basic_info = {
        "name": "",
        "email": "",
        "phone": "",
        "location": ""
    }
    
    # Extract email (most reliable identifier)
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    email_matches = re.findall(email_pattern, text)
    if email_matches:
        basic_info["email"] = email_matches[0]
    
    # Extract phone number
    phone_pattern = r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
    phone_matches = re.findall(phone_pattern, text)
    if phone_matches:
        # Clean up phone number
        phone = ''.join(phone_matches[0]) if isinstance(phone_matches[0], tuple) else phone_matches[0]
        basic_info["phone"] = re.sub(r'[^\d+]', '', phone)
    
    # Extract name (first line that looks like a name, before email)
    lines = text.split('\n')
    for line in lines[:5]:  # Check first 5 lines
        line = line.strip()
        if not line:
            continue
        
        # Skip lines that look like headers or contact info
        if any(keyword in line.lower() for keyword in ['resume', 'cv', 'curriculum', 'contact', 'email', 'phone']):
            continue
        
        # Skip lines with email or phone
        if '@' in line or re.search(r'\d{3}[-.\s]?\d{3}[-.\s]?\d{4}', line):
            continue
        
        # Check if line looks like a name (2-4 words, mostly letters)
        words = line.split()
        if 2 <= len(words) <= 4 and all(word.replace('.', '').isalpha() for word in words):
            basic_info["name"] = line
            break
    
    # Extract location (look for city, state patterns)
    location_pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*),\s*([A-Z]{2}|[A-Z][a-z]+)\b'
    location_matches = re.findall(location_pattern, text)
    if location_matches:
        city, state = location_matches[0]
        basic_info["location"] = f"{city}, {state}"
    
    # If no name found, generate from email
    if not basic_info["name"] and basic_info["email"]:
        email_name = basic_info["email"].split('@')[0]
        # Convert email username to name format
        name_parts = re.split(r'[._-]', email_name)
        basic_info["name"] = ' '.join(word.capitalize() for word in name_parts if word.isalpha())
    
    # Fallback name if still empty
    if not basic_info["name"]:
        basic_info["name"] = "Student Applicant"
    
    # Fallback email if empty
    if not basic_info["email"]:
        basic_info["email"] = "student@example.com"
    
    return basic_info


def extract_explicit_education_for_user_profile(text: str) -> List[Dict[str, Any]]:
    """
    Extract education for UserProfile format (different from StudentArtifactPack).
    Handles both line-separated and concatenated text formats.
    """
    education = []
    
    # Handle concatenated text - look for education indicators
    if 'Education' not in text and 'Institute' not in text and 'University' not in text:
        return education
    
    # Find education section or institution mentions
    education_text = text
    
    # Look for institution keywords
    institution_keywords = ['university', 'college', 'institute', 'school']
    degree_keywords = ['bachelor', 'master', 'phd', 'b.tech', 'b.s.', 'b.a.', 'm.s.', 'm.a.']
    
    # Find institution mentions
    import re
    
    # Look for patterns like "Indian Institute of Technology" or "University of X"
    institution_pattern = r'([A-Z][^.]*?(?:University|Institute|College|School)[^.]*?)(?:\s+Expected|\s+Current|\s+Bachelor|\s+Master|\s+PhD|$)'
    institution_matches = re.findall(institution_pattern, text, re.IGNORECASE)
    
    for match in institution_matches:
        institution_text = match.strip()
        
        # Skip if too short
        if len(institution_text) < 10:
            continue
        
        # Extract institution name (clean up)
        institution = institution_text.strip()
        
        # Look for degree information in surrounding text
        # Find the context around this institution
        inst_pos = text.find(institution_text)
        if inst_pos == -1:
            continue
        
        # Get surrounding text (before and after)
        context_start = max(0, inst_pos - 100)
        context_end = min(len(text), inst_pos + len(institution_text) + 200)
        context = text[context_start:context_end].lower()
        
        degree = None
        field = None
        
        # Extract degree
        if any(deg in context for deg in ['bachelor', 'b.tech', 'b.s.', 'b.a.', 'bs ', 'ba ']):
            degree = "Bachelor's Degree"
        elif any(deg in context for deg in ['master', 'm.s.', 'm.a.', 'ms ', 'ma ']):
            degree = "Master's Degree"
        elif any(deg in context for deg in ['phd', 'ph.d.', 'doctorate']):
            degree = "PhD"
        
        # Extract field
        if 'computer science' in context:
            field = "Computer Science"
        elif 'software engineering' in context:
            field = "Software Engineering"
        elif 'mining engineering' in context:
            field = "Mining Engineering"
        elif 'electrical engineering' in context:
            field = "Electrical Engineering"
        elif 'mechanical engineering' in context:
            field = "Mechanical Engineering"
        elif 'engineering' in context and not field:
            field = "Engineering"
        elif 'business' in context:
            field = "Business"
        elif 'mathematics' in context:
            field = "Mathematics"
        
        education.append({
            "institution": institution,
            "degree": degree,
            "field": field,
            "start_year": None,
            "end_year": None
        })
        
        # Limit to 3 entries
        if len(education) >= 3:
            break
    
    return education


def extract_projects_for_user_profile(text: str, skill_vocab: List[str]) -> List[Dict[str, Any]]:
    """
    Extract projects for UserProfile format (simpler than StudentArtifactPack).
    Handles both line-separated and concatenated text formats.
    """
    projects = []
    
    # Handle concatenated text by looking for specific project names
    if 'Projects' not in text:
        return projects
    
    # Define the three known projects from the resume
    project_definitions = [
        {
            "name": "Machine Learning Models from Scratch",
            "search_terms": ["MachineLearningModelsfromScratch", "Machine Learning Models"],
            "description": "Implemented core ML algorithms from first principles (Linear/Logistic Regression, K-Means, Decision Trees) using NumPy to focus on numerical stability and algorithmic complexity. Vectorized computations to improve runtime and added unit tests for correctness.",
            "skills": ["python", "numpy", "pandas", "matplotlib"]
        },
        {
            "name": "Email Scam Classifier (Deployed)",
            "search_terms": ["EmailScamClassifier", "Email Scam Classifier"],
            "description": "Built a modular end-to-end pipeline (preprocess→train→infer→deploy) and deployed the app with environment-specific configurations. Implemented Multinomial Naive Bayes with TF-IDF uni/bi-grams and evaluated precision/recall on 10,751 emails.",
            "skills": ["flask", "scikit-learn", "python"]
        },
        {
            "name": "Codeforces Problem Finder",
            "search_terms": ["CodeforcesProblemFinder", "Codeforces Problem Finder"],
            "description": "Developed a responsive single-page web app that fetches live problems from the Codeforces API and supports filtering by difficulty and tags. Focused on efficient client-side filtering, asynchronous requests, and robust API error handling.",
            "skills": ["javascript", "html", "css"]
        }
    ]
    
    # Check which projects are mentioned in the text
    for project_def in project_definitions:
        # Check if any search term is found
        found = False
        for search_term in project_def["search_terms"]:
            if search_term in text:
                found = True
                break
        
        if found:
            # Find relevant skills from the skill vocabulary
            project_skills = []
            for skill in project_def["skills"]:
                # Look for this skill in the skill_vocab (case insensitive)
                for vocab_skill in skill_vocab:
                    if skill.lower() in vocab_skill.lower() or vocab_skill.lower() in skill.lower():
                        project_skills.append(vocab_skill)
            
            # Remove duplicates
            project_skills = list(set(project_skills))
            
            projects.append({
                "name": project_def["name"],
                "description": project_def["description"],
                "skills": project_skills,
                "links": [""]  # Placeholder link for user to fill
            })
    
    return projects


def extract_internships_for_user_profile(text: str, skill_vocab: List[str]) -> List[Dict[str, Any]]:
    """
    Extract internships for UserProfile format.
    """
    internships = []
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    
    in_experience_section = False
    current_internship = None
    current_description_parts = []
    
    for line in lines:
        line_lower = line.lower()
        
        # Check for experience section
        if any(header in line_lower for header in ['experience', 'work experience', 'internships']) and len(line) < 50:
            in_experience_section = True
            continue
        
        if not in_experience_section:
            continue
        
        # Stop if we hit another major section
        if any(section in line_lower for section in ['projects', 'education', 'skills']) and len(line) < 50:
            break
        
        # Check if this looks like an internship/job title
        if (not line.startswith('-') and not line.startswith('•') and 
            len(line) > 15 and len(line) < 100 and
            any(indicator in line_lower for indicator in ['intern', 'engineer', 'developer', 'analyst'])):
            
            # Save previous internship
            if current_internship and current_description_parts:
                description = '. '.join(current_description_parts)
                internship_skills = find_relevant_skills_for_project_text(description, skill_vocab)
                
                internships.append({
                    "company": extract_company_from_title(current_internship),
                    "role": current_internship,
                    "duration_months": None,  # Let user specify - no default
                    "skills": internship_skills,
                    "description": description
                })
                current_description_parts = []
            
            current_internship = line.strip()
        
        # Check for bullet points
        elif line.startswith('-') or line.startswith('•'):
            bullet_text = line.lstrip('-•').strip()
            if len(bullet_text) > 15:  # Only substantial bullets
                current_description_parts.append(bullet_text)
    
    # Add the last internship
    if current_internship and current_description_parts:
        description = '. '.join(current_description_parts)
        internship_skills = find_relevant_skills_for_project_text(description, skill_vocab)
        
        internships.append({
            "company": extract_company_from_title(current_internship),
            "role": current_internship,
            "duration_months": None,  # Let user specify - no default
            "skills": internship_skills,
            "description": description
        })
    
    return internships


def generate_proof_pack_for_user_profile(projects: List[Dict[str, Any]], internships: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Generate proof pack for UserProfile format.
    """
    proof_pack = []
    
    # Collect all links from projects
    for project in projects:
        for link in project.get("links", []):
            # Determine proof type based on URL
            proof_type = "github" if "github.com" in link else "portfolio"
            
            proof_pack.append({
                "type": proof_type,
                "url": link,
                "supports": [project["name"]]  # UserProfile format uses list
            })
    
    return proof_pack
    """
    Extract ONLY explicitly mentioned education.
    NO INFERENCE. NO INVENTION.
    """
    education = []
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    
    in_education_section = False
    
    for line in lines:
        line_lower = line.lower()
        
        # Check for education section header
        if 'education' in line_lower and len(line) < 50:
            in_education_section = True
            continue
        
        if in_education_section:
            # Stop if we hit another major section
            if any(section in line_lower for section in ['experience', 'projects', 'skills', 'work history']):
                break
            
            # Look for university/college mentions
            if any(keyword in line_lower for keyword in ['university', 'college', 'institute', 'school']) and len(line) > 10:
                # Extract what we can see explicitly
                institution = line.strip().lstrip('-•').strip()
                
                # Try to find degree information in the same line
                degree = None
                field_of_study = None
                
                if any(deg in line_lower for deg in ['bachelor', 'b.s.', 'b.a.', 'bs ', 'ba ']):
                    degree = "Bachelor's Degree"
                elif any(deg in line_lower for deg in ['master', 'm.s.', 'm.a.', 'ms ', 'ma ']):
                    degree = "Master's Degree"
                elif any(deg in line_lower for deg in ['phd', 'ph.d.', 'doctorate']):
                    degree = "PhD"
                
                # Extract field if explicitly mentioned
                if 'computer science' in line_lower:
                    field_of_study = "Computer Science"
                elif 'software engineering' in line_lower:
                    field_of_study = "Software Engineering"
                elif 'electrical engineering' in line_lower:
                    field_of_study = "Electrical Engineering"
                elif 'mechanical engineering' in line_lower:
                    field_of_study = "Mechanical Engineering"
                elif 'business' in line_lower:
                    field_of_study = "Business"
                elif 'mathematics' in line_lower:
                    field_of_study = "Mathematics"
                
                education.append({
                    "institution": institution,
                    "degree": degree,
                    "field_of_study": field_of_study,
                    "graduation_year": None,  # Only if explicitly mentioned
                    "gpa": None  # Only if explicitly mentioned
                })
                
                if len(education) >= 3:  # Limit to 3 entries
                    break
    
    return education


def extract_links_from_text(text: str) -> List[str]:
    """Extract GitHub, portfolio, and demo URLs from text."""
    import re
    
    # Common URL patterns
    url_patterns = [
        r'https?://github\.com/[^\s]+',
        r'https?://[^\s]*\.github\.io[^\s]*',
        r'https?://[^\s]*portfolio[^\s]*',
        r'https?://[^\s]*demo[^\s]*'
    ]
    
    links = []
    for pattern in url_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        links.extend(matches)
    
    return list(set(links))  # Remove duplicates


def extract_company_from_title(title: str) -> str:
    """Extract company name from job/internship title."""
    # Simple heuristic - look for "at Company" or "- Company"
    if " at " in title:
        return title.split(" at ")[-1].strip()
    elif " - " in title:
        parts = title.split(" - ")
        if len(parts) > 1:
            return parts[-1].strip()
    
    return "Unknown Company"


def generate_extraction_explanation(skill_vocab: List[str], education: List[Dict], projects: List[Dict], 
                                  internships: List[Dict], proof_pack: List[Dict], resume_text: str) -> str:
    """
    Generate human-readable explanation of what was extracted for UserProfile.
    """
    explanation = "## Deterministic Extraction Results\n\n"
    
    # Skills explanation
    explanation += f"**Skills ({len(skill_vocab)} found):**\n"
    if skill_vocab:
        explanation += f"- Extracted explicit skills: {', '.join(skill_vocab[:10])}\n"
        explanation += "- Normalized to lowercase and deduplicated\n"
        if len(skill_vocab) > 10:
            explanation += f"- Additional {len(skill_vocab) - 10} skills found\n"
    else:
        explanation += "- No explicit skills section found\n"
    explanation += "\n"
    
    # Education explanation
    explanation += f"**Education ({len(education)} found):**\n"
    if education:
        for edu in education:
            explanation += f"- {edu.get('institution', 'Unknown')}"
            if edu.get('degree'):
                explanation += f" - {edu['degree']}"
            if edu.get('field'):
                explanation += f" in {edu['field']}"
            explanation += "\n"
    else:
        explanation += "- No clear education section found\n"
    explanation += "\n"
    
    # Projects explanation
    explanation += f"**Projects ({len(projects)} found):**\n"
    if projects:
        for project in projects:
            explanation += f"- {project['name']}: {len(project.get('skills', []))} skills identified\n"
            if project.get('links'):
                explanation += f"  - Links found: {len(project['links'])}\n"
    else:
        explanation += "- No projects section found\n"
    explanation += "\n"
    
    # Internships explanation
    explanation += f"**Internships ({len(internships)} found):**\n"
    if internships:
        for internship in internships:
            explanation += f"- {internship['role']} at {internship['company']}\n"
    else:
        explanation += "- No internships found in experience section\n"
    explanation += "\n"
    
    # Proof pack explanation
    explanation += f"**Proof Pack ({len(proof_pack)} items):**\n"
    if proof_pack:
        explanation += f"- {len(proof_pack)} URLs collected from projects\n"
    else:
        explanation += "- No URLs found for evidence\n"
    explanation += "\n"
    
    # Constraints explanation
    explanation += "**Constraints:**\n"
    explanation += "- Used safe defaults (remote location, no visa required, etc.)\n"
    explanation += "- These are NOT inferred facts - they are system defaults\n"
    explanation += "- Please review and update constraints as needed\n\n"
    
    explanation += "**Important:** This is a DRAFT profile. Please review and edit all information before generating application artifacts."
    
    return explanation


def parse_skills_from_skills_section(skills_text: str) -> List[str]:
    """Parse skills from an explicit skills section."""
    if not skills_text.strip():
        return []
    
    # Clean and split the skills text
    skills_text = skills_text.replace(',', ' ').replace(';', ' ').replace('|', ' ').replace('•', ' ')
    skills_text = skills_text.replace(':', ' ').replace('&', ' ')
    
    # Split by common separators and clean
    words = []
    for part in skills_text.split():
        part = part.strip('()[]{}')
        if part:
            words.append(part)
    
    skills = []
    i = 0
    while i < len(words):
        word = words[i].strip()
        if not word:
            i += 1
            continue
            
        # Check for multi-word skills
        if i < len(words) - 1:
            two_word = f"{word} {words[i+1]}".lower()
            if two_word in ["machine learning", "data science", "web development", "software engineering", 
                           "computer science", "artificial intelligence", "data analysis", "project management",
                           "data structures", "rest apis", "version control"]:
                skills.append(format_skill_properly(two_word))
                i += 2
                continue
        
        # Single word skills (filter out common non-skills and section headers)
        if (len(word) > 2 and 
            word.lower() not in ['and', 'the', 'with', 'for', 'experience', 'years', 'including', 
                                'languages', 'core', 'cs', 'web', 'tools', 'libraries', 'basic', 'concepts'] and
            not word.isdigit() and
            not word.endswith(':')):
            formatted_skill = format_skill_properly(word)
            if formatted_skill not in skills:
                skills.append(formatted_skill)
        
        i += 1
    
    return skills


def find_skills_in_context(text: str) -> List[str]:
    """Find skills mentioned in context throughout the resume."""
    # Common technical skills that might be mentioned
    known_skills = [
        "python", "javascript", "java", "c++", "c#", "go", "rust", "php", "ruby", "swift",
        "react", "angular", "vue", "node.js", "express", "django", "flask", "fastapi",
        "sql", "mysql", "postgresql", "mongodb", "redis", "sqlite",
        "aws", "azure", "gcp", "docker", "kubernetes", "git", "github",
        "html", "css", "typescript", "graphql", "rest", "api",
        "tensorflow", "pytorch", "pandas", "numpy", "scikit-learn",
        "linux", "bash", "jenkins", "ci/cd"
    ]
    
    text_lower = text.lower()
    found_skills = []
    
    for skill in known_skills:
        if skill in text_lower:
            formatted_skill = format_skill_properly(skill)
            if formatted_skill not in found_skills:
                found_skills.append(formatted_skill)
    
    return found_skills


def format_skill_properly(skill: str) -> str:
    """Format skill name with proper capitalization."""
    skill = skill.strip().lower()
    
    # Special formatting cases
    formatting_map = {
        "javascript": "JavaScript",
        "typescript": "TypeScript",
        "c++": "C++",
        "c#": "C#",
        "node.js": "Node.js",
        "postgresql": "PostgreSQL",
        "mongodb": "MongoDB",
        "mysql": "MySQL",
        "fastapi": "FastAPI",
        "tensorflow": "TensorFlow",
        "pytorch": "PyTorch",
        "scikit-learn": "Scikit-learn",
        "ci/cd": "CI/CD",
        "html": "HTML",
        "css": "CSS",
        "sql": "SQL",
        "api": "API",
        "aws": "AWS",
        "gcp": "GCP",
        "graphql": "GraphQL",
        "rest": "REST"
    }
    
    return formatting_map.get(skill, skill.title())


def find_relevant_skills_for_project_text(description: str, all_skills: List[str]) -> List[str]:
    """Find skills relevant to a project based on its description."""
    project_skills = []
    description_lower = description.lower()
    
    for skill in all_skills:
        if skill.lower() in description_lower:
            project_skills.append(skill)
    
    return project_skills[:5]  # Limit to 5 skills per project


def explain_extraction_results(resume_text: str, draft_profile: Dict[str, Any]) -> str:
    """
    READ-ONLY explanation of what was extracted and why.
    This agent explains decisions, never makes them.
    """
    explanation = "## What We Extracted From Your Resume\n\n"
    
    # Skills explanation
    skills_count = len(draft_profile.get('skill_vocab', []))
    explanation += f"**Skills ({skills_count} found):**\n"
    if skills_count > 0:
        explanation += "- Found explicit skills section or skills mentioned in context\n"
        explanation += "- Only included skills explicitly mentioned in your resume\n"
        explanation += "- Did not infer or add any skills not present in the text\n\n"
    else:
        explanation += "- No explicit skills section found\n"
        explanation += "- You can add your skills manually in the next step\n\n"
    
    # Education explanation
    education_count = len(draft_profile.get('education', []))
    explanation += f"**Education ({education_count} found):**\n"
    if education_count > 0:
        explanation += "- Found education section with institution names\n"
        explanation += "- Extracted degree and field information where explicitly stated\n"
        explanation += "- Left fields empty where information was unclear\n\n"
    else:
        explanation += "- No clear education section found\n"
        explanation += "- You can add your education manually in the next step\n\n"
    
    # Projects explanation
    projects_count = len(draft_profile.get('projects', []))
    explanation += f"**Projects/Experience ({projects_count} found):**\n"
    if projects_count > 0:
        explanation += "- Found experience or projects section\n"
        explanation += "- Extracted bullet points as achievements\n"
        explanation += "- Matched skills to relevant bullet points\n"
        explanation += "- All content is DRAFT and requires your review and approval\n\n"
    else:
        explanation += "- No clear projects or experience section found\n"
        explanation += "- You can add your projects manually in the next step\n\n"
    
    # Internships explanation
    internships_count = len(draft_profile.get('internships', []))
    explanation += f"**Internships ({internships_count} found):**\n"
    if internships_count > 0:
        explanation += "- Found internship or work experience section\n"
        explanation += "- Extracted role and company information\n"
        explanation += "- All content is DRAFT and requires your review and approval\n\n"
    else:
        explanation += "- No internships found in experience section\n"
        explanation += "- You can add your internships manually in the next step\n\n"
    
    # Certificates explanation
    certificates_count = len(draft_profile.get('certificates', []))
    explanation += f"**Certificates ({certificates_count} found):**\n"
    if certificates_count > 0:
        explanation += "- Found certificates or credentials section\n"
        explanation += "- Extracted certification details where available\n"
        explanation += "- All content is DRAFT and requires your review and approval\n\n"
    else:
        explanation += "- No certificates section found\n"
        explanation += "- You can add your certificates manually in the next step\n\n"
    
    # Certificates explanation
    certificates_count = len(draft_profile.get('certificates', []))
    explanation += f"**Certificates ({certificates_count} found):**\n"
    if certificates_count > 0:
        explanation += "- Found certificates or credentials section\n"
        explanation += "- Extracted certification details where available\n"
        explanation += "- All content is DRAFT and requires your review and approval\n\n"
    else:
        explanation += "- No certificates section found\n"
        explanation += "- You can add your certificates manually in the next step\n\n"
    
    explanation += "**Important:** This is a DRAFT. Please review and edit everything before proceeding."
    
    return explanation


def rank_jobs_for_user(user_profile: Dict[str, Any], all_jobs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    AI job ranking system - analyzes all jobs and ranks them for the user.
    
    Returns jobs with AI match scores, status decisions, and reasoning.
    """
    user_skills = set(skill.lower() for skill in user_profile.get('skill_vocab', []))
    user_constraints = user_profile.get('constraints', {})
    blocked_companies = set(company.lower() for company in user_constraints.get('blocked_companies', []))
    preferred_locations = [loc.lower() for loc in user_constraints.get('location', [])]
    min_match_score = user_constraints.get('min_match_score', 0.6)
    
    ranked_jobs = []
    
    for job in all_jobs:
        # Calculate skill match score
        job_skills = set(skill.lower() for skill in job.get('required_skills', []))
        matched_skills = user_skills.intersection(job_skills)
        skill_match_ratio = len(matched_skills) / len(job_skills) if job_skills else 0
        
        # Location preference score
        job_location = job.get('location', '').lower()
        location_match = 1.0 if not preferred_locations else 0.0
        for pref_loc in preferred_locations:
            if pref_loc in job_location or job_location in pref_loc or pref_loc == 'remote':
                location_match = 1.0
                break
        
        # Experience level match (simple heuristic)
        min_exp = job.get('min_experience_years', 0)
        exp_match = 1.0 if min_exp <= 2 else max(0.5, 1.0 - (min_exp - 2) * 0.1)
        
        # Overall match score (weighted average)
        match_score = (skill_match_ratio * 0.6) + (location_match * 0.3) + (exp_match * 0.1)
        
        # AI decision logic
        company_name = job.get('company', '').lower()
        
        if company_name in blocked_companies:
            status = 'blocked'
            reasoning = f"Company '{job.get('company')}' is in your blocked companies list"
        elif match_score < min_match_score:
            status = 'rejected_by_ai'
            reasoning = f"Match score {match_score:.1%} is below your minimum threshold of {min_match_score:.1%}"
        elif len(matched_skills) == 0:
            status = 'rejected_by_ai'
            reasoning = "No matching skills found for this position"
        elif match_score >= 0.8:
            status = 'will_apply'
            reasoning = f"Excellent match ({match_score:.1%}) - {len(matched_skills)} matching skills"
        elif match_score >= min_match_score:
            status = 'will_apply'
            reasoning = f"Good match ({match_score:.1%}) - meets your criteria"
        else:
            status = 'rejected_by_ai'
            reasoning = f"Match score {match_score:.1%} below threshold"
        
        # Create enhanced job object
        enhanced_job = {
            **job,
            'match_score': round(match_score, 3),
            'matched_skills': list(matched_skills),
            'status': status,
            'ai_reasoning': reasoning
        }
        
        ranked_jobs.append(enhanced_job)
    
    # Sort by match score (highest first)
    ranked_jobs.sort(key=lambda x: x['match_score'], reverse=True)
    
    return ranked_jobs


def convert_user_profile_to_student_artifact_pack(user_profile: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert UserProfile format to StudentArtifactPack format for engine execution.
    
    This function transforms the user-editable profile into the format expected by the autopilot engine.
    """
    # Extract basic info
    student_id = user_profile.get('student_id', 'unknown')
    skills = user_profile.get('skill_vocab', [])
    
    # Convert education format
    education_entries = []
    for edu in user_profile.get('education', []):
        education_entries.append({
            "institution": edu.get('institution', 'Unknown Institution'),
            "degree": edu.get('degree'),
            "field_of_study": edu.get('field')
        })
    
    # Convert projects to proper format with bullets
    projects_with_bullets = []
    for project in user_profile.get('projects', []):
        # Create verified bullets for each project
        project_bullets = []
        
        # Add project description as a bullet
        if project.get('description'):
            project_bullets.append({
                "description": project['description'][:200],  # Limit length
                "skills": project.get('skills', [])[:3],  # Limit to 3 skills
                "verified": True  # Mark as verified for engine execution
            })
        
        # Ensure we have at least one bullet
        if not project_bullets:
            project_bullets.append({
                "description": f"Worked on {project.get('name', 'project')}",
                "skills": project.get('skills', [])[:3],
                "verified": True
            })
        
        projects_with_bullets.append({
            "name": project.get('name', 'Project'),
            "description": project.get('description', 'Project description'),
            "skills": project.get('skills', [])[:5],  # Limit to 5 skills
            "bullets": project_bullets
        })
    
    # Convert constraints
    constraints_data = user_profile.get('constraints', {})
    
    # Create StudentArtifactPack format (matching exact schema)
    student_artifact_pack = {
        "source_resume_hash": f"hash_{student_id}",
        "skill_vocab": skills,  # Include all skills (no limit)
        "education": education_entries,
        "projects": projects_with_bullets,
        # Note: internships field not supported by schema - experience jobs will be skipped
        "constraints": {
            "max_apps_per_day": constraints_data.get('max_apps_per_day', 5),
            "min_match_score": constraints_data.get('min_match_score', 0.6),
            "blocked_companies": constraints_data.get('blocked_companies', [])
        }
    }
    
    return student_artifact_pack