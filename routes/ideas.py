"""
Ideas routes for idea management
"""

from flask import Blueprint, request, jsonify
from models.idea import IdeaModel
from services.vector_service import vector_service
from services.ai_service import gemini_service
from services.ai_service_enhanced import enhanced_ai_service
from services.pdf_service import pdf_service
from services.ai_summary_service import ai_summary_service
from utils.sample_data import get_sample_ideas
from database.setup import init_database
import logging

ideas_bp = Blueprint('ideas', __name__)

@ideas_bp.route('/api/init-database', methods=['POST'])
def initialize_database():
    """Initialize database with tables and extensions"""
    try:
        result = init_database()
        return jsonify(result)
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500

@ideas_bp.route('/api/clear-vector-store', methods=['POST'])
def clear_vector_store():
    """Clear vector store and reinitialize (fixes dimension mismatch)"""
    try:
        result = vector_service.clear_vector_store()
        return jsonify(result)
    except Exception as e:
        logging.error(f"❌ Error clearing vector store: {e}")
        return jsonify({"status": "error", "error": str(e)}), 500

@ideas_bp.route('/api/load-sample-data', methods=['POST'])
def load_sample_data():
    """Load sample data from notebook into database and vector store"""
    try:
        # Get sample ideas
        sample_ideas = get_sample_ideas()
        
        # Clear existing data
        IdeaModel.clear_all_ideas()
        vector_service.clear_vector_store()
        
        # Insert ideas into database
        created_ideas = []
        for idea_data in sample_ideas:
            created_idea = IdeaModel.create_idea(idea_data)
            created_ideas.append(created_idea)
        
        # Load ideas into vector store
        vector_result = vector_service.load_ideas_to_vector_store(created_ideas)
        
        return jsonify({
            "message": "Sample data loaded successfully",
            "database_count": len(created_ideas),
            "vector_result": vector_result
        })
        
    except Exception as e:
        logging.error(f"Error loading sample data: {e}")
        return jsonify({"error": str(e)}), 500

