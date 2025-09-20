"""
Enhanced text processing with spaCy and NLTK for better entity extraction
"""
import re
from typing import List, Dict, Tuple, Set
from dataclasses import dataclass

try:
    import spacy
    from spacy.matcher import Matcher
    SPACY_AVAILABLE = True
    
    # Try to load spaCy model
    try:
        nlp = spacy.load("en_core_web_sm")
    except OSError:
        # If model not found, use blank model
        nlp = spacy.blank("en")
        SPACY_AVAILABLE = False
except ImportError:
    SPACY_AVAILABLE = False
    nlp = None

try:
    import nltk
    from nltk.corpus import stopwords
    from nltk.tokenize import word_tokenize, sent_tokenize
    from nltk.stem import WordNetLemmatizer
    NLTK_AVAILABLE = True
    
    # Download required NLTK data
    try:
        nltk.data.find('tokenizers/punkt')
        nltk.data.find('corpora/stopwords')
        nltk.data.find('corpora/wordnet')
    except LookupError:
        nltk.download('punkt', quiet=True)
        nltk.download('stopwords', quiet=True)
        nltk.download('wordnet', quiet=True)
    
    stop_words = set(stopwords.words('english'))
    lemmatizer = WordNetLemmatizer()
    
except ImportError:
    NLTK_AVAILABLE = False
    stop_words = set()
    lemmatizer = None

@dataclass
class ExtractedEntities:
    """Structured data for extracted entities"""
    skills: List[str]
    experience_years: List[int]
    education: List[str]
    certifications: List[str]
    technologies: List[str]
    companies: List[str]
    locations: List[str]
    contact_info: Dict[str, str]

