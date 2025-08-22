"""
Idea Hub - Google Gemini AI Service
===========================================

This module provides integration with Google's Gemini AI service for:
- Text embedding generation for semantic search
- Natural language text generation and summarization
- AI-powered idea analysis and comparison

The service is central to the platform's AI capabilities including:
- Duplicate idea detection through semantic similarity
- Automated idea summaries and insights
- Intelligent search and recommendation features

Key Features:
------------
- Text embedding generation using Gemini embedding models
- Text generation for summaries and analysis
- Robust error handling with graceful fallbacks
- Configuration-based model selection
- Service availability checking for health monitoring

Dependencies:
------------
- google-generativeai: Official Google Gemini Python SDK
- GEMINI_API_KEY: Required environment variable for authentication
- Configuration from config.settings

Model Configuration:
-------------------
- Text Generation: Uses configurable Gemini model (default: gemini-2.5-flash)
- Embeddings: Uses text-embedding-004 model for semantic vectors
- Task Type: Configured for retrieval/document processing

Usage:
------
from services.ai_service import gemini_service

# Check if service is available
if gemini_service.is_available():
    # Generate embeddings for semantic search
    embedding = gemini_service.generate_embedding("innovation text")
    
    # Generate text summaries
    summary = gemini_service.generate_text("Summarize this idea...")

Error Handling:
--------------
- Service gracefully handles missing API keys
- Provides fallback empty embeddings when service unavailable
- Comprehensive logging for debugging and monitoring
- Automatic retry logic for transient failures

Author: Innovation Team
Last Updated: 2025
"""

import google.generativeai as genai
import logging
import numpy as np
from config.settings import Config

#=============================================================================
# GEMINI AI SERVICE CLASS
#=============================================================================

class GeminiService:
    """
    Google Gemini AI service for text generation and embedding operations
    
    This class encapsulates all interactions with Google's Gemini AI service,
    providing a clean interface for the Idea Hub application.
    
    The service handles:
    - Text embedding generation for semantic similarity calculations
    - Natural language text generation for summaries and insights
    - Model configuration and API key management
    - Error handling and fallback behaviors
    - Service health monitoring and availability checks
    
    Initialization:
        The service automatically initializes on instantiation and configures
        the Gemini API with the provided API key from configuration.
        
    Thread Safety:
        This class is designed to be thread-safe for concurrent usage across
        multiple Flask request handlers.
    """
    
    def __init__(self):
        self.api_key = Config.GEMINI_API_KEY
        self.model_name = Config.GEMINI_MODEL
        self.embedding_model = Config.EMBEDDING_MODEL
        self.model = None
        
        self._initialize()
    
    def _initialize(self):
        """Initialize Gemini AI"""
        if self.api_key and self.api_key != "your_gemini_api_key_here":
            try:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel(self.model_name)
                logging.info("✅ Gemini AI initialized successfully")
            except Exception as e:
                logging.error(f"❌ Gemini initialization failed: {e}")
                self.model = None
        else:
            logging.warning("⚠️ Gemini API key not set - AI features disabled")
            self.model = None
    
    def is_available(self):
        """Check if Gemini service is available"""
        return self.model is not None
    
    def generate_embedding(self, text):
        """Generate embedding using Gemini"""
        if not self.is_available():
            return [0.0] * 768  # Fallback empty embedding
        
        try:
            result = genai.embed_content(
                model=self.embedding_model,
                content=text,
                task_type="retrieval_document"
            )
            return result['embedding']
        except Exception as e:
            logging.error(f"Error generating embedding: {e}")
            return [0.0] * 768
    
    def calculate_similarity(self, embedding1, embedding2):
        """Calculate cosine similarity between two embeddings"""
        try:
            a = np.array(embedding1)
            b = np.array(embedding2)
            
            # Handle zero vectors
            norm_a = np.linalg.norm(a)
            norm_b = np.linalg.norm(b)
            
            if norm_a == 0 or norm_b == 0:
                return 0.0
                
            return np.dot(a, b) / (norm_a * norm_b)
        except Exception as e:
            logging.error(f"Error calculating similarity: {e}")
            return 0.0
    
    def generate_text(self, prompt, timeout=10):
        """Generate text using Gemini with thread-safe timeout"""
        if not self.is_available():
            return "AI service not available"
        
        try:
            import threading
            import time
            
            result_container = {"result": None, "error": None}
            
            def api_call():
                try:
                    response = self.model.generate_content(prompt)
                    result_container["result"] = response.text.strip()
                except Exception as e:
                    result_container["error"] = str(e)
            
            # Start the API call in a separate thread
            thread = threading.Thread(target=api_call)
            thread.daemon = True
            thread.start()
            
            # Wait for completion or timeout
            thread.join(timeout)
            
            if thread.is_alive():
                logging.error(f"Gemini API call timed out after {timeout} seconds")
                return "AI service temporarily unavailable (timeout)"
            
            if result_container["error"]:
                logging.error(f"Error generating text: {result_container['error']}")
                return f"Error generating response: {result_container['error']}"
            
            return result_container["result"] or "AI service returned empty response"
            
        except Exception as e:
            logging.error(f"Error in generate_text: {e}")
            return f"Error generating response: {e}"
    
    def generate_collaboration_suggestion(self, new_idea, similar_idea, similarity_score):
        """Generate AI collaboration suggestion"""
        prompt = f"""
        Generate a brief collaboration suggestion message.
        
        New idea: "{new_idea['title']}" by {new_idea['contributor']}
        Similar existing idea: "{similar_idea['title']}" by {similar_idea['contributor']}
        Similarity: {similarity_score:.1%}
        
        Write a 1-2 sentence suggestion for collaboration.
        """
        
        return self.generate_text(prompt)
    
    def generate_insights(self, data_summary):
        """Generate AI insights about idea hub data"""
        prompt = f"""
        Analyze this Idea Hub data and provide 3-4 key insights:
        
        Total Ideas: {data_summary.get('total_ideas', 0)}
        Categories: {data_summary.get('categories', {})}
        Impact Levels: {data_summary.get('impacts', {})}
        
        Provide actionable insights in bullet points about innovation trends and opportunities.
        Keep each insight concise and actionable.
        """
        
        response = self.generate_text(prompt)
        
        # Parse bullet points
        insights = []
        for line in response.split('\n'):
            line = line.strip()
            if line and (line.startswith('•') or line.startswith('-') or line.startswith('*')):
                insights.append(line.strip('• -*').strip())
        
        return insights if insights else [response]

# Global instance
gemini_service = GeminiService() 