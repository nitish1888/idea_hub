"""
Vector Service for PGVector operations
Based on idea_borad.ipynb langchain PGVector patterns
"""

import logging
from langchain_community.vectorstores import PGVector
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
            else:
                logging.warning("⚠️ Vector service initialized without HuggingFace embeddings")
        except Exception as e:
            logging.error(f"❌ Vector service initialization failed: {e}")
            self.vector_store = None
    
    def _connect_to_existing_store(self):
        """Connect to existing vector store or create new one"""
        try:
            # Try to connect to existing store
            self.vector_store = PGVector(
                collection_name=self.collection_name,
                connection_string=self.connection_string,
                embedding_function=huggingface_service.get_embedding_model()
            )
            logging.info(f"✅ Connected to existing vector store: {self.collection_name}")
        except Exception as e:
            logging.info(f"Creating new vector store: {e}")
            self.vector_store = None
    
    def is_available(self):
        """Check if vector service is available"""
        return self.vector_store is not None and huggingface_service.is_available()
    
    def add_idea_to_vector_store(self, idea):
        """Add a single idea to vector store"""
        if not huggingface_service.is_available():
            logging.warning("Skipping vector storage - HuggingFace service not available")
            return
        
        try:
            # Create document from idea (like in notebook)
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
            
            # Create vector store if it doesn't exist
            if self.vector_store is None:
                self.vector_store = PGVector.from_documents(
                    documents=[document],
                    embedding=huggingface_service.get_embedding_model(),
                    collection_name=self.collection_name,
                    connection_string=self.connection_string
                )
                logging.info(f"✅ Created new vector store with first document")
            else:
                # Add to existing store
                self.vector_store.add_documents([document])
                logging.info(f"✅ Added idea '{idea['title']}' to vector store")
                
        except Exception as e:
            logging.error(f"❌ Error adding idea to vector store: {e}")
    
    def load_ideas_to_vector_store(self, ideas):
        """Load multiple ideas to vector store (like notebook bulk loading)"""
        if not huggingface_service.is_available():
            logging.warning("Skipping vector storage - HuggingFace service not available")
            return {"status": "skipped", "reason": "HuggingFace service not available"}
        
        try:
            # Convert ideas to documents (like in notebook)
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
            
            # Create or recreate vector store with all documents
            self.vector_store = PGVector.from_documents(
                documents=documents,
                embedding=huggingface_service.get_embedding_model(),
                collection_name=self.collection_name,
                connection_string=self.connection_string
            )
            
            logging.info(f"✅ Loaded {len(documents)} ideas to vector store")
            return {"status": "success", "count": len(documents)}
            
        except Exception as e:
            logging.error(f"❌ Error loading ideas to vector store: {e}")
            return {"status": "error", "error": str(e)}
    
    def search_similar_ideas(self, query_text, top_k=5):
        """Search for similar ideas using vector similarity"""
        if not self.is_available():
            return []
        
        try:
            # Use similarity search with scores (like in notebook)
            results = self.vector_store.similarity_search_with_score(query_text, k=top_k)
            
            similar_ideas = []
            for doc, score in results:
                # Convert distance to similarity percentage (like in notebook)
                similarity_percentage = (1 - score) * 100
                
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
            
            return similar_ideas
            
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
            
            # Reset vector store
            self.vector_store = None
            
            logging.info(f"✅ Cleared vector store: {self.collection_name}")
            
        except Exception as e:
            logging.error(f"❌ Error clearing vector store: {e}")

# Global instance
vector_service = VectorService() 