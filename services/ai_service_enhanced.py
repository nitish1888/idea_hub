"""
Idea Hub - Enhanced AI Service with MCP Integration
==========================================================

This module provides enhanced AI service integration that combines:
- MCP server capabilities for advanced AI operations
- Fallback to local Gemini AI service for reliability
- Seamless integration for existing application code

The enhanced service automatically routes requests to the most appropriate
AI backend, preferring the MCP server for its advanced capabilities while
maintaining compatibility with the existing codebase.

Key Features:
------------
- Primary integration with deployed MCP server
- Automatic fallback to local Gemini AI service
- Maintains existing API compatibility
- Enhanced capabilities through MCP tools
- Improved error handling and resilience

Usage:
------
from services.ai_service_enhanced import enhanced_ai_service

# Service automatically chooses best backend
summary = enhanced_ai_service.generate_summary(idea_content)
duplicates = enhanced_ai_service.detect_duplicates(idea_text)
search_results = enhanced_ai_service.search_ideas(query)
"""

import logging
from typing import Dict, List, Optional, Any
from config.settings import Config

# Import both MCP client and original AI service
try:
    from services.mcp_client import mcp_client
    MCP_AVAILABLE = True
except ImportError as e:
    logging.warning(f"MCP client not available: {e}")
    MCP_AVAILABLE = False
    mcp_client = None

try:
    from services.ai_service import gemini_service
    GEMINI_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Gemini service not available: {e}")
    GEMINI_AVAILABLE = False
    gemini_service = None