@ideas_bp.route('/api/ideas', methods=['GET'])
def get_all_ideas():
    """Get all ideas"""
    try:
        ideas = IdeaModel.get_all_ideas()
        return jsonify({
            "ideas": ideas,
            "count": len(ideas)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@ideas_bp.route('/api/ideas/<int:idea_id>', methods=['GET'])
def get_idea(idea_id):
    """Get a specific idea by ID"""
    try:
        idea = IdeaModel.get_idea_by_id(idea_id)
        if not idea:
            return jsonify({"error": "Idea not found"}), 404
        
        return jsonify(idea)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@ideas_bp.route('/api/ideas/submit', methods=['POST'])
def submit_idea():
    """Submit a new idea with AI similarity checking (with optional PDF)"""
    try:
        # Handle both JSON and form data (for file uploads)
        if request.content_type and 'multipart/form-data' in request.content_type:
            # Form data with possible file upload
            data = request.form.to_dict()
            pdf_file = request.files.get('pdf_file')
        else:
            # JSON data (no file upload)
            data = request.get_json()
            pdf_file = None
        
        # Validate required fields
        required_fields = ['title', 'description', 'contributor', 'category', 'impact']
        for field in required_fields:
            if not data.get(field):
                return jsonify({"error": f"{field} is required"}), 400
        
        # Check if user wants to override duplicate detection
        override_duplicate = data.get('override_duplicate', False)
        
        # Check for high similarity matches using Enhanced AI service unless overriding
        if not override_duplicate:
            idea_text = f"{data['title']} {data['description']} {data.get('abstract', '')}"
            
            # Use enhanced AI service for duplicate detection (MCP server with fallback)
            logging.info("🔍 Using Enhanced AI service for duplicate detection...")
            duplicates = enhanced_ai_service.detect_duplicates(idea_text, threshold=0.70)
            
            # If enhanced service returns nothing, try local vector service as fallback
            if not duplicates and vector_service.is_available():
                logging.info("🔄 Using local vector service as fallback for duplicate detection")
                similar_ideas = vector_service.search_similar_ideas(idea_text, top_k=10)
                duplicates = []
                for idea in similar_ideas:
                    if idea.get('similarity', 0) >= 70.0:  # 70% threshold
                        duplicates.append({
                            'id': idea.get('id'),
                            'title': idea.get('title', ''),
                            'description': idea.get('description', ''),
                            'contributor': idea.get('contributor', ''),
                            'similarity_score': idea.get('similarity', 0.0) / 100.0  # Convert to 0-1 scale
                        })
            
            if duplicates:
                top_match = duplicates[0]
                similarity_pct = top_match.get('similarity_score', 0.0) * 100
                
                # Generate AI-enhanced summaries using Enhanced AI service
                try:
                    logging.info("🤖 Generating AI summary for duplicate detection...")
                    
                    # Generate summary for the top match
                    summary_text = f"Title: {top_match.get('title', '')}\nDescription: {top_match.get('description', '')}"
                    ai_summary = enhanced_ai_service.generate_summary(summary_text)
                    
                    # Generate collaboration suggestion
                    comparison_context = enhanced_ai_service.generate_collaboration_suggestion(
                        data, top_match, similarity_pct / 100.0
                    )
                    
                    if not ai_summary:
                        ai_summary = f"Existing idea in {top_match.get('category', 'Unknown')} category."
                    if not comparison_context:
                        comparison_context = f"Found {similarity_pct:.1f}% similarity. Review the existing idea before proceeding."
                        
                    logging.info("✅ AI summary generated successfully")
                except Exception as e:
                    logging.warning(f"⚠️ AI summary failed, using fallback: {e}")
                    ai_summary = f"Existing idea by {top_match.get('contributor', 'Unknown contributor')}."
                    comparison_context = f"Found {similarity_pct:.1f}% similarity. Review the existing idea before proceeding."
                
                # Enhance duplicates with AI summaries
                enhanced_duplicates = []
                for i, match in enumerate(duplicates[:3]):  # Top 3 matches
                    match_similarity = match.get('similarity_score', 0.0) * 100
                    enhanced_duplicates.append({
                        **match,
                        "similarity": match_similarity,  # Convert back to percentage for compatibility
                        "ai_summary": ai_summary if i == 0 else f"Similar idea by {match.get('contributor', 'Unknown')}",
                        "comparison_context": comparison_context if i == 0 else f"{match_similarity:.1f}% similarity detected"
                    })
                
                response_data = {
                    "status": "high_similarity_detected", 
                    "message": f"Found {similarity_pct:.1f}% similar idea: '{top_match.get('title', '')}' by {top_match.get('contributor', '')}",
                    "duplicates": enhanced_duplicates,
                    "suggestion": "Review the similar idea and consider collaboration or highlight key differences",
                    "ai_insights": {
                        "similarity_explanation": comparison_context,
                        "existing_idea_summary": ai_summary,
                        "recommendation": "Consider reaching out to collaborate or clearly differentiate your approach",
                        "ai_service": "Enhanced AI (MCP + fallback)"
                    }
                }
                
                logging.info(f"🔍 Sending 409 response with {len(enhanced_duplicates)} duplicates")
                return jsonify(response_data), 409
        
        # Create idea in database
        created_idea = IdeaModel.create_idea(data)
        idea_id = created_idea['id']
        
        # Process PDF if uploaded
        pdf_result = None
        if pdf_file and pdf_file.filename:
            try:
                logging.info(f"Processing PDF upload for idea {idea_id}")
                pdf_result = pdf_service.process_pdf_for_idea(pdf_file, data, idea_id)
                
                # Update idea with PDF information in database
                IdeaModel.update_pdf_info(idea_id, {
                    "pdf_filename": pdf_result["file_info"]["filename"],
                    "pdf_pages": pdf_result["extracted_content"]["total_pages"],
                    "pdf_size": pdf_result["file_info"]["size"]
                })
                
                # Update the in-memory idea object too
                created_idea.update({
                    "pdf_filename": pdf_result["file_info"]["filename"],
                    "pdf_pages": pdf_result["extracted_content"]["total_pages"],
                    "pdf_size": pdf_result["file_info"]["size"]
                })
                
                logging.info(f"✅ PDF processed successfully for idea {idea_id}")
                
            except Exception as e:
                logging.error(f"❌ PDF processing failed for idea {idea_id}: {e}")
                # Continue without PDF - idea still gets created
                pdf_result = {"error": str(e)}
        
        # Add to vector store (will include PDF content if available)
        if not pdf_file:  # Only add to vector store if no PDF (PDF processing handles vector storage)
            vector_service.add_idea_to_vector_store(created_idea)
        
        # Check for similar ideas with AI-enhanced summaries for better user understanding
        # Only check if not overriding duplicate detection
        if not override_duplicate:
            search_text = f"{data['title']} {data['description']} {data.get('abstract', '')}"
            similar_ideas = vector_service.search_similar_ideas(search_text, top_k=5)
            
            # Check for high similarity (duplicates) first
            for similar in similar_ideas:
                if similar.get('similarity', 0) >= 80:  # High similarity threshold
                    try:
                        # Generate AI summary for better user understanding
                        ai_summary = ai_summary_service.generate_idea_summary(similar, max_words=250)
                        
                        # Generate comparison context
                        comparison_context = ai_summary_service.generate_comparison_context(
                            data, similar, similar.get('similarity', 0)
                        )
                        
                    except Exception as e:
                        logging.error(f"AI summary generation failed: {e}")
                        # Fallback to basic summary
                        ai_summary = f"Idea: {similar.get('title', '')}. {similar.get('description', '')[:200]}..."
                        comparison_context = f"Found {similar.get('similarity', 0):.1f}% similarity. Consider reviewing the existing idea."
                    # Return duplicate detection with AI insights
                    return jsonify({
                        "status": "duplicate_detected",
                        "message": f"Very similar idea found: '{similar['title']}' by {similar['contributor']}",
                        "suggestion": "Review the existing idea summary below to decide if you should collaborate or proceed with differences",
                        "duplicates": [{
                            **similar,
                            "ai_summary": ai_summary,
                            "comparison_context": comparison_context
                        }],
                        "ai_insights": {
                            "similarity_explanation": comparison_context,
                            "existing_idea_summary": ai_summary,
                            "recommendation": "Consider reaching out to collaborate or clearly differentiate your approach"
                        }
                    }), 409  # Conflict status
        
        # Find collaboration opportunities (medium similarity)
        collaborations = vector_service.find_collaboration_opportunities(data)
        
        # Enhance collaboration suggestions with AI summaries
        enhanced_collaborations = []
        for collab in collaborations[:3]:  # Top 3
            try:
                # Add AI summary for better understanding
                ai_summary = ai_summary_service.generate_idea_summary(collab, max_words=200)
                
                enhanced_collab = {
                    **collab,
                    "ai_summary": ai_summary
                }
                enhanced_collaborations.append(enhanced_collab)
                
            except Exception as e:
                logging.warning(f"Failed to enhance collaboration suggestion: {e}")
                # Add collaboration without AI summary
                enhanced_collab = {
                    **collab,
                    "ai_summary": f"Idea: {collab.get('title', '')}. {collab.get('description', '')[:150]}..."
                }
                enhanced_collaborations.append(enhanced_collab)
        
        # Generate AI collaboration suggestions
        ai_suggestions = []
        if gemini_service.is_available() and enhanced_collaborations:
            for collab in enhanced_collaborations:
                try:
                    suggestion = gemini_service.generate_collaboration_suggestion(
                        new_idea=data,
                        similar_idea=collab,
                        similarity_score=collab['similarity'] / 100
                    )
                    ai_suggestions.append({
                        "similar_idea": collab,
                        "suggestion": suggestion
                    })
                except Exception as e:
                    logging.warning(f"Failed to generate AI suggestion: {e}")
        
        response_data = {
            "status": "success",
            "message": "Idea submitted successfully",
            "idea": created_idea,
            "collaboration_opportunities": collaborations,
            "ai_suggestions": ai_suggestions
        }
        
        # Add PDF information if available
        if pdf_result:
            if "error" in pdf_result:
                response_data["pdf_processing"] = {
                    "status": "failed",
                    "error": pdf_result["error"]
                }
            else:
                response_data["pdf_processing"] = {
                    "status": "success",
                    "filename": pdf_result["file_info"]["filename"],
                    "pages": pdf_result["extracted_content"]["total_pages"],
                    "size": pdf_result["file_info"]["size"],
                    "vector_stored": pdf_result["vector_stored"]
                }
        
        return jsonify(response_data)
        
    except Exception as e:
        logging.error(f"Error submitting idea: {e}")
        return jsonify({"error": str(e)}), 500

@ideas_bp.route('/api/ideas/search', methods=['POST'])
def search_ideas():
    """Search for similar ideas using Enhanced AI service (MCP + fallback)"""
    try:
        data = request.get_json()
        query = data.get('query', '')
        search_type = data.get('search_type', 'hybrid')  # hybrid, semantic, keyword
        limit = data.get('limit', 50)  # Increased default limit since we filter by 70% similarity
        threshold = 0.7  # 70% similarity threshold for quality results
        
        if not query:
            return jsonify({"error": "Query is required"}), 400
        
        # Use enhanced AI service (MCP server with fallback)
        results = enhanced_ai_service.search_ideas(query, search_type, limit, threshold)
        
        # Debug: Check for duplicates in results
        if results:
            logging.info(f"🔍 Enhanced AI service returned {len(results)} results")
            ids_seen = set()
            unique_results = []
            for i, result in enumerate(results):
                result_id = result.get('id')
                logging.info(f"  Result {i}: ID={result_id}, Title={result.get('title')}")
                if result_id not in ids_seen:
                    ids_seen.add(result_id)
                    unique_results.append(result)
                else:
                    logging.warning(f"⚠️ REMOVING duplicate result with ID {result_id} at position {i}")
            
            if len(unique_results) != len(results):
                logging.info(f"🧹 Filtered from {len(results)} to {len(unique_results)} unique results")
            results = unique_results
        
        # If enhanced service returns empty, try local vector service as final fallback
        if not results and vector_service.is_available():
            logging.info("🔄 Using local vector service as final fallback for search")
            local_results = vector_service.search_similar_ideas(query, top_k=limit)
            # Convert local results to expected format
            results = []
            for result in local_results:
                similarity_score = result.get('similarity', 0.0) / 100.0  # Convert percentage to 0-1 scale
                # Only include results above threshold
                if similarity_score >= threshold:
                    results.append({
                        'id': result.get('idea_id'),  # Fix field mapping
                        'title': result.get('title', ''),
                        'description': result.get('content_preview', ''),  # Use content preview as description
                        'contributor': result.get('contributor', ''),
                        'category': result.get('category', ''),
                        'impact': result.get('impact', ''),
                        'similarity_score': similarity_score
                    })
        
        return jsonify({
            "status": "success",
            "query": query,
            "search_type": search_type,
            "results": results,
            "total_found": len(results),
            "similarity_threshold": threshold,
            "ai_service": "Enhanced AI (MCP + fallback)",
            "note": f"AI-powered semantic search with {threshold*100}% minimum similarity threshold"
        })
        
    except Exception as e:
        logging.error(f"Error searching ideas: {e}")
        return jsonify({"error": str(e)}), 500

@ideas_bp.route('/api/mcp/test', methods=['GET'])
def test_mcp_integration():
    """Test MCP server integration and capabilities"""
    try:
        result = {
            "mcp_client_available": False,
            "mcp_server_healthy": False,
            "enhanced_ai_available": False,
            "embedding_stats": None,
            "test_search": None,
            "error": None
        }
        
        # Test Enhanced AI Service availability
        if enhanced_ai_service.is_available():
            result["enhanced_ai_available"] = True
            
            # Test MCP client specifically  
            from services.mcp_client import mcp_client
            if enhanced_ai_service.mcp_enabled and mcp_client:
                result["mcp_client_available"] = True
                
                if mcp_client.is_available():
                    result["mcp_server_healthy"] = True
                    
                    # Get embedding stats from MCP server
                    try:
                        stats = enhanced_ai_service.get_embedding_stats()
                        result["embedding_stats"] = stats
                    except Exception as e:
                        result["embedding_stats_error"] = str(e)
                    
                    # Test search functionality
                    try:
                        test_results = enhanced_ai_service.search_ideas("machine learning", limit=3)
                        result["test_search"] = {
                            "query": "machine learning",
                            "results_count": len(test_results),
                            "first_result": test_results[0] if test_results else None
                        }
                    except Exception as e:
                        result["test_search_error"] = str(e)
        
        return jsonify({
            "status": "mcp_test_complete",
            "results": result,
            "timestamp": "2025-08-17T13:15:00Z"
        })
        
    except Exception as e:
        logging.error(f"Error testing MCP integration: {e}")
        return jsonify({
            "status": "error", 
            "error": str(e),
            "timestamp": "2025-08-17T13:15:00Z"
        }), 500

@ideas_bp.route('/api/ideas/restore-embeddings', methods=['POST'])
def restore_embeddings():
    """Restore vector embeddings for all existing ideas"""
    try:
        from models.idea import IdeaModel
        from services.vector_service import vector_service
        from services.huggingface_service import huggingface_service
        
        # Check if services are available
        if not huggingface_service.is_available():
            return jsonify({
                "status": "error",
                "message": "HuggingFace service not available"
            }), 500
            
        if not vector_service.is_available():
            return jsonify({
                "status": "error", 
                "message": "Vector service not available"
            }), 500
        
        # Get all ideas from database
        all_ideas = IdeaModel.get_all_ideas()
        logging.info(f"🔄 Restoring embeddings for {len(all_ideas)} ideas...")
        
        if len(all_ideas) == 0:
            return jsonify({
                "status": "success",
                "message": "No ideas found to restore",
                "ideas_processed": 0
            })
        
        # Restore embeddings
        result = vector_service.load_ideas_to_vector_store(all_ideas)
        
        if result["status"] == "success":
            # Test the restoration with a search
            test_results = vector_service.search_similar_ideas("test", top_k=3)
            
            return jsonify({
                "status": "success",
                "message": f"Successfully restored embeddings for {result['count']} ideas",
                "ideas_processed": result['count'],
                "test_search_results": len(test_results),
                "sample_results": [r['title'] for r in test_results[:3]]
            })
        else:
            return jsonify({
                "status": "error",
                "message": f"Failed to restore embeddings: {result.get('error', 'Unknown error')}",
                "ideas_processed": 0
            }), 500
            
    except Exception as e:
        logging.error(f"❌ Error restoring embeddings: {e}")
        return jsonify({
            "status": "error",
            "message": f"Error restoring embeddings: {str(e)}",
            "ideas_processed": 0
        }), 500

@ideas_bp.route('/api/ideas/search-debug', methods=['GET'])
def search_debug():
    """Debug endpoint to check AI search functionality"""
    try:
        from services.vector_service import vector_service
        from services.huggingface_service import huggingface_service
        from services.ai_service import gemini_service
        from config.settings import Config
        
        debug_info = {
            "vector_service": {
                "available": vector_service.is_available(),
                "vector_store_initialized": vector_service.vector_store is not None,
                "collection_name": vector_service.collection_name
            },
            "huggingface_service": {
                "available": huggingface_service.is_available(),
                "current_model": getattr(huggingface_service, 'current_model', None),
                "embedding_model_initialized": huggingface_service.embedding_model is not None
            },
            "gemini_service": {
                "available": gemini_service.is_available(),
                "api_key_set": bool(gemini_service.api_key and gemini_service.api_key != ""),
                "model_name": gemini_service.model_name
            },
            "database": {
                "connection_string": Config.DATABASE_URL[:50] + "..." if Config.DATABASE_URL else None,
                "vector_table": Config.VECTOR_TABLE_NAME
            }
        }
        
        # Test embeddings
        if huggingface_service.is_available():
            try:
                test_embedding = huggingface_service.generate_embedding("test innovation query")
                debug_info["huggingface_service"]["test_embedding_length"] = len(test_embedding)
                debug_info["huggingface_service"]["test_successful"] = True
                debug_info["huggingface_service"]["embedding_dimension"] = huggingface_service.embedding_dimension
                debug_info["huggingface_service"]["first_few_values"] = test_embedding[:5] if test_embedding else []
            except Exception as e:
                debug_info["huggingface_service"]["test_error"] = str(e)
                debug_info["huggingface_service"]["test_successful"] = False
        else:
            debug_info["huggingface_service"]["test_successful"] = False
            debug_info["huggingface_service"]["reason"] = "Service not available"
        
        # Test vector search
        if vector_service.is_available():
            try:
                test_results = vector_service.search_similar_ideas("test innovation cloud automation", top_k=3)
                debug_info["vector_service"]["test_search_results"] = len(test_results)
                debug_info["vector_service"]["test_successful"] = True
                debug_info["vector_service"]["sample_results"] = [
                    {"title": r.get("title", ""), "similarity": r.get("similarity", 0)} 
                    for r in test_results[:2]
                ] if test_results else []
            except Exception as e:
                debug_info["vector_service"]["test_error"] = str(e)
                debug_info["vector_service"]["test_successful"] = False
        else:
            debug_info["vector_service"]["test_successful"] = False
            debug_info["vector_service"]["reason"] = "Vector store not initialized"
        
        return jsonify({
            "status": "success",
            "debug_info": debug_info,
            "recommendations": [
                "Check logs for detailed error messages",
                "Verify GEMINI_API_KEY is set in .env file", 
                "Ensure PostgreSQL pgvector extension is installed",
                "Install new LangChain packages: pip install langchain-huggingface langchain-postgres",
                "Try restarting the application to re-initialize services",
                "Ensure mixedbread model is properly cached and accessible"
            ],
            "fixes_applied": [
                "✅ Simplified to use only working mixedbread model",
                "✅ Removed fallback embedding models",
                "✅ Fixed vector service connection issues", 
                "✅ Enhanced error handling and logging",
                "✅ Updated LangChain dependencies",
                "✅ Suppressed non-critical SSL warnings"
            ]
        })
        
    except Exception as e:
        logging.error(f"Error in search debug: {e}")
        return jsonify({"status": "error", "error": str(e)}), 500

@ideas_bp.route('/api/ideas/test-duplicates', methods=['POST'])
def test_duplicate_detection():
    """Test endpoint to check duplicate detection based on text content"""
    try:
        data = request.get_json()
        test_text = data.get('text', '')
        threshold = data.get('threshold', 0.7)  # 70% default
        
        if not test_text:
            return jsonify({"error": "Text is required"}), 400
        
        logging.info(f"🧪 Testing duplicate detection for: '{test_text[:50]}...'")
        
        # Use enhanced AI service for duplicate detection
        duplicates = enhanced_ai_service.detect_duplicates(test_text, threshold)
        
        return jsonify({
            "status": "success",
            "test_text": test_text[:100] + "..." if len(test_text) > 100 else test_text,
            "threshold": threshold,
            "duplicates_found": len(duplicates),
            "duplicates": duplicates,
            "message": f"Found {len(duplicates)} similar ideas above {threshold*100}% threshold"
        })
        
    except Exception as e:
        logging.error(f"Error testing duplicate detection: {e}")
        return jsonify({"error": str(e)}), 500

@ideas_bp.route('/api/ideas/upload-pdf', methods=['POST'])
def upload_pdf_test():
    """Test endpoint for PDF upload and processing"""
    try:
        if 'pdf_file' not in request.files:
            return jsonify({"error": "No PDF file provided"}), 400
        
        pdf_file = request.files['pdf_file']
        
        if pdf_file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        if not pdf_service.is_allowed_file(pdf_file.filename):
            return jsonify({"error": "Invalid file type. Only PDF files are allowed."}), 400
        
        # Test PDF processing without creating an idea
        test_idea_data = {
            "title": "PDF Test Idea",
            "description": "Testing PDF upload functionality",
            "abstract": "This is a test for PDF processing",
            "contributor": "TestUser",
            "category": "Test",
            "impact": "Low"
        }
        
        # Process the PDF
        test_id = 999  # Test ID
        pdf_result = pdf_service.process_pdf_for_idea(pdf_file, test_idea_data, test_id)
        
        return jsonify({
            "status": "success",
            "message": "PDF processed successfully",
            "file_info": pdf_result["file_info"],
            "extracted_content": {
                "total_pages": pdf_result["extracted_content"]["total_pages"],
                "total_characters": pdf_result["extracted_content"]["total_characters"],
                "preview": pdf_result["extracted_content"]["full_text"][:500] + "..." if len(pdf_result["extracted_content"]["full_text"]) > 500 else pdf_result["extracted_content"]["full_text"]
            },
            "vector_stored": pdf_result["vector_stored"]
        })
        
    except Exception as e:
        logging.error(f"Error processing PDF upload: {e}")
        return jsonify({"error": str(e)}), 500 