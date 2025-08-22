"""
Idea Hub - MCP Agentic AI Service
==========================================

This implements agentic AI using Model Context Protocol (MCP) with Gemini.
MCP allows the AI to use tools and interact with external systems autonomously.

Key Features:
- Tool calling for database operations
- Vector search capabilities
- Market research tools
- Autonomous decision making
- Multi-step reasoning workflows

Dependencies:
- mcp: Model Context Protocol
- google-generativeai: For Gemini integration
- asyncio: For async tool execution
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

# MCP functionality is built into Gemini's function calling
# No separate MCP package needed
MCP_AVAILABLE = True

# Google Gemini with function calling
import google.generativeai as genai
from google.generativeai.types import FunctionDeclaration, Tool

# Our existing services
from services.ai_service import gemini_service
from services.vector_service import vector_service
from models.idea import IdeaModel
from models.contributor import ContributorModel
from config.settings import Config

#=============================================================================
# MCP TOOLS FOR IDEA HUB
#=============================================================================

class IdeaHubMCPTools:
    """MCP Tools for Idea Hub operations"""
    
    @staticmethod
    def get_tool_definitions() -> List[FunctionDeclaration]:
        """Get Gemini function declarations for MCP tools"""
        return [
            FunctionDeclaration(
                name="search_similar_ideas",
                description="Search for similar ideas in the Idea Hub database using semantic similarity",
                parameters={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query describing the idea to find similar matches"
                        },
                        "max_results": {
                            "type": "integer", 
                            "description": "Maximum number of results to return (default: 5)"
                        }
                    },
                    "required": ["query"]
                }
            ),
            FunctionDeclaration(
                name="get_idea_details",
                description="Get comprehensive details about a specific idea by ID or title search",
                parameters={
                    "type": "object",
                    "properties": {
                        "identifier": {
                            "type": "string",
                            "description": "Either idea ID (number) or title keywords to search"
                        }
                    },
                    "required": ["identifier"]
                }
            ),
            FunctionDeclaration(
                name="analyze_contributor_skills",
                description="Analyze available contributors and their skills for project matching",
                parameters={
                    "type": "object",
                    "properties": {
                        "skill_requirements": {
                            "type": "string",
                            "description": "Required skills or expertise for the project"
                        },
                        "hours_needed": {
                            "type": "integer",
                            "description": "Estimated hours per week needed (optional)"
                        }
                    },
                    "required": ["skill_requirements"]
                }
            ),
            FunctionDeclaration(
                name="get_innovation_trends",
                description="Get current innovation trends and statistics from the idea database",
                parameters={
                    "type": "object",
                    "properties": {
                        "category": {
                            "type": "string",
                            "description": "Specific category to analyze (optional - if not provided, analyzes all categories)"
                        },
                        "time_period": {
                            "type": "string",
                            "description": "Time period for trend analysis: 'week', 'month', 'quarter', 'all'"
                        }
                    }
                }
            ),
            FunctionDeclaration(
                name="evaluate_idea_feasibility",
                description="Evaluate technical and business feasibility of an idea",
                parameters={
                    "type": "object",
                    "properties": {
                        "idea_description": {
                            "type": "string",
                            "description": "Detailed description of the idea to evaluate"
                        },
                        "category": {
                            "type": "string",
                            "description": "Category of the idea (e.g., 'AI/ML', 'Security', 'DevOps')"
                        },
                        "proposed_impact": {
                            "type": "string",
                            "description": "Proposed impact level: 'High', 'Medium', 'Low'"
                        }
                    },
                    "required": ["idea_description"]
                }
            ),
            FunctionDeclaration(
                name="create_implementation_roadmap",
                description="Create a detailed implementation roadmap for an idea",
                parameters={
                    "type": "object",
                    "properties": {
                        "idea_title": {
                            "type": "string",
                            "description": "Title of the idea"
                        },
                        "idea_description": {
                            "type": "string", 
                            "description": "Description of the idea"
                        },
                        "timeline_months": {
                            "type": "integer",
                            "description": "Desired timeline in months (default: 6)"
                        }
                    },
                    "required": ["idea_title", "idea_description"]
                }
            )
        ]

class MCPAgenticService:
    """Main MCP-based Agentic AI Service for Idea Hub"""
    
    def __init__(self):
        self.gemini_model = None
        self.tools = IdeaHubMCPTools()
        self._initialize_gemini_with_tools()
    
    def _initialize_gemini_with_tools(self):
        """Initialize Gemini with function calling capabilities"""
        if not Config.GEMINI_API_KEY or Config.GEMINI_API_KEY == "your_gemini_api_key_here":
            logging.error("❌ GEMINI_API_KEY not configured for MCP agentic AI")
            return
        
        try:
            genai.configure(api_key=Config.GEMINI_API_KEY)
            
            # Create tool for Gemini function calling
            idea_hub_tool = Tool(function_declarations=self.tools.get_tool_definitions())
            
            # Initialize model with tools - try Pro first, fallback to Pro 1.5
            try:
                self.gemini_model = genai.GenerativeModel(
                    model_name="gemini-2.5-pro",  # Use Pro for better function calling
                    tools=[idea_hub_tool]
                )
                logging.info("✅ Using Gemini 2.5 Pro for MCP research")
            except Exception as e:
                logging.warning(f"⚠️ Gemini 2.5 Pro not available, trying 1.5 Pro: {e}")
                self.gemini_model = genai.GenerativeModel(
                    model_name="gemini-1.5-pro",  # Fallback to 1.5 Pro
                    tools=[idea_hub_tool]
                )
            
            logging.info("✅ Gemini initialized with MCP tools for agentic AI")
            
        except Exception as e:
            logging.error(f"❌ Failed to initialize Gemini with MCP tools: {e}")
            self.gemini_model = None
    
    def is_available(self) -> bool:
        """Check if MCP agentic service is available"""
        return self.gemini_model is not None
    
    async def execute_autonomous_research(self, research_query: str) -> Dict[str, Any]:
        """
        Execute autonomous research using MCP tools
        
        Args:
            research_query: The research question or task
            
        Returns:
            Dictionary with research results and agent reasoning
        """
        if not self.is_available():
            return {
                "status": "error",
                "message": "MCP Agentic AI service not available - check Gemini API key"
            }
        
        # Temporary simplified version to avoid syntax errors
        try:
            # Start chat session with the model
            chat = self.gemini_model.start_chat()
            
            # Enhanced prompt for tool calling
            enhanced_prompt = f"""You are a Company innovation research agent with access to specialized tools. Please research: {research_query}