class EnhancedAIService:
    """Enhanced AI service that integrates MCP server with local fallback"""
    
    def __init__(self):
        self.mcp_enabled = Config.MCP_ENABLED and MCP_AVAILABLE
        self.fallback_enabled = Config.MCP_FALLBACK_ENABLED and GEMINI_AVAILABLE
        
        logging.info(f"🧠 Enhanced AI Service initialized:")
        logging.info(f"   - MCP integration: {'✅ Enabled' if self.mcp_enabled else '❌ Disabled'}")
        logging.info(f"   - Local fallback: {'✅ Enabled' if self.fallback_enabled else '❌ Disabled'}")
        
        # Test MCP server availability on startup
        if self.mcp_enabled:
            self._test_mcp_connection()
    
    def _test_mcp_connection(self):
        """Test MCP server connection on startup"""
        try:
            if mcp_client and mcp_client.is_available():
                logging.info("✅ MCP server connection verified")
            else:
                logging.warning("⚠️ MCP server not available - will use fallback")
        except Exception as e:
            logging.warning(f"⚠️ MCP server test failed: {e}")
    
    def is_available(self) -> bool:
        """Check if any AI service is available"""
        if self.mcp_enabled and mcp_client and mcp_client.is_available():
            return True
        
        if self.fallback_enabled and gemini_service and gemini_service.is_available():
            return True
        
        return False
    
    def search_ideas(self, query: str, search_type: str = "hybrid", limit: int = 10, threshold: float = 0.7) -> List[Dict[str, Any]]:
        """Search for ideas using AI-powered semantic search"""
        try:
            # Try MCP server first
            if self.mcp_enabled and mcp_client and mcp_client.is_available():
                logging.info(f"🔍 Using MCP server for idea search: '{query}'")
                return mcp_client.search_ideas(query, search_type, limit)
            
            # Fallback to local search (if available)
            elif self.fallback_enabled:
                logging.info(f"🔍 Using local fallback for idea search: '{query}'")
                # Import vector service for local search
                try:
                    from services.vector_service import vector_service
                    if vector_service.is_available():
                        results = vector_service.search_similar_ideas(query, top_k=limit)
                        # Convert to expected format and apply threshold filtering
                        formatted_results = []
                        for result in results:
                            similarity_score = result.get('similarity', 0.0) / 100.0  # Convert percentage to 0-1 scale
                            # Only include results above threshold
                            if similarity_score >= threshold:
                                formatted_results.append({
                                    'id': result.get('idea_id'),  # Fix field mapping
                                    'title': result.get('title', ''),
                                    'description': result.get('content_preview', ''),  # Use content preview as description
                                    'contributor': result.get('contributor', ''),
                                    'category': result.get('category', ''),
                                    'impact': result.get('impact', ''),
                                    'similarity_score': similarity_score
                                })
                        return formatted_results
                except ImportError:
                    logging.warning("Vector service not available for fallback search")
            
            logging.warning("No AI search service available")
            return []
            
        except Exception as e:
            logging.error(f"❌ Error in AI search: {e}")
            return []
    
    def detect_duplicates(self, idea_text: str, threshold: float = 0.85) -> List[Dict[str, Any]]:
        """Detect duplicate or similar ideas using AI analysis"""
        try:
            logging.info(f"🔍 Duplicate detection - Text: '{idea_text[:100]}...' | Threshold: {threshold*100}%")
            
            # Try MCP server first
            if self.mcp_enabled and mcp_client and mcp_client.is_available():
                logging.info("🔍 Using MCP server for duplicate detection")
                return mcp_client.detect_duplicates(idea_text, threshold)
            
            # Fallback to local duplicate detection
            elif self.fallback_enabled:
                logging.info("🔍 Using local fallback for duplicate detection")
                try:
                    from services.vector_service import vector_service
                    if vector_service.is_available():
                        results = vector_service.search_similar_ideas(idea_text, top_k=5)
                        # Filter by threshold and format
                        duplicates = []
                        for result in results:
                            similarity = result.get('similarity', 0.0)
                            if similarity >= threshold * 100:  # Convert threshold to percentage
                                logging.info(f"💡 DUPLICATE FOUND: '{result.get('title', '')}' | Similarity: {similarity}% | Content: '{result.get('content_preview', '')[:80]}...'")
                                duplicates.append({
                                    'id': result.get('idea_id'),
                                    'title': result.get('title', ''),
                                    'description': result.get('content_preview', ''),
                                    'contributor': result.get('contributor', ''),
                                    'similarity_score': similarity / 100.0  # Convert to 0-1 scale
                                })
                        
                        if duplicates:
                            logging.info(f"📋 Found {len(duplicates)} duplicates above {threshold*100}% threshold")
                        else:
                            logging.info(f"✅ No duplicates found above {threshold*100}% threshold")
                        
                        return duplicates
                except ImportError:
                    logging.warning("Vector service not available for fallback duplicate detection")
            
            logging.warning("No duplicate detection service available")
            return []
            
        except Exception as e:
            logging.error(f"❌ Error in duplicate detection: {e}")
            return []
    
    def generate_summary(self, idea_content: str) -> Optional[str]:
        """Generate AI summary of idea content"""
        try:
            # Try MCP server first
            if self.mcp_enabled and mcp_client and mcp_client.is_available():
                logging.info("✨ Using MCP server for summary generation")
                return mcp_client.generate_summary(idea_content)
            
            # Fallback to local Gemini service
            elif self.fallback_enabled and gemini_service and gemini_service.is_available():
                logging.info("✨ Using local Gemini for summary generation")
                prompt = f"""
                Please provide a concise summary of this innovation idea:
                
                {idea_content}
                
                Focus on:
                - Main objective and value proposition
                - Key features or capabilities
                - Potential impact or benefits
                
                Keep the summary under 150 words.
                """
                return gemini_service.generate_text(prompt)
            
            logging.warning("No summary generation service available")
            return None
            
        except Exception as e:
            logging.error(f"❌ Error in summary generation: {e}")
            return None
    
    def search_contributors(self, skills: List[str], availability: Optional[str] = None) -> List[Dict[str, Any]]:
        """Search for contributors using AI matching"""
        try:
            # Try MCP server first
            if self.mcp_enabled and mcp_client and mcp_client.is_available():
                logging.info(f"👥 Using MCP server for contributor search: {skills}")
                return mcp_client.search_contributors(skills, availability)
            
            # For now, no local fallback for contributor search
            # This could be implemented with database queries + AI matching
            logging.warning("Contributor search only available through MCP server")
            return []
            
        except Exception as e:
            logging.error(f"❌ Error in contributor search: {e}")
            return []
    
    def generate_collaboration_suggestion(self, new_idea: Dict, similar_idea: Dict, similarity_score: float) -> str:
        """Generate AI collaboration suggestion (maintains compatibility)"""
        try:
            # Try MCP server for enhanced suggestion
            if self.mcp_enabled and mcp_client and mcp_client.is_available():
                prompt = f"""
                Generate a collaboration suggestion for these similar ideas:
                
                New idea: "{new_idea.get('title', '')}" by {new_idea.get('contributor', '')}
                Similar idea: "{similar_idea.get('title', '')}" by {similar_idea.get('contributor', '')}
                Similarity: {similarity_score:.1%}
                
                Provide a brief, encouraging suggestion for collaboration.
                """
                summary = mcp_client.generate_summary(prompt)
                if summary:
                    return summary
            
            # Fallback to local Gemini service
            if self.fallback_enabled and gemini_service and gemini_service.is_available():
                return gemini_service.generate_collaboration_suggestion(new_idea, similar_idea, similarity_score)
            
            # Default fallback message
            return f"Consider collaborating with {similar_idea.get('contributor', 'the other contributor')} on '{similar_idea.get('title', 'their similar idea')}' - you have {similarity_score:.1%} alignment!"
            
        except Exception as e:
            logging.error(f"❌ Error generating collaboration suggestion: {e}")
            return "Consider reaching out to discuss potential collaboration opportunities."
    
    def generate_text(self, prompt: str, timeout: int = 10) -> str:
        """Generate text using AI (maintains compatibility with existing code)"""
        try:
            # Try MCP server first
            if self.mcp_enabled and mcp_client and mcp_client.is_available():
                summary = mcp_client.generate_summary(prompt)
                if summary:
                    return summary
            
            # Fallback to local Gemini service
            if self.fallback_enabled and gemini_service and gemini_service.is_available():
                return gemini_service.generate_text(prompt, timeout)
            
            return "AI service not available"
            
        except Exception as e:
            logging.error(f"❌ Error in text generation: {e}")
            return f"Error generating response: {e}"
    
    def generate_embedding(self, text: str) -> Optional[List[float]]:
        """Generate text embedding (maintains compatibility)"""
        try:
            # For embeddings, we still use local service for consistency
            # MCP server embeddings are used for its own operations
            if self.fallback_enabled and gemini_service and gemini_service.is_available():
                return gemini_service.generate_embedding(text)
            
            logging.warning("No embedding service available")
            return None
            
        except Exception as e:
            logging.error(f"❌ Error generating embedding: {e}")
            return None
    
    def get_embedding_stats(self) -> Optional[Dict[str, Any]]:
        """Get vector embedding statistics"""
        try:
            # Try MCP server first for comprehensive stats
            if self.mcp_enabled and mcp_client and mcp_client.is_available():
                return mcp_client.get_embedding_stats()
            
            return None
            
        except Exception as e:
            logging.error(f"❌ Error getting embedding stats: {e}")
            return None

# Global enhanced AI service instance
enhanced_ai_service = EnhancedAIService()

def get_enhanced_ai_service() -> EnhancedAIService:
    """Get the global enhanced AI service instance"""
    return enhanced_ai_service