class AdvancedTextProcessor:
    """
    Advanced text processing using spaCy and NLTK for entity extraction and normalization
    """
    
    def __init__(self):
        self.skill_patterns = self._load_skill_patterns()
        self.tech_patterns = self._load_tech_patterns()
        self.education_patterns = self._load_education_patterns()
        
        if SPACY_AVAILABLE and nlp.has_pipe('ner'):
            self.matcher = Matcher(nlp.vocab)
            self._setup_custom_patterns()
    
    def _load_skill_patterns(self) -> List[str]:
        """Extended skill patterns for better detection"""
        return [
            # Programming Languages
            "python", "java", "javascript", "typescript", "c++", "c#", "go", "rust", "scala", "kotlin",
            "php", "ruby", "swift", "objective-c", "dart", "r", "matlab", "perl", "shell", "bash",
            
            # Web Technologies
            "html", "css", "react", "angular", "vue", "node.js", "express", "django", "flask", "fastapi",
            "bootstrap", "tailwind", "sass", "less", "webpack", "vite", "next.js", "nuxt.js",
            
            # Databases
            "sql", "mysql", "postgresql", "mongodb", "redis", "elasticsearch", "cassandra", "neo4j",
            "sqlite", "oracle", "sql server", "dynamodb", "firebase",
            
            # Cloud & DevOps
            "aws", "azure", "gcp", "docker", "kubernetes", "terraform", "ansible", "jenkins",
            "gitlab ci", "github actions", "ci/cd", "nginx", "apache", "linux", "ubuntu",
            
            # Data Science & ML
            "pandas", "numpy", "sklearn", "pytorch", "tensorflow", "keras", "jupyter", "matplotlib",
            "seaborn", "plotly", "apache spark", "hadoop", "airflow", "dbt", "tableau", "power bi",
            
            # Other Technologies
            "git", "jira", "confluence", "slack", "figma", "adobe", "photoshop", "illustrator"
        ]
    
    def _load_tech_patterns(self) -> List[str]:
        """Technology and framework patterns"""
        return [
            "machine learning", "artificial intelligence", "deep learning", "natural language processing",
            "computer vision", "data analysis", "data science", "big data", "blockchain", "microservices",
            "api development", "mobile development", "web development", "frontend", "backend", "full stack"
        ]
    
    def _load_education_patterns(self) -> List[str]:
        """Education degree patterns"""
        return [
            "bachelor", "master", "phd", "doctorate", "mba", "b.tech", "m.tech", "b.sc", "m.sc",
            "bca", "mca", "be", "me", "diploma", "certificate", "associate degree"
        ]
    
    def _setup_custom_patterns(self):
        """Setup custom spaCy patterns for better entity recognition"""
        if not hasattr(self, 'matcher'):
            return
            
        # Experience patterns
        experience_pattern = [
            [{"LOWER": {"IN": ["years", "year"]}}, {"LOWER": "of"}, {"LOWER": "experience"}],
            [{"LIKE_NUM": True}, {"LOWER": {"IN": ["years", "year", "yrs", "yr"]}}, {"LOWER": {"IN": ["experience", "exp"]}}],
            [{"LIKE_NUM": True}, {"LOWER": "+"}, {"LOWER": {"IN": ["years", "year", "yrs"]}}]
        ]
        
        for pattern in experience_pattern:
            self.matcher.add("EXPERIENCE", [pattern])
    
    def normalize_text(self, text: str) -> str:
        """Advanced text normalization"""
        # Remove special characters and normalize whitespace
        text = re.sub(r'[^\w\s\-\.]', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        
        # Remove common resume artifacts
        text = re.sub(r'\b(page \d+ of \d+|confidential|resume|cv)\b', '', text, flags=re.IGNORECASE)
        
        # Normalize common abbreviations
        replacements = {
            r'\byrs?\b': 'years',
            r'\bexp\b': 'experience',
            r'\btech\b': 'technology',
            r'\buniv\b': 'university',
            r'\bcert\b': 'certification'
        }
        
        for pattern, replacement in replacements.items():
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        
        return text.strip()
    
    def extract_entities(self, text: str) -> ExtractedEntities:
        """Extract structured entities from text"""
        normalized_text = self.normalize_text(text)
        
        return ExtractedEntities(
            skills=self._extract_skills(normalized_text),
            experience_years=self._extract_experience_years(normalized_text),
            education=self._extract_education(normalized_text),
            certifications=self._extract_certifications(normalized_text),
            technologies=self._extract_technologies(normalized_text),
            companies=self._extract_companies(normalized_text),
            locations=self._extract_locations(normalized_text),
            contact_info=self._extract_contact_info(normalized_text)
        )
    
    def _extract_skills(self, text: str) -> List[str]:
        """Extract technical skills from text"""
        text_lower = text.lower()
        found_skills = []
        
        for skill in self.skill_patterns:
            if skill.lower() in text_lower:
                found_skills.append(skill)
        
        # Use spaCy for additional skill extraction if available
        if SPACY_AVAILABLE and nlp.has_pipe('ner'):
            doc = nlp(text)
            for ent in doc.ents:
                if ent.label_ in ['PRODUCT', 'ORG'] and len(ent.text) > 2:
                    found_skills.append(ent.text)
        
        return list(set(found_skills))
    
    def _extract_experience_years(self, text: str) -> List[int]:
        """Extract years of experience"""
        experience_patterns = [
            r'(\d+)\s*(?:\+)?\s*(?:years?|yrs?)\s*(?:of\s*)?(?:experience|exp)',
            r'experience\s*[:\-]\s*(\d+)\s*(?:years?|yrs?)',
            r'(\d+)\s*(?:\+)?\s*(?:years?|yrs?)\s*in',
            r'over\s*(\d+)\s*(?:years?|yrs?)',
            r'more\s*than\s*(\d+)\s*(?:years?|yrs?)'
        ]
        
        years = []
        for pattern in experience_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            years.extend([int(match) for match in matches if match.isdigit()])
        
        return sorted(list(set(years)), reverse=True)
    
    def _extract_education(self, text: str) -> List[str]:
        """Extract education information"""
        education = []
        
        for degree in self.education_patterns:
            pattern = rf'\b{degree}[\w\s]*(?:in|of)\s+[\w\s]+(?:science|engineering|technology|business|arts|studies)?'
            matches = re.findall(pattern, text, re.IGNORECASE)
            education.extend(matches)
        
        return education
    
    def _extract_certifications(self, text: str) -> List[str]:
        """Extract certifications"""
        cert_patterns = [
            r'certified?\s+[\w\s]+(?:professional|specialist|expert|developer|administrator)',
            r'[\w\s]+\s+certification',
            r'aws\s+[\w\s]+(?:associate|professional)',
            r'microsoft\s+[\w\s]+(?:associate|expert)',
            r'google\s+[\w\s]+(?:associate|professional)',
            r'cisco\s+[\w\s]+(?:associate|professional)'
        ]
        
        certifications = []
        for pattern in cert_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            certifications.extend(matches)
        
        return certifications
    
    def _extract_technologies(self, text: str) -> List[str]:
        """Extract technology mentions"""
        technologies = []
        
        for tech in self.tech_patterns:
            if tech.lower() in text.lower():
                technologies.append(tech)
        
        return technologies
    
    def _extract_companies(self, text: str) -> List[str]:
        """Extract company names using spaCy NER"""
        companies = []
        
        if SPACY_AVAILABLE and nlp.has_pipe('ner'):
            doc = nlp(text)
            for ent in doc.ents:
                if ent.label_ == 'ORG':
                    companies.append(ent.text)
        
        return companies
    
    def _extract_locations(self, text: str) -> List[str]:
        """Extract location information"""
        locations = []
        
        if SPACY_AVAILABLE and nlp.has_pipe('ner'):
            doc = nlp(text)
            for ent in doc.ents:
                if ent.label_ in ['GPE', 'LOC']:
                    locations.append(ent.text)
        
        return locations
    
    def _extract_contact_info(self, text: str) -> Dict[str, str]:
        """Extract contact information"""
        contact = {}
        
        # Email pattern
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        if emails:
            contact['email'] = emails[0]
        
        # Phone pattern
        phone_pattern = r'[\+]?[1-9]?[\d\s\-\(\)]{8,15}\d'
        phones = re.findall(phone_pattern, text)
        if phones:
            contact['phone'] = phones[0]
        
        # LinkedIn pattern
        linkedin_pattern = r'linkedin\.com/in/[\w\-]+'
        linkedin = re.findall(linkedin_pattern, text, re.IGNORECASE)
        if linkedin:
            contact['linkedin'] = linkedin[0]
        
        return contact
    
    def get_text_summary(self, text: str) -> Dict[str, int]:
        """Get text statistics and summary"""
        if NLTK_AVAILABLE:
            sentences = sent_tokenize(text)
            words = word_tokenize(text.lower())
            words_no_stop = [word for word in words if word.isalnum() and word not in stop_words]
        else:
            sentences = text.split('.')
            words = text.split()
            words_no_stop = words
        
        return {
            'character_count': len(text),
            'word_count': len(words),
            'sentence_count': len(sentences),
            'unique_words': len(set(words_no_stop)),
            'avg_sentence_length': len(words) / max(len(sentences), 1)
        }

# Global instance
text_processor = AdvancedTextProcessor()