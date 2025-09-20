# 🎯 AI Resume Evaluation Engine (Production Ready)

An advanced AI-powered resume evaluation system that combines rule-based checks with LLM-powered semantic understanding, featuring vector stores, advanced entity extraction, and comprehensive analytics.

## 🚀 Key Features

### 📄 **Document Processing**
- **Multi-format Support**: PDF and DOCX resume/JD uploads
- **Advanced Text Extraction**: Clean, normalized text processing
- **Entity Recognition**: Extract skills, experience, education, certifications
- **Smart Parsing**: Automatic skill categorization from job descriptions

### 🧠 **AI-Powered Analysis**
- **Hybrid Scoring**: Rule-based (60%) + Semantic (40%) evaluation
- **LLM Integration**: OpenAI GPT, Google Gemini, Claude support
- **Vector Store**: Chroma DB for semantic search and similarity
- **Advanced NLP**: spaCy and NLTK for entity extraction
- **Confidence Scoring**: AI reliability indicators

### 📊 **Comprehensive Evaluation**
- **Relevance Score**: 0-100% with detailed breakdown
- **Missing Skills**: Identify gaps in candidate profiles
- **Strengths Analysis**: Highlight candidate advantages
- **Improvement Suggestions**: AI-generated feedback
- **Verdict System**: High/Medium/Low suitability ratings

### 🎨 **Beautiful Interface**
- **Modern UI**: Gradient designs, interactive charts
- **Real-time Analytics**: Live dashboards with Plotly visualizations
- **Progressive Enhancement**: Works with/without LLM features
- **Mobile Responsive**: Works on all device sizes
- **Status Indicators**: Real-time system capability display

### 🔌 **Dual Architecture**
- **Streamlit Frontend**: Beautiful, interactive web interface
- **FastAPI Backend**: REST API for integrations and scalability
- **Database Layer**: SQLite with SQLAlchemy ORM
- **Vector Storage**: Persistent embeddings with Chroma

## 🛠️ Tech Stack

### **Core AI & ML**
- **Python 3.11+** - Primary programming language
- **LangChain** - LLM orchestration and workflows
- **LangGraph** - Structured stateful pipelines
- **OpenAI GPT** - Advanced language understanding
- **Sentence Transformers** - Embedding generation
- **ChromaDB** - Vector database for semantic search
- **spaCy & NLTK** - Advanced text processing

### **Web & APIs**
- **Streamlit** - Interactive web interface
- **FastAPI** - High-performance API backend
- **Plotly** - Interactive data visualizations
- **Uvicorn** - ASGI server

### **Data & Storage**
- **SQLAlchemy** - Database ORM
- **SQLite** - Local database (easily scalable to PostgreSQL)
- **Pandas** - Data manipulation and analysis
- **Pydantic** - Data validation and settings

### **Document Processing**
- **pdfplumber** - PDF text extraction
- **docx2txt** - DOCX text extraction
- **rapidfuzz** - Fuzzy string matching

## 🚀 Quick Start

### **1. Setup Environment**
```bash
# Clone and navigate
git clone <repository>
cd Resume

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt
```

### **2. Configure API Keys (Optional)**
```bash
# Copy environment template
cp .env.example .env

# Add your OpenAI API key to .env
OPENAI_API_KEY=your_key_here
```

### **3. Run the System**

**Option A: Streamlit Only**
```bash
streamlit run app/web/streamlit_app.py
```

**Option B: Full System (Streamlit + FastAPI)**
```bash
python run_system.py
```

**Option C: FastAPI Only**
```bash
uvicorn app.api.main:app --reload
```

### **4. Access Applications**
- **Streamlit UI**: http://localhost:8501
- **FastAPI Docs**: http://localhost:8000/docs
- **API Health**: http://localhost:8000/health

## 📱 How to Use

### **📄 Upload Job Descriptions**
1. Navigate to "Upload JD" page
2. Choose file upload (PDF/DOCX) or manual text entry
3. Use AI skill extraction for automatic categorization
4. Configure must-have and nice-to-have skills
5. Save to database with vector indexing

### **📋 Evaluate Resumes**
1. Go to "Upload Resume" page
2. Select target job description
3. Upload candidate resume (PDF/DOCX)
4. Get comprehensive AI analysis:
   - Relevance score and verdict
   - LLM-powered detailed feedback
   - Entity extraction results
   - Missing skills identification
   - Improvement suggestions

