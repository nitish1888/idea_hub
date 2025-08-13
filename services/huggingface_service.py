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
        # Use static model configuration from settings
        from config.settings import Config
        self.model_name = Config.EMBEDDING_MODEL
        self.embedding_model = None
        self.current_model = None
        self.embedding_dimension = 384   # all-MiniLM-L6-v2 dimension
        self._initialize()
    
    def _initialize(self):
        """Initialize HuggingFace embeddings with offline-first approach"""
        try:
            logging.info(f"🔄 Initializing embedding model: {self.model_name}")
            
            # Initialize the embedding model with offline-first configuration
            self.embedding_model = HuggingFaceEmbeddings(
                model_name=self.model_name,
                model_kwargs={
                    'device': 'cpu',  # Force CPU for stability
                    'local_files_only': True,  # Prevent internet access
                    'trust_remote_code': False  # Security setting
                }
            )
            
            # Test the model works
            logging.info("🧪 Testing embedding model...")
            test_embedding = self.embedding_model.embed_query("test embedding")
            
            if test_embedding and len(test_embedding) > 0:
                self.current_model = self.model_name
                self.embedding_dimension = len(test_embedding)
                logging.info(f"✅ Embedding model initialized successfully!")
                logging.info(f"📐 Embedding dimension: {self.embedding_dimension}")
            else:
                logging.error("❌ Embedding model test failed - empty embedding returned")
                self.embedding_model = None
                
        except Exception as e:
            logging.error(f"❌ Failed to initialize embedding model: {str(e)}")
            
            # Try fallback without local_files_only if it was a network issue
            if "local_files_only" in str(e).lower() or "ssl" in str(e).lower() or "connection" in str(e).lower():
                logging.warning("🔄 Retrying without local_files_only restriction...")
                try:
                    self.embedding_model = HuggingFaceEmbeddings(
                        model_name=self.model_name,
                        model_kwargs={'device': 'cpu'}
                    )
                    
                    # Test the fallback model
                    test_embedding = self.embedding_model.embed_query("test embedding")
                    if test_embedding and len(test_embedding) > 0:
                        self.current_model = self.model_name
                        self.embedding_dimension = len(test_embedding)
                        logging.warning(f"⚠️ Embedding model initialized with fallback method!")
                        logging.info(f"📏 Model '{self.current_model}' embedding dimension: {self.embedding_dimension}")
                        return
                except Exception as fallback_e:
                    logging.error(f"❌ Fallback initialization also failed: {fallback_e}")
                    
                    # Try direct sentence-transformers approach as last resort
                    logging.warning("🔄 Trying direct sentence-transformers approach...")
                    try:
                        import sentence_transformers
                        st_model = sentence_transformers.SentenceTransformer(self.model_name)
                        
                        # Create a wrapper that mimics HuggingFaceEmbeddings interface
                        class STWrapper:
                            def __init__(self, model):
                                self.model = model
                            
                            def embed_query(self, text):
                                return self.model.encode(text).tolist()
                            
                            def embed_documents(self, texts):
                                return [self.model.encode(text).tolist() for text in texts]
                        
                        self.embedding_model = STWrapper(st_model)
                        
                        # Test the wrapper
                        test_embedding = self.embedding_model.embed_query("test embedding")
                        if test_embedding and len(test_embedding) > 0:
                            self.current_model = self.model_name
                            self.embedding_dimension = len(test_embedding)
                            logging.warning(f"⚠️ Embedding model initialized with sentence-transformers wrapper!")
                            logging.info(f"📏 Model '{self.current_model}' embedding dimension: {self.embedding_dimension}")
                            return
                    except Exception as st_e:
                        logging.error(f"❌ Sentence-transformers fallback also failed: {st_e}")
            
            logging.warning("⚠️ Vector service will run without embeddings")
            self.embedding_model = None
    
    def is_available(self):
        """Check if embedding service is available"""
        return self.embedding_model is not None
    
    def get_embedding_model(self):
        """Get the embedding model for Langchain (this is what we need!)"""
        return self.embedding_model
    
    def generate_embedding(self, text):
        """Generate embedding for a single text using the configured model"""
        if not self.is_available():
            logging.error("❌ Embedding service not available")
            return None
        
        try:
            # Use embed_query for single text
            embedding = self.embedding_model.embed_query(text)
            if embedding and len(embedding) > 0:
                return embedding
            else:
                logging.error("❌ Empty embedding returned from model")
                return None
        except Exception as e:
            logging.error(f"❌ Error generating embedding: {e}")
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