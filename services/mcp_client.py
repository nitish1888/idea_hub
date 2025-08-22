"""
Red Hat Idea Hub - MCP Client Service
====================================

This module provides integration with the deployed MCP server for:
- Semantic idea search using vector embeddings
- Duplicate detection through AI-powered similarity analysis
- AI summary generation and text processing
- Contributor matching and search capabilities

The MCP client communicates with the deployed MCP server via HTTP API calls,
providing a clean interface for AI operations while maintaining separation
of concerns between the main application and AI processing.

Key Features:
------------
- HTTP-based communication with deployed MCP server
- Async/sync API support for different use cases
- Robust error handling with graceful fallbacks
- Configuration-based MCP server endpoint
- Service availability checking for health monitoring

Dependencies:
------------
- httpx: Modern HTTP client for API communication
- asyncio: Async support for concurrent operations
- MCP server deployed at configured endpoint

Configuration:
-------------
- MCP_SERVER_URL: Base URL of the deployed MCP server
- MCP_API_TIMEOUT: Request timeout for MCP operations
- Fallback to local services when MCP server unavailable

Usage:
------
from services.mcp_client import mcp_client

# Check if MCP service is available
if mcp_client.is_available():
    # Search for ideas using semantic search
    results = mcp_client.search_ideas("machine learning innovation")
    
    # Detect duplicates
    duplicates = mcp_client.detect_duplicates(idea_text)
    
    # Generate AI summary
    summary = mcp_client.generate_summary(idea_content)

Error Handling:
--------------
- Service gracefully handles MCP server unavailability
- Provides fallback to local AI services when needed
- Comprehensive logging for debugging and monitoring
"""

import logging
import httpx
import asyncio
import json
from typing import Dict, List, Optional, Any
from config.settings import Config

class MCPClient:
    """Client for communicating with the deployed MCP server"""
    
    def __init__(self):
        self.base_url = self._get_mcp_server_url()
        self.timeout = getattr(Config, 'MCP_API_TIMEOUT', 30.0)
        
        # Configure HTTP clients to handle self-signed certificates in OpenShift
        self.client = httpx.Client(
            timeout=self.timeout,
            verify=False,  # Disable SSL verification for OpenShift self-signed certs
            headers={'User-Agent': 'IdeaHub-MCP-Client/1.0'}
        )
        self.async_client = httpx.AsyncClient(
            timeout=self.timeout,
            verify=False,  # Disable SSL verification for OpenShift self-signed certs  
            headers={'User-Agent': 'IdeaHub-MCP-Client/1.0'}
        )
        self._available = None  # Cache availability status
        
        logging.info(f"🔗 MCP Client initialized with server: {self.base_url}")
    
    def _get_mcp_server_url(self) -> str:
        """Get MCP server URL from configuration"""
        # Check for environment variable first
        import os
        mcp_url = os.getenv('MCP_SERVER_URL')
        
        if not mcp_url:
            # Use the deployed OpenShift route
            mcp_url = "https://idea-hub-mcp-server-trend-analysis-using-ai--runtime-int.apps.int.spoke.preprod.us-east-1.aws.paas.redhat.com"
        
        return mcp_url.rstrip('/')
    
    def is_available(self) -> bool:
        """Check if MCP server is available"""
        if self._available is not None:
            return self._available
        
        try:
            response = self.client.get(f"{self.base_url}/api/health")
            if response.status_code == 200:
                health_data = response.json()
                self._available = health_data.get('status') == 'healthy'
                if self._available:
                    logging.info("✅ MCP server is available and healthy")
                else:
                    logging.warning("⚠️ MCP server responded but reports unhealthy status")
            else:
                logging.warning(f"⚠️ MCP server health check failed: {response.status_code}")
                self._available = False
        except Exception as e:
            logging.warning(f"⚠️ MCP server not available: {e}")
            self._available = False
        
        return self._available
    
    def search_ideas(self, query: str, search_type: str = "hybrid", limit: int = 10) -> List[Dict[str, Any]]:
        """Search for ideas using the MCP server's semantic search capabilities"""
        try:
            if not self.is_available():
                logging.warning("MCP server not available, returning empty results")
                return []
            
            payload = {
                "query": query,
                "search_type": search_type,
                "limit": limit
            }
            
            response = self.client.post(f"{self.base_url}/api/search-ideas", json=payload)
            
            if response.status_code == 200:
                result = response.json()
                ideas = result.get('ideas', [])
                logging.info(f"🔍 MCP search found {len(ideas)} ideas for query: '{query}'")
                return ideas
            else:
                logging.error(f"❌ MCP search failed: {response.status_code} - {response.text}")
                return []
                
        except Exception as e:
            logging.error(f"❌ Error in MCP search: {e}")
            return []
    
    def detect_duplicates(self, idea_text: str, threshold: float = 0.85) -> List[Dict[str, Any]]:
        """Detect duplicate or similar ideas using MCP server"""
        try:
            if not self.is_available():
                logging.warning("MCP server not available for duplicate detection")
                return []
            
            payload = {
                "title": idea_text[:100],  # Use first 100 chars as title
                "description": idea_text,
                "threshold": threshold
            }
            
            response = self.client.post(f"{self.base_url}/api/detect-duplicates", json=payload)
            
            if response.status_code == 200:
                result = response.json()
                duplicates = result.get('similar_ideas', [])
                logging.info(f"🔍 MCP duplicate detection found {len(duplicates)} similar ideas")
                return duplicates
            else:
                logging.error(f"❌ MCP duplicate detection failed: {response.status_code} - {response.text}")
                return []
                
        except Exception as e:
            logging.error(f"❌ Error in MCP duplicate detection: {e}")
            return []
    
    def generate_summary(self, idea_content: str) -> Optional[str]:
        """Generate AI summary using MCP server"""
        try:
            if not self.is_available():
                logging.warning("MCP server not available for summary generation")
                return None
            
            payload = {
                "idea_id": 1,  # Placeholder ID for summary generation
                "content": idea_content
            }
            
            response = self.client.post(f"{self.base_url}/api/generate-summary", json=payload)
            
            if response.status_code == 200:
                result = response.json()
                summary = result.get('summary', '')
                logging.info("✅ MCP summary generated successfully")
                return summary
            else:
                logging.error(f"❌ MCP summary generation failed: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logging.error(f"❌ Error in MCP summary generation: {e}")
            return None
    
    def search_contributors(self, skills: List[str], availability: Optional[str] = None) -> List[Dict[str, Any]]:
        """Search for contributors using MCP server"""
        try:
            if not self.is_available():
                logging.warning("MCP server not available for contributor search")
                return []
            
            payload = {
                "skills": skills,
                "availability": availability
            }
            
            response = self.client.post(f"{self.base_url}/api/search-contributors", json=payload)
            
            if response.status_code == 200:
                result = response.json()
                contributors = result.get('contributors', [])
                logging.info(f"👥 MCP contributor search found {len(contributors)} matches")
                return contributors
            else:
                logging.error(f"❌ MCP contributor search failed: {response.status_code} - {response.text}")
                return []
                
        except Exception as e:
            logging.error(f"❌ Error in MCP contributor search: {e}")
            return []
    
    def get_idea_details(self, idea_id: int) -> Optional[Dict[str, Any]]:
        """Get detailed idea information using MCP server"""
        try:
            if not self.is_available():
                logging.warning("MCP server not available for idea details")
                return None
            
            response = self.client.get(f"{self.base_url}/api/idea/{idea_id}")
            
            if response.status_code == 200:
                idea = response.json()
                logging.info(f"📄 MCP retrieved details for idea {idea_id}")
                return idea
            else:
                logging.error(f"❌ MCP idea details failed: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logging.error(f"❌ Error getting MCP idea details: {e}")
            return None
    
    def get_embedding_stats(self) -> Optional[Dict[str, Any]]:
        """Get vector embedding statistics from MCP server"""
        try:
            if not self.is_available():
                return None
            
            response = self.client.get(f"{self.base_url}/api/embedding-stats")
            
            if response.status_code == 200:
                stats = response.json()
                logging.info("📊 MCP embedding stats retrieved successfully")
                return stats
            else:
                logging.error(f"❌ MCP embedding stats failed: {response.status_code}")
                return None
                
        except Exception as e:
            logging.error(f"❌ Error getting MCP embedding stats: {e}")
            return None
    
    async def async_search_ideas(self, query: str, search_type: str = "hybrid", limit: int = 10) -> List[Dict[str, Any]]:
        """Async version of search_ideas for concurrent operations"""
        try:
            if not self.is_available():
                return []
            
            payload = {
                "query": query,
                "search_type": search_type,
                "limit": limit
            }
            
            response = await self.async_client.post(f"{self.base_url}/api/search-ideas", json=payload)
            
            if response.status_code == 200:
                result = response.json()
                return result.get('ideas', [])
            else:
                logging.error(f"❌ Async MCP search failed: {response.status_code}")
                return []
                
        except Exception as e:
            logging.error(f"❌ Error in async MCP search: {e}")
            return []
    
    def close(self):
        """Close HTTP clients"""
        try:
            self.client.close()
            asyncio.create_task(self.async_client.aclose())
        except Exception as e:
            logging.warning(f"Warning during MCP client closure: {e}")
    
    def __del__(self):
        """Cleanup on object destruction"""
        try:
            self.close()
        except:
            pass

# Global MCP client instance
mcp_client = MCPClient()

def get_mcp_client() -> MCPClient:
    """Get the global MCP client instance"""
    return mcp_client