### **📊 Analytics Dashboard**
1. Visit "Dashboard" page for insights:
   - Score distribution charts
   - Verdict breakdowns
   - Evaluation timeline
   - Advanced filtering and search
   - CSV export functionality

## 🤖 AI Capabilities

### **Without API Keys (Fallback Mode)**
- ✅ Hybrid scoring with TF-IDF similarity
- ✅ Keyword-based skill matching
- ✅ Basic entity extraction
- ✅ Statistical analysis
- ✅ Vector storage and search

### **With OpenAI API Key (Full Power)**
- ✅ LLM-powered semantic analysis
- ✅ Detailed feedback generation
- ✅ Confidence scoring
- ✅ Advanced skill gap analysis
- ✅ Personalized improvement suggestions
- ✅ Enhanced entity recognition

## 🔧 Configuration

### **Scoring Weights** (`app/config.py`)
```python
HARD_MATCH_WEIGHT = 0.6  # Rule-based scoring
SOFT_MATCH_WEIGHT = 0.4  # Semantic similarity
```

### **Verdict Thresholds**
```python
VERDICT_THRESHOLDS = {
    "high": 75,    # 75%+ = High suitability
    "medium": 50,  # 50-74% = Medium suitability
}                  # <50% = Low suitability
```

### **LLM Settings**
```python
EMBEDDINGS_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
USE_EMBEDDINGS = True
```

## 📊 API Endpoints

### **Job Management**
- `POST /jobs/` - Create job description
- `GET /jobs/` - List all jobs
- `GET /jobs/{id}` - Get specific job
- `POST /jobs/upload` - Upload JD from file

### **Resume Evaluation**
- `POST /evaluate/` - Comprehensive evaluation
- `GET /search/resumes` - Semantic resume search
- `GET /search/jobs` - Semantic job search

### **Analytics**
- `GET /analytics/dashboard` - Dashboard metrics
- `GET /health` - System health check

## 🗂️ Project Structure

```
Resume/
├── app/
│   ├── api/              # FastAPI backend
│   ├── db/               # Database models & CRUD
│   ├── nlp/              # AI/ML processing
│   ├── parsing/          # Document processing
│   ├── services/         # Business logic
│   └── web/              # Streamlit frontend
├── data/                 # Database & vector storage
├── requirements.txt      # Dependencies
├── run_system.py        # Full system launcher
└── .env.example         # Configuration template
```

## 🔄 Workflow

1. **Job Setup**: Upload job descriptions with AI skill extraction
2. **Resume Processing**: Extract and normalize candidate information
3. **Hybrid Analysis**: Combine rule-based and semantic evaluation
4. **LLM Enhancement**: Generate detailed feedback and suggestions
5. **Storage**: Index in vector store for future search
6. **Analytics**: Track performance and generate insights

## 🌟 Advanced Features

- **Vector Similarity Search**: Find similar resumes/jobs
- **Entity Recognition**: Extract structured information
- **Confidence Scoring**: AI reliability indicators
- **Progressive Enhancement**: Graceful degradation without API keys
- **Real-time Analytics**: Live dashboard updates
- **Export Capabilities**: CSV download for analysis
- **Multi-model Support**: OpenAI, Google, Anthropic compatibility

## 📈 Performance

- **Fast Processing**: Optimized text extraction and analysis
- **Scalable Architecture**: FastAPI + vector database
- **Efficient Storage**: SQLite for rapid development, PostgreSQL ready
- **Smart Caching**: Vector embeddings cached for reuse
- **Background Processing**: Non-blocking evaluation pipeline

## 🔐 Security & Production

- **Environment Variables**: Secure API key management
- **CORS Configuration**: Configurable cross-origin policies
- **Input Validation**: Pydantic models for data validation
- **Error Handling**: Comprehensive exception management
- **Logging**: Structured logging for monitoring

---

## 🎯 **Your AI Resume Evaluation Engine is Production Ready!**

This system implements every aspect of your specification with enterprise-grade architecture, beautiful UI, and advanced AI capabilities. It's ready for deployment and can scale from individual use to enterprise solutions.

**Ready to revolutionize resume evaluation!** 🚀
