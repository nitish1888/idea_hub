"""
HuggingFace Embedding Service
Using the working mixedbread model path
"""

import logging
import os
try:
    # Try new langchain-huggingface package first
    from langchain_huggingface import HuggingFaceEmbeddings
    logging.info("✅ Using new langchain-huggingface package")
except ImportError:
    try:
        # Fallback to community package
        from langchain_community.embeddings import HuggingFaceEmbeddings
        logging.warning("⚠️ Using deprecated langchain_community.embeddings - consider upgrading to langchain-huggingface")
    except ImportError:
        logging.error("❌ No HuggingFace embeddings package found")

class HuggingFaceEmbeddingService:
    """Service for HuggingFace embeddings using the working mixedbread model"""
    
    def __init__(self):
        # Use only the working mixedbread model path
        self.model_path = "/Users/riskumar/.cache/huggingface/hub/models--mixedbread-ai--mxbai-embed-large-v1/snapshots/db9d1fe0f31addb4978201b2bf3e577f3f8900d2"
        self.embedding_model = None
        self.current_model = None
        self.embedding_dimension = 1024  # mixedbread dimension
        self._initialize()
    
    def _initialize(self):
        """Initialize HuggingFace embeddings with mixedbread model"""
        try:
            if not os.path.exists(self.model_path):
                logging.error(f"❌ Mixedbread model not found at: {self.model_path}")
                self.embedding_model = None
                return
            
            logging.info(f"🔄 Initializing mixedbread model: {self.model_path}")
            
            # Initialize the embedding model
            self.embedding_model = HuggingFaceEmbeddings(
                model_name=self.model_path,
                model_kwargs={'device': 'cpu'}  # Force CPU for stability
            )
            
            # Test the model works
            logging.info("🧪 Testing mixedbread model...")
            test_embedding = self.embedding_model.embed_query("test embedding")
            
            if test_embedding and len(test_embedding) > 0:
                self.current_model = self.model_path
                self.embedding_dimension = len(test_embedding)
                logging.info(f"✅ Mixedbread model initialized successfully!")
                logging.info(f"📐 Embedding dimension: {self.embedding_dimension}")
            else:
                logging.error("❌ Mixedbread model test failed - empty embedding returned")
                self.embedding_model = None
                
        except Exception as e:
            logging.error(f"❌ Failed to initialize mixedbread model: {str(e)}")
            self.embedding_model = None
    
    def is_available(self):
        """Check if embedding service is available"""
        return self.embedding_model is not None
    
    def get_embedding_model(self):
        """Get the embedding model for Langchain (this is what we need!)"""
        return self.embedding_model
    
    def generate_embedding(self, text):
        """Generate embedding for a single text using mixedbread model"""
        if not self.is_available():
            logging.error("❌ Mixedbread embedding service not available")
            return None
        
        try:
            # Use embed_query for single text
            embedding = self.embedding_model.embed_query(text)
            if embedding and len(embedding) > 0:
                return embedding
            else:
                logging.error("❌ Empty embedding returned from mixedbread model")
                return None
        except Exception as e:
            logging.error(f"❌ Error generating embedding with mixedbread: {e}")
            return None
    
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