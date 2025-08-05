"""
Red Hat Idea Hub - MCP Agentic AI Service
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
# MCP TOOLS FOR RED HAT IDEA HUB
#=============================================================================

class IdeaHubMCPTools:
    """MCP Tools for Red Hat Idea Hub operations"""
    
    @staticmethod
    def get_tool_definitions() -> List[FunctionDeclaration]:
        """Get Gemini function declarations for MCP tools"""
        return [
            FunctionDeclaration(
                name="search_similar_ideas",
                description="Search for similar ideas in the Red Hat Idea Hub database using semantic similarity",
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
    """Main MCP-based Agentic AI Service for Red Hat Idea Hub"""
    
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
            
            # Initialize model with tools
            self.gemini_model = genai.GenerativeModel(
                model_name="gemini-2.5-pro",  # Use Pro for better function calling
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
        
        try:
            # Start chat session with the model
            chat = self.gemini_model.start_chat()
            
            # System prompt for autonomous research
            system_prompt = f"""
            You are an intelligent Red Hat Innovation Research Agent with access to specialized tools.
            
            Your task: {research_query}
            
            You can use the following tools to gather information:
            1. search_similar_ideas - Find related ideas in the database
            2. get_idea_details - Get detailed information about specific ideas
            3. analyze_contributor_skills - Find contributors with relevant expertise
            4. get_innovation_trends - Analyze innovation patterns and trends
            5. evaluate_idea_feasibility - Assess technical and business feasibility
            6. create_implementation_roadmap - Generate implementation plans
            
            Guidelines:
            - Use multiple tools to gather comprehensive information
            - Analyze the data you collect to form insights
            - Provide specific, actionable recommendations
            - Explain your reasoning for each recommendation
            - Focus on Red Hat's strategic interests and capabilities
            
            Begin your research now by using the appropriate tools.
            """
            
            # Send the research query
            response = chat.send_message(system_prompt)
            
            # Track tool calls and results
            research_steps = []
            function_results = []
            
            # Process function calls
            while response.candidates[0].content.parts:
                part = response.candidates[0].content.parts[0]
                
                # Check if this is a function call
                if hasattr(part, 'function_call') and part.function_call:
                    function_call = part.function_call
                    function_name = function_call.name
                    function_args = dict(function_call.args)
                    
                    logging.info(f"🤖 Agent calling tool: {function_name} with args: {function_args}")
                    
                    # Execute the function call
                    try:
                        result = await self._execute_tool_call(function_name, function_args)
                        
                        research_steps.append({
                            "tool": function_name,
                            "args": function_args,
                            "result": result,
                            "timestamp": datetime.now().isoformat()
                        })
                        
                        # Send function result back to model using proper format
                        function_response = {
                            "function_response": {
                                "name": function_name,
                                "response": {"result": str(result)}
                            }
                        }
                        response = chat.send_message([function_response])
                        
                    except Exception as e:
                        error_msg = f"Error executing {function_name}: {str(e)}"
                        logging.error(f"❌ {error_msg}")
                        
                        # Send error back to model using proper format
                        error_response = {
                            "function_response": {
                                "name": function_name,
                                "response": {"error": error_msg}
                            }
                        }
                        response = chat.send_message([error_response])
                else:
                    # This is the final response
                    break
            
            # Get final analysis - safely extract text from response
            final_response = self._extract_text_from_response(response)
            
            return {
                "status": "success",
                "research_query": research_query,
                "agent_analysis": final_response,
                "research_steps": research_steps,
                "tools_used": [step["tool"] for step in research_steps],
                "timestamp": datetime.now().isoformat(),
                "agent_type": "MCP-powered Gemini Agent"
            }
            
        except Exception as e:
            logging.error(f"❌ Error in autonomous research: {e}")
            return {
                "status": "error",
                "message": f"Research failed: {str(e)}",
                "research_query": research_query
            }
    
    def _extract_text_from_response(self, response) -> str:
        """
        Safely extract text from a Gemini response, handling function calls
        """
        try:
            # Try to get text directly first
            if hasattr(response, 'text') and response.text:
                return response.text
        except Exception:
            # If direct text access fails, manually extract text parts
            pass
        
        # Manually extract text from parts
        text_parts = []
        try:
            if hasattr(response, 'candidates') and response.candidates:
                candidate = response.candidates[0]
                if hasattr(candidate, 'content') and candidate.content:
                    for part in candidate.content.parts:
                        if hasattr(part, 'text') and part.text:
                            text_parts.append(part.text)
        except Exception as e:
            logging.warning(f"Could not extract text from response: {e}")
        
        if text_parts:
            return "\n".join(text_parts)
        else:
            return "Research completed successfully. Please check the tool results for detailed findings."

    async def _execute_tool_call(self, function_name: str, args: Dict[str, Any]) -> str:
        """Execute a tool call and return the result"""
        
        if function_name == "search_similar_ideas":
            query = args.get("query", "")
            max_results = args.get("max_results", 5)
            
            try:
                similar_ideas = vector_service.search_similar_ideas(query, top_k=max_results)
                if not similar_ideas:
                    return f"No similar ideas found for query: {query}"
                
                results = []
                for idea in similar_ideas:
                    results.append(f"• {idea['title']} ({idea['similarity']:.1f}% match) - {idea['category']} by {idea['contributor']}")
                
                return f"Found {len(similar_ideas)} similar ideas:\n" + "\n".join(results)
                
            except Exception as e:
                return f"Error searching ideas: {str(e)}"
        
        elif function_name == "get_idea_details":
            identifier = args.get("identifier", "")
            
            try:
                # Try to get by ID first
                if identifier.isdigit():
                    idea = IdeaModel.get_idea_by_id(int(identifier))
                    if idea:
                        return f"""
                        Title: {idea['title']}
                        Description: {idea['description']}
                        Category: {idea['category']}
                        Impact: {idea['impact']}
                        Status: {idea['status']}
                        Contributor: {idea['contributor']}
                        Created: {idea.get('created_at', 'Unknown')}
                        Abstract: {idea.get('abstract', 'No abstract available')}
                        """
                
                # Search by title/keywords in all ideas
                all_ideas = IdeaModel.get_all_ideas()
                matching_ideas = []
                
                for idea in all_ideas:
                    # Check if identifier matches title (case-insensitive partial match)
                    if identifier.lower() in idea['title'].lower():
                        matching_ideas.append(idea)
                
                if not matching_ideas:
                    return f"No idea found matching: {identifier}"
                
                idea = matching_ideas[0]  # Get first match
                return f"""
                Title: {idea['title']}
                Description: {idea['description']}
                Category: {idea['category']}
                Impact: {idea['impact']}
                Status: {idea['status']}
                Contributor: {idea['contributor']}
                Abstract: {idea.get('abstract', 'No abstract available')}
                """
                
            except Exception as e:
                return f"Error getting idea details: {str(e)}"
        
        elif function_name == "analyze_contributor_skills":
            skill_requirements = args.get("skill_requirements", "")
            hours_needed = args.get("hours_needed")
            
            try:
                contributors = ContributorModel.search_contributors(skill_requirements)
                if not contributors:
                    return f"No contributors found with skills matching: {skill_requirements}"
                
                # Filter by hours if specified
                if hours_needed:
                    contributors = [c for c in contributors if c.get('hours_available', 0) >= hours_needed]
                
                results = []
                for contributor in contributors[:10]:  # Limit to top 10
                    hours_info = f"({contributor.get('hours_available', 'Unknown')}h/week available)" if contributor.get('hours_available') else ""
                    results.append(f"• {contributor['name']} - {contributor.get('skillset', 'No skills listed')} {hours_info}")
                
                return f"Found {len(contributors)} contributors with relevant skills:\n" + "\n".join(results)
                
            except Exception as e:
                return f"Error analyzing contributors: {str(e)}"
        
        elif function_name == "get_innovation_trends":
            category = args.get("category")
            time_period = args.get("time_period", "month")
            
            try:
                stats = IdeaModel.get_dashboard_stats()
                
                trend_analysis = f"""
                Innovation Trends Analysis:
                
                Total Ideas: {stats.get('total_ideas', 0)}
                Recent Activity: {stats.get('recent_submissions', 0)} ideas in the last week
                Active Contributors: {stats.get('unique_contributors', 0)} unique contributors
                
                Categories Distribution:
                """
                
                categories = stats.get('category_breakdown', {})
                total_ideas = stats.get('total_ideas', 1)
                for cat, count in categories.items():
                    percentage = (count / total_ideas) * 100
                    trend_analysis += f"• {cat}: {count} ideas ({percentage:.1f}%)\n"
                
                trend_analysis += f"""
                Impact Distribution:
                """
                
                impacts = stats.get('impact_breakdown', {})
                for impact, count in impacts.items():
                    percentage = (count / total_ideas) * 100
                    trend_analysis += f"• {impact} Impact: {count} ideas ({percentage:.1f}%)\n"
                
                trend_analysis += f"""
                Status Overview:
                """
                
                statuses = stats.get('status_breakdown', {})
                for status, count in statuses.items():
                    percentage = (count / total_ideas) * 100
                    trend_analysis += f"• {status}: {count} ideas ({percentage:.1f}%)\n"
                
                if category:
                    # Focus on specific category
                    category_count = categories.get(category, 0)
                    if category_count > 0:
                        trend_analysis += f"\nFocus on {category}: {category_count} ideas represent {(category_count/total_ideas*100):.1f}% of all innovations"
                    else:
                        trend_analysis += f"\nNo ideas found in {category} category"
                
                return trend_analysis
                
            except Exception as e:
                return f"Error analyzing trends: {str(e)}"
        
        elif function_name == "evaluate_idea_feasibility":
            idea_description = args.get("idea_description", "")
            category = args.get("category", "")
            proposed_impact = args.get("proposed_impact", "")
            
            # Rule-based feasibility assessment (could be enhanced with ML)
            feasibility_analysis = f"""
            Feasibility Assessment for: {category} idea
            
            Technical Feasibility:
            """
            
            # Analyze technical complexity
            complexity_indicators = {
                "High Complexity": ["machine learning", "artificial intelligence", "distributed system", "blockchain", "quantum", "real-time processing"],
                "Medium Complexity": ["web application", "mobile app", "automation", "integration", "api", "microservice"],
                "Low Complexity": ["dashboard", "report", "form", "simple tool", "basic automation", "script"]
            }
            
            description_lower = idea_description.lower()
            
            for complexity, keywords in complexity_indicators.items():
                if any(keyword in description_lower for keyword in keywords):
                    if complexity == "High Complexity":
                        feasibility_analysis += "• High technical complexity - Requires specialized expertise and significant development time\n"
                        feasibility_analysis += "• Recommend: Phased approach, proof-of-concept first\n"
                    elif complexity == "Medium Complexity":
                        feasibility_analysis += "• Moderate technical complexity - Standard development practices apply\n"
                        feasibility_analysis += "• Recommend: Standard project timeline, regular checkpoints\n"
                    else:
                        feasibility_analysis += "• Low technical complexity - Straightforward implementation\n"
                        feasibility_analysis += "• Recommend: Fast-track development, minimal risk\n"
                    break
            else:
                feasibility_analysis += "• Technical complexity unclear - Recommend technical review\n"
            
            # Analyze business impact alignment
            feasibility_analysis += f"""
            
            Business Impact Assessment:
            • Proposed Impact Level: {proposed_impact}
            • Category Alignment: {category} is a strategic focus area for Red Hat
            """
            
            if proposed_impact == "High":
                feasibility_analysis += "• High impact potential - Prioritize for executive review\n"
            elif proposed_impact == "Medium":
                feasibility_analysis += "• Solid business value - Good candidate for standard innovation pipeline\n"
            else:
                feasibility_analysis += "• Incremental improvement - Consider for quick wins program\n"
            
            return feasibility_analysis
        
        elif function_name == "create_implementation_roadmap":
            idea_title = args.get("idea_title", "")
            idea_description = args.get("idea_description", "")
            timeline_months = args.get("timeline_months", 6)
            
            roadmap = f"""
            Implementation Roadmap for: {idea_title}
            Timeline: {timeline_months} months
            
            Phase 1 (Month 1-2): Discovery & Planning
            • Requirements gathering and stakeholder alignment
            • Technical architecture design
            • Resource allocation and team formation
            • Risk assessment and mitigation planning
            
            Phase 2 (Month 2-4): Development & Testing
            • Core functionality development
            • Integration with existing Red Hat systems
            • Unit testing and quality assurance
            • Security review and compliance validation
            
            Phase 3 (Month 4-{timeline_months}): Deployment & Optimization
            • Pilot deployment with selected users
            • Performance monitoring and optimization
            • User feedback collection and iteration
            • Full production rollout
            
            Key Deliverables:
            • Technical specification document
            • Working prototype/MVP
            • Production-ready solution
            • Documentation and training materials
            
            Success Metrics:
            • User adoption rate
            • Performance benchmarks
            • Business impact measurement
            • ROI analysis
            
            Risk Mitigation:
            • Regular checkpoint reviews
            • Fallback planning for critical dependencies
            • Stakeholder communication plan
            • Change management strategy
            """
            
            return roadmap
        
        else:
            return f"Unknown tool: {function_name}"

#=============================================================================
# GLOBAL INSTANCE
#=============================================================================

# Global instance for use across the application
mcp_agentic_service = MCPAgenticService()