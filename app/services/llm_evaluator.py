"""
Advanced LLM-powered evaluation service using LangChain and LangGraph
"""
import os
import sys
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.prompts import ChatPromptTemplate
from langchain.schema.runnable import RunnablePassthrough
from langchain.schema.output_parser import StrOutputParser
import json

# Handle ChromaDB import with SQLite fix
try:
    __import__('pysqlite3')
    sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
    import chromadb
    from chromadb.utils import embedding_functions
    CHROMADB_AVAILABLE = True
except (ImportError, RuntimeError) as e:
    print(f"ChromaDB not available: {e}")
    CHROMADB_AVAILABLE = False

try:
    from langchain_openai import ChatOpenAI, OpenAIEmbeddings
    from langchain_community.vectorstores import Chroma
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

@dataclass
class LLMEvaluationResult:
    semantic_score: float
    detailed_feedback: str
    skill_gaps: List[str]
    strengths: List[str]
    improvement_suggestions: List[str]
    relevance_explanation: str
    confidence_score: float

class AdvancedLLMEvaluator:
    """
    Advanced LLM-powered resume evaluator with vector store and structured analysis
    """
    
    def __init__(self, openai_api_key: Optional[str] = None):
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        self.vector_store = None
        self.llm = None
        self.embeddings = None
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        
        # Initialize if API key is available
        if self.openai_api_key and OPENAI_AVAILABLE:
            self._initialize_llm_components()
        
        # Initialize local vector store
        self._initialize_vector_store()
    
    def _initialize_llm_components(self):
        """Initialize LLM and embeddings if OpenAI API key is available"""
        try:
            self.llm = ChatOpenAI(
                api_key=self.openai_api_key,
                model="gpt-3.5-turbo",
                temperature=0.3
            )
            self.embeddings = OpenAIEmbeddings(api_key=self.openai_api_key)
        except Exception as e:
            print(f"LLM initialization failed: {e}")
            self.llm = None
            self.embeddings = None
    
    def _initialize_vector_store(self):
        """Initialize Chroma vector store if available"""
        try:
            if not CHROMADB_AVAILABLE:
                print("ChromaDB not available, skipping vector store initialization")
                self.collection = None
                return
                
            # Use sentence-transformers embeddings as fallback
            try:
                embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
                    model_name="sentence-transformers/all-MiniLM-L6-v2"
                )
            except Exception as e:
                print(f"Failed to initialize embedding function: {e}")
                if "429" in str(e) or "rate limit" in str(e).lower():
                    print("HuggingFace rate limiting detected - ChromaDB will use default embeddings")
                # Fall back to default embeddings
                embedding_fn = embedding_functions.DefaultEmbeddingFunction()
            
            client = chromadb.PersistentClient(path="./data/chroma_db")
            
            # Create or get collection
            self.collection = client.get_or_create_collection(
                name="resume_jd_collection",
                embedding_function=embedding_fn
            )
        except Exception as e:
            print(f"Vector store initialization failed: {e}")
            self.collection = None
    
    def add_to_vector_store(self, text: str, metadata: Dict[str, Any], doc_id: str):
        """Add document to vector store if available"""
        if self.collection:
            try:
                self.collection.add(
                    documents=[text],
                    metadatas=[metadata],
                    ids=[doc_id]
                )
            except Exception as e:
                print(f"Failed to add to vector store: {e}")
        else:
            print("Vector store not available, skipping document addition")
    
    def semantic_search(self, query: str, n_results: int = 5) -> List[Dict]:
        """Perform semantic search in vector store if available"""
        if not self.collection:
            print("Vector store not available, returning empty results")
            return []
            
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results
            )
            return [
                {
                    "document": doc,
                    "metadata": meta,
                    "distance": dist
                }
                for doc, meta, dist in zip(
                    results["documents"][0],
                    results["metadatas"][0],
                    results["distances"][0]
                )
            ]
        except Exception as e:
            print(f"Semantic search failed: {e}")
            return []
    
    def evaluate_with_llm(self, resume_text: str, jd_text: str) -> LLMEvaluationResult:
        """
        Advanced LLM-powered evaluation with structured analysis
        """
        if not self.llm:
            return self._fallback_evaluation(resume_text, jd_text)
        
        # Create evaluation prompt
        evaluation_prompt = ChatPromptTemplate.from_template("""
        You are an expert HR professional and technical recruiter. Analyze the following resume against the job description and provide a comprehensive evaluation.

        Job Description:
        {job_description}

        Resume:
        {resume}

        Provide your analysis in the following JSON format:
        {{
            "semantic_score": <float between 0.0 and 1.0>,
            "detailed_feedback": "<comprehensive feedback on the candidate's fit>",
            "skill_gaps": ["<skill1>", "<skill2>", ...],
            "strengths": ["<strength1>", "<strength2>", ...],
            "improvement_suggestions": ["<suggestion1>", "<suggestion2>", ...],
            "relevance_explanation": "<explanation of why this score was given>",
            "confidence_score": <float between 0.0 and 1.0 indicating confidence in evaluation>
        }}

        Focus on:
        1. Technical skill alignment
        2. Experience relevance
        3. Domain knowledge
        4. Potential for growth
        5. Cultural fit indicators

        Be specific and actionable in your feedback.
        """)
        
        try:
            # Create evaluation chain
            chain = (
                {"job_description": RunnablePassthrough(), "resume": RunnablePassthrough()}
                | evaluation_prompt
                | self.llm
                | StrOutputParser()
            )
            
            # Run evaluation
            result = chain.invoke({"job_description": jd_text, "resume": resume_text})
            
            # Parse JSON response
            evaluation_data = json.loads(result)
            
            return LLMEvaluationResult(
                semantic_score=evaluation_data.get("semantic_score", 0.5),
                detailed_feedback=evaluation_data.get("detailed_feedback", ""),
                skill_gaps=evaluation_data.get("skill_gaps", []),
                strengths=evaluation_data.get("strengths", []),
                improvement_suggestions=evaluation_data.get("improvement_suggestions", []),
                relevance_explanation=evaluation_data.get("relevance_explanation", ""),
                confidence_score=evaluation_data.get("confidence_score", 0.5)
            )
            
        except Exception as e:
            print(f"LLM evaluation failed: {e}")
            return self._fallback_evaluation(resume_text, jd_text)
    
    def _fallback_evaluation(self, resume_text: str, jd_text: str) -> LLMEvaluationResult:
        """Fallback evaluation when LLM is not available"""
        from app.nlp.embeddings import embedding_similarity
        from app.nlp.skills import extract_candidate_skills
        
        semantic_score = embedding_similarity(resume_text, jd_text)
        
        # Extract skills for basic gap analysis
        resume_skills = set(extract_candidate_skills(resume_text))
        jd_skills = set(extract_candidate_skills(jd_text))
        
        skill_gaps = list(jd_skills - resume_skills)
        strengths = list(resume_skills & jd_skills)
        
        return LLMEvaluationResult(
            semantic_score=semantic_score,
            detailed_feedback=f"Semantic similarity score: {semantic_score:.2f}. Basic skill analysis completed.",
            skill_gaps=skill_gaps[:5],  # Limit to top 5
            strengths=strengths[:5],
            improvement_suggestions=[
                "Consider adding missing skills to your resume",
                "Highlight relevant experience more prominently",
                "Include specific project examples"
            ],
            relevance_explanation=f"Score based on semantic similarity and skill overlap",
            confidence_score=0.7
        )
    
    def get_skill_recommendations(self, missing_skills: List[str]) -> List[str]:
        """Get learning recommendations for missing skills"""
        if not self.llm:
            return [f"Learn {skill} through online courses and practice projects" for skill in missing_skills[:3]]
        
        recommendations_prompt = ChatPromptTemplate.from_template("""
        Provide specific, actionable learning recommendations for these missing skills: {skills}
        
        For each skill, suggest:
        1. Best learning resources (courses, books, tutorials)
        2. Practical projects to demonstrate competency
        3. Timeline for achieving proficiency
        
        Keep recommendations practical and achievable.
        """)
        
        try:
            chain = recommendations_prompt | self.llm | StrOutputParser()
            recommendations = chain.invoke({"skills": ", ".join(missing_skills)})
            return recommendations.split("\n")[:10]  # Limit results
        except Exception:
            return [f"Learn {skill} through online courses and practice projects" for skill in missing_skills[:3]]

# Global instance
llm_evaluator = AdvancedLLMEvaluator()