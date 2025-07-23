"""
HuggingFace Embedding Service
Using the same model and approach as idea_borad.ipynb notebook
"""

import logging
import os
from langchain_community.embeddings import HuggingFaceEmbeddings

class HuggingFaceEmbeddingService:
    """Service for HuggingFace embeddings using the same model as the notebook"""
    
    def __init__(self):
        # Use the exact model path from your notebook
        self.model_path = "/Users/nitsingh/.cache/huggingface/hub/models--mixedbread-ai--mxbai-embed-large-v1/snapshots/e7857440379da569f68f19e8403b69cd7be26e50"
        self.embedding_model = None
        self._initialize()
    
    def _initialize(self):
        """Initialize HuggingFace embeddings"""
        try:
            # Check if model exists locally first
            if os.path.exists(self.model_path):
                logging.info(f"Using local model: {self.model_path}")
                model_name = self.model_path
            else:
                # Fallback to model name if local path doesn't exist
                logging.info("Local model not found, downloading mixedbread-ai/mxbai-embed-large-v1")
                model_name = "mixedbread-ai/mxbai-embed-large-v1"
            
            # Initialize exactly like in your notebook
            self.embedding_model = HuggingFaceEmbeddings(
                model_name=model_name
            )
            
            logging.info("✅ HuggingFace embeddings initialized successfully")
            
        except Exception as e:
            logging.error(f"❌ HuggingFace embeddings initialization failed: {e}")
            self.embedding_model = None
    
    def is_available(self):
        """Check if embedding service is available"""
        return self.embedding_model is not None
    
    def get_embedding_model(self):
        """Get the embedding model for Langchain (this is what we need!)"""
        return self.embedding_model
    
    def generate_embedding(self, text):
        """Generate embedding for a single text"""
        if not self.is_available():
            return [0.0] * 1024  # mxbai-embed-large-v1 has 1024 dimensions
        
        try:
            # Use embed_query for single text
            return self.embedding_model.embed_query(text)
        except Exception as e:
            logging.error(f"Error generating embedding: {e}")
            return [0.0] * 1024
    
    def calculate_similarity(self, embedding1, embedding2):
        """Calculate cosine similarity between two embeddings"""
        try:
            import numpy as np
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

# Global instance
huggingface_service = HuggingFaceEmbeddingService() 