"""
Vector Service for PGVector operations
Based on idea_borad.ipynb langchain PGVector patterns
"""

import logging
# Use langchain_community (compatible with existing schema)
from langchain_community.vectorstores import PGVector
USING_NEW_PGVECTOR = False
logging.info("✅ Using langchain_community PGVector (compatible with existing schema)")

from langchain.schema import Document
from config.settings import Config
from database.connection import get_db_connection
from services.huggingface_service import huggingface_service

class VectorService:
    """Service for vector operations using PGVector and Langchain"""
    
    def __init__(self):
        self.vector_store = None
        self.collection_name = Config.VECTOR_TABLE_NAME
        self.connection_string = Config.DATABASE_URL
        
        self._initialize()
    
    def _initialize(self):
        """Initialize vector store"""
        try:
            # Create a dummy embedding to test connection
            if huggingface_service.is_available():
                # Initialize with existing collection if it exists
                self._connect_to_existing_store()
                
                # If connection failed due to dimension mismatch, create new store
                if self.vector_store is None:
                    self._create_new_vector_store()
            else:
                logging.warning("⚠️ Vector service initialized without HuggingFace embeddings")
        except Exception as e:
            logging.error(f"❌ Vector service initialization failed: {e}")
            self.vector_store = None
    
    def _create_new_vector_store(self):
        """Create a new vector store with current embedding dimensions"""
        try:
            if not huggingface_service.is_available():
                logging.error("❌ Cannot create vector store - HuggingFace service not available")
                return
            
            embedding_function = huggingface_service.get_embedding_model()
            if embedding_function is None:
                logging.error("❌ Cannot create vector store - no embedding function available")
                return
            
            # Configuration for new vector store
            vector_config = {
                "collection_name": self.collection_name,
                "connection_string": self.connection_string,
                "embedding_function": embedding_function,
                "pre_delete_collection": False  # Don't delete, just create new if needed
            }
            
            logging.info(f"🔄 Creating new vector store: {self.collection_name}")
            
            # Create new store
            self.vector_store = PGVector(**vector_config)
            logging.info(f"✅ Created new vector store: {self.collection_name}")
            
        except Exception as e:
            logging.error(f"❌ Failed to create new vector store: {e}")
            self.vector_store = None
    
    def _connect_to_existing_store(self):
        """Connect to existing populated vector store"""
        try:
            if not huggingface_service.is_available():
                logging.error("❌ Cannot connect to vector store - HuggingFace service not available")
                self.vector_store = None
                return
            
            embedding_function = huggingface_service.get_embedding_model()
            if embedding_function is None:
                logging.error("❌ Cannot connect to vector store - no embedding function available")
                self.vector_store = None
                return
            
            # Configuration for langchain_community (compatible with existing schema)
            vector_config = {
                "collection_name": self.collection_name,
                "connection_string": self.connection_string,
                "embedding_function": embedding_function,
                "pre_delete_collection": False  # NEVER delete existing data
            }
            
            logging.info(f"🔄 Connecting to existing populated vector store: {self.collection_name}")
            
            # Connect to existing store (DO NOT CREATE NEW)
            self.vector_store = PGVector(**vector_config)
            logging.info(f"✅ Connected to existing vector store: {self.collection_name}")
            
            # Test if the connection works with a simple search
            try:
                test_results = self.vector_store.similarity_search("test", k=1)
                logging.info(f"✅ Vector store is working with {len(test_results)} items found in test")
            except Exception as test_e:
                logging.warning(f"⚠️ Vector store connected but test search failed: {test_e}")
                # If dimension mismatch, the vector store still exists but needs clearing
                if "different vector dimensions" in str(test_e):
                    logging.warning("⚠️ Vector dimension mismatch detected - vector store needs reset")
                    self.vector_store = None  # Mark as unavailable until cleared
            
        except Exception as e:
            logging.error(f"❌ Failed to connect to existing vector store: {e}")
            self.vector_store = None
    

    
    def is_available(self):
        """Check if vector service is available"""
        return self.vector_store is not None and huggingface_service.is_available()
    
    def add_idea_to_vector_store(self, idea):
        """Add a single idea to existing vector store"""
        if not self.is_available():
            logging.warning("⚠️ Vector store not available - cannot add idea")
            return
        
        try:
            # Create document from idea
            full_text = f"{idea['title']} {idea['description']} {idea.get('abstract', '')}"
            
            document = Document(
                page_content=full_text,
                metadata={
                    "idea_id": idea.get('id'),
                    "idea_title": idea['title'],
                    "category": idea['category'],
                    "impact": idea['impact'],
                    "contributor": idea['contributor'],
                    "status": idea.get('status', 'Under Review')
                }
            )
            
            # Add to existing store (never create new)
            self.vector_store.add_documents([document])
            logging.info(f"✅ Added idea '{idea['title']}' to existing vector store")
                
        except Exception as e:
            logging.error(f"❌ Error adding idea to vector store: {e}")
    
    def load_ideas_to_vector_store(self, ideas):
        """Add multiple ideas to existing vector store (DO NOT RECREATE)"""
        if not self.is_available():
            logging.warning("⚠️ Vector store not available - cannot load ideas")
            return {"status": "error", "reason": "Vector store not available"}
        
        try:
            # Convert ideas to documents
            documents = []
            for idea in ideas:
                full_text = f"{idea['title']} {idea['description']} {idea.get('abstract', '')}"
                
                document = Document(
                    page_content=full_text,
                    metadata={
                        "idea_id": idea.get('id'),
                        "idea_title": idea['title'],
                        "category": idea['category'],
                        "impact": idea['impact'],
                        "contributor": idea['contributor'],
                        "status": idea.get('status', 'Under Review')
                    }
                )
                documents.append(document)
            
            # Add to existing vector store (NEVER recreate)
            self.vector_store.add_documents(documents)
            
            logging.info(f"✅ Added {len(documents)} ideas to existing vector store")
            return {"status": "success", "count": len(documents)}
            
        except Exception as e:
            logging.error(f"❌ Error adding ideas to vector store: {e}")
            return {"status": "error", "error": str(e)}
    
    def search_similar_ideas(self, query_text, top_k=5):
        """Search for similar ideas using vector similarity"""
        if not self.is_available():
            logging.error("❌ Vector service not available - cannot search")
            return []
        
        try:
            logging.info(f"🔍 Searching for: '{query_text}' (top {top_k})")
            
            # Use similarity search with scores (like in notebook)
            results = self.vector_store.similarity_search_with_score(query_text, k=top_k)
            
            similar_ideas = []
            for doc, score in results:
                # Convert distance to similarity percentage (like in notebook)
                # Note: Different distance metrics may need different conversion
                similarity_percentage = max(0, min(100, (1 - score) * 100))
                
                logging.debug(f"Found idea: {doc.metadata.get('idea_title')} - {similarity_percentage}% similarity")
                
                if similarity_percentage > Config.SEARCH_THRESHOLD * 100:
                    similar_ideas.append({
                        "idea_id": doc.metadata.get('idea_id'),
                        "title": doc.metadata.get('idea_title'),
                        "category": doc.metadata.get('category'),
                        "contributor": doc.metadata.get('contributor'),
                        "impact": doc.metadata.get('impact'),
                        "content_preview": doc.page_content[:200],
                        "similarity": round(similarity_percentage, 1)
                    })
            
            logging.info(f"🔍 Found {len(similar_ideas)} similar ideas for query: '{query_text[:50]}...'")
            
            # Remove duplicates by idea_id (keep the one with highest similarity)
            unique_ideas = {}
            for idea in similar_ideas:
                idea_id = idea.get('idea_id')
                if idea_id not in unique_ideas or idea.get('similarity', 0) > unique_ideas[idea_id].get('similarity', 0):
                    if idea_id in unique_ideas:
                        logging.warning(f"⚠️ Removing duplicate for idea_id {idea_id} (keeping higher similarity)")
                    unique_ideas[idea_id] = idea
            
            # Convert back to list, sorted by similarity
            final_results = sorted(unique_ideas.values(), key=lambda x: x.get('similarity', 0), reverse=True)
            
            if len(final_results) != len(similar_ideas):
                logging.info(f"🧹 Removed {len(similar_ideas) - len(final_results)} duplicate entries")
            
            return final_results
            
        except Exception as e:
            logging.error(f"❌ Error searching similar ideas: {e}")
            return []
    

    
    def find_duplicate_ideas(self, new_idea):
        """Find potential duplicate ideas"""
        if not self.is_available():
            return []
        
        # Create search text from new idea
        search_text = f"{new_idea['title']} {new_idea['description']} {new_idea.get('abstract', '')}"
        
        # Search for similar ideas
        similar_ideas = self.search_similar_ideas(search_text, top_k=10)
        
        # Filter for high similarity (potential duplicates)
        duplicates = [
            idea for idea in similar_ideas 
            if idea['similarity'] > Config.DUPLICATE_THRESHOLD * 100
        ]
        
        return duplicates
    
    def find_collaboration_opportunities(self, new_idea):
        """Find ideas suitable for collaboration"""
        if not self.is_available():
            return []
        
        # Create search text from new idea
        search_text = f"{new_idea['title']} {new_idea['description']} {new_idea.get('abstract', '')}"
        
        # Search for similar ideas
        similar_ideas = self.search_similar_ideas(search_text, top_k=10)
        
        # Filter for collaboration opportunities (medium to high similarity)
        collaborations = [
            idea for idea in similar_ideas 
            if Config.COLLABORATION_THRESHOLD * 100 <= idea['similarity'] < Config.DUPLICATE_THRESHOLD * 100
        ]
        
        return collaborations
    
    def clear_vector_store(self):
        """Clear the vector store (useful for reset)"""
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            
            # Delete documents from this collection
            cur.execute("""
                DELETE FROM langchain_pg_embedding 
                WHERE collection_id = (
                    SELECT uuid FROM langchain_pg_collection 
                    WHERE name = %s
                )
            """, (self.collection_name,))
            
            # Delete collection
            cur.execute("DELETE FROM langchain_pg_collection WHERE name = %s", (self.collection_name,))
            
            conn.commit()
            cur.close()
            conn.close()
            
            logging.info(f"✅ Cleared vector store: {self.collection_name}")
            
            # Reinitialize vector store with new dimensions
            self._initialize()
            
            return {"status": "success", "message": "Vector store cleared and reinitialized"}
            
        except Exception as e:
            logging.error(f"❌ Error clearing vector store: {e}")
            return {"status": "error", "error": str(e)}

# Global instance
vector_service = VectorService() 