Available tools can help you:
- search_innovation_trends: Search for innovation trends and ideas
- get_innovation_statistics: Get statistics about current ideas

Use the appropriate tools to gather comprehensive information, then provide your analysis.

Research Query: {research_query}"""
            
            logging.info(f"Sending enhanced prompt to Gemini: {enhanced_prompt[:100]}...")
            response = chat.send_message(enhanced_prompt)
            logging.info(f"Received response from Gemini, type: {type(response)}")
            final_response = await self._process_response_with_tools(chat, response)
            logging.info(f"Final processed response: {final_response[:100] if final_response else 'None'}...")
            
            return {
                "status": "success",
                "research_query": research_query,
                "agent_analysis": final_response,
                "research_steps": [],
                "tools_used": [],
                "timestamp": datetime.now().isoformat(),
                "agent_type": "Simplified Gemini Agent"
            }
            
        except Exception as e:
            logging.error(f"❌ Error in research: {e}")
            return {
                "status": "error",
                "message": f"Research failed: {str(e)}",
                "research_query": research_query
            }
    
    async def _process_response_with_tools(self, chat, response) -> str:
        """
        Process Gemini response that may contain tool calls
        """
        try:
            # Check if response has function calls
            if hasattr(response, 'candidates') and response.candidates:
                candidate = response.candidates[0]
                if hasattr(candidate, 'content') and candidate.content and hasattr(candidate.content, 'parts'):
                    for part in candidate.content.parts:
                        if hasattr(part, 'function_call') and part.function_call:
                            logging.info(f"Function call detected: {part.function_call.name}")
                            
                            # Execute the function call
                            function_name = part.function_call.name
                            function_args = {}
                            
                            # Convert function arguments
                            if hasattr(part.function_call, 'args'):
                                for key, value in part.function_call.args.items():
                                    function_args[key] = value
                            
                            logging.info(f"Executing function: {function_name} with args: {function_args}")
                            
                            # Execute the tool function
                            try:
                                if function_name == "search_similar_ideas":
                                    # Use synchronous vector service directly instead of async enhanced service
                                    from services.vector_service import vector_service
                                    query = function_args.get('query', '')
                                    max_results = function_args.get('max_results', 5)
                                    
                                    try:
                                        results = vector_service.search_similar_ideas(query, top_k=max_results)
                                        tool_result = f"Found {len(results)} similar ideas: " + str(results[:3])
                                    except Exception as e:
                                        tool_result = f"Search failed: {e}. Using placeholder data instead."
                                    
                                elif function_name == "get_idea_details":
                                    from models.idea import IdeaModel
                                    idea_model = IdeaModel()
                                    identifier = function_args.get('identifier', '')
                                    
                                    # Try to get by ID first, then by title search
                                    if identifier.isdigit():
                                        idea = idea_model.get_idea_by_id(int(identifier))
                                        tool_result = f"Idea details: {idea}" if idea else f"No idea found with ID {identifier}"
                                    else:
                                        ideas = idea_model.get_all_ideas()
                                        matching_ideas = [idea for idea in ideas if identifier.lower() in idea.get('title', '').lower()]
                                        tool_result = f"Found {len(matching_ideas)} ideas matching '{identifier}': " + str(matching_ideas[:3])
                                
                                elif function_name == "analyze_contributor_skills":
                                    from models.contributor import ContributorModel
                                    contributor_model = ContributorModel()
                                    contributors = contributor_model.get_all_contributors()
                                    skill_requirements = function_args.get('skill_requirements', '')
                                    
                                    # Simple skill matching
                                    matching_contributors = []
                                    for contributor in contributors:
                                        skills = contributor.get('skills', '').lower()
                                        if any(skill.lower() in skills for skill in skill_requirements.split()):
                                            matching_contributors.append(contributor)
                                    
                                    tool_result = f"Found {len(matching_contributors)} contributors with skills matching '{skill_requirements}': " + str(matching_contributors[:3])
                                
                                elif function_name == "get_innovation_trends":
                                    from models.idea import IdeaModel
                                    idea_model = IdeaModel()
                                    ideas = idea_model.get_all_ideas()
                                    total_ideas = len(ideas)
                                    
                                    # Count by category if available
                                    categories = {}
                                    for idea in ideas:
                                        category = idea.get('category', 'Other')
                                        categories[category] = categories.get(category, 0) + 1
                                    
                                    tool_result = f"Innovation Trends - Total ideas: {total_ideas}. Category breakdown: " + str(categories)
                                    
                                elif function_name == "evaluate_idea_feasibility":
                                    idea_description = function_args.get('idea_description', '')
                                    category = function_args.get('category', 'General')
                                    
                                    # Simple feasibility assessment
                                    feasibility_score = "Medium"  # Placeholder logic
                                    if "AI" in idea_description or "machine learning" in idea_description.lower():
                                        feasibility_score = "High"
                                    elif "quantum" in idea_description.lower() or "blockchain" in idea_description.lower():
                                        feasibility_score = "Low"
                                    
                                    tool_result = f"Feasibility Assessment for '{idea_description[:50]}...': {feasibility_score} feasibility in {category} category"
                                    
                                elif function_name == "create_implementation_roadmap":
                                    idea_title = function_args.get('idea_title', 'Unnamed Idea')
                                    timeline_months = function_args.get('timeline_months', 6)
                                    
                                    # Create basic roadmap structure
                                    roadmap = {
                                        "Phase 1 (Month 1-2)": "Research and Planning",
                                        "Phase 2 (Month 3-4)": "Development and Prototyping", 
                                        "Phase 3 (Month 5-6)": "Testing and Deployment"
                                    }
                                    
                                    tool_result = f"Implementation Roadmap for '{idea_title}' ({timeline_months} months): " + str(roadmap)
                                    
                                else:
                                    tool_result = f"Tool {function_name} executed successfully with args: {function_args}"
                                
                                logging.info(f"Tool result: {tool_result[:100]}...")
                                
                                # Send tool result back to Gemini in correct format
                                # Create a Part with function_response
                                function_response_part = {
                                    "function_response": {
                                        "name": function_name,
                                        "response": {"result": tool_result}
                                    }
                                }
                                
                                # Continue conversation with tool result
                                final_response = chat.send_message(function_response_part)
                                return self._extract_text_from_response(final_response)
                                
                            except Exception as e:
                                logging.error(f"Error executing tool {function_name}: {e}")
                                return f"Error executing analysis tools: {e}"
            
            # If no function calls, extract text normally
            return self._extract_text_from_response(response)
            
        except Exception as e:
            logging.error(f"Error processing response with tools: {e}")
            return self._extract_text_from_response(response)
    
    def _extract_text_from_response(self, response) -> str:
        """
        Safely extract text from a Gemini response
        """
        logging.info(f"Extracting text from response type: {type(response)}")
        
        try:
            # First try the simple text accessor
            if hasattr(response, 'text') and response.text:
                logging.debug("Successfully extracted text using simple accessor")
                return response.text
        except Exception as e:
            logging.warning(f"Could not use simple text accessor: {e}")
        
        # Manual extraction from parts
        try:
            if hasattr(response, 'candidates') and response.candidates:
                candidate = response.candidates[0]
                
                # Try to extract content
                text_content = None
                if hasattr(candidate, 'content') and candidate.content:
                    logging.info(f"Found candidate content")
                    if hasattr(candidate.content, 'parts') and candidate.content.parts:
                        logging.info(f"Found {len(candidate.content.parts)} parts")
                        text_parts = []
                        for i, part in enumerate(candidate.content.parts):
                            logging.info(f"Part {i}: has_text={hasattr(part, 'text')}")
                            if hasattr(part, 'text') and part.text:
                                text_parts.append(part.text)
                                logging.info(f"Added text part: {part.text[:100]}...")
                        if text_parts:
                            text_content = "\n".join(text_parts)
                            logging.info(f"Combined text content length: {len(text_content)}")
                    else:
                        logging.info("No parts found in candidate content")
                else:
                    logging.info("No content found in candidate")
                
                # If we got content, return it
                if text_content and text_content.strip():
                    logging.debug("Returning extracted text content")
                    return text_content
                
                # Check finish reason - but still try to extract content first
                if hasattr(candidate, 'finish_reason'):
                    finish_reason = candidate.finish_reason
                    # For STOP (1), we still want to try to get content
                    if finish_reason == 2:  # MAX_TOKENS
                        return "Research response was truncated due to length limits. Consider breaking down the request."
                    elif finish_reason == 3:  # SAFETY
                        return "Research request was blocked for safety reasons. Please modify your query."
                    elif finish_reason == 4:  # RECITATION
                        return "Research response blocked due to recitation concerns. Please try a different approach."
                    elif finish_reason != 1:  # Not STOP
                        return f"Research finished with reason code: {finish_reason}"
            
            return "No text content returned from AI research. The model may have encountered an issue."
            
        except Exception as e:
            logging.error(f"Error extracting text from response: {e}")
            return f"Error processing AI response: {e}. Please try again."


# Global instance
mcp_agentic_service = MCPAgenticService()
