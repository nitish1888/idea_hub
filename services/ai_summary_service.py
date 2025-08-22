"""
AI Summary Service for Idea Comparison
Uses Gemini LLM to generate concise summaries of existing ideas
to help users understand similarity during submission
"""

import logging
from services.ai_service import gemini_service

class AISummaryService:
    """Service for generating AI summaries of ideas for comparison"""
    
    def __init__(self):
        self.gemini = gemini_service
    
    def is_available(self):
        """Check if AI service is available"""
        return self.gemini.is_available()
    
    def generate_idea_summary(self, idea_data, max_words=250):
        """
        Generate a concise summary of an existing idea for comparison
        
        Args:
            idea_data: Dict with idea information
            max_words: Maximum words in summary (default 250, user wanted <300)
        
        Returns:
            String summary or fallback text
        """
        if not self.is_available():
            # Fallback to basic summary if AI not available
            return self._create_basic_summary(idea_data, max_words)
        
        prompt = f"""
        Create a clear, concise summary of this Company idea in exactly {max_words} words or less.
        
        Title: {idea_data.get('title', '')}
        Description: {idea_data.get('description', '')}
        Abstract: {idea_data.get('abstract', '')}
        Category: {idea_data.get('category', '')}
        Impact: {idea_data.get('impact', '')}
        Contributor: {idea_data.get('contributor', '')}
        
        Write a summary that helps someone quickly understand:
        1. What the idea does
        2. The main technology/approach used
        3. The expected benefit or impact
        
        Keep it under {max_words} words, clear and informative for comparison purposes.
        """
        
        try:
            summary = self.gemini.generate_text(prompt)
            
            # Ensure it's within word limit
            words = summary.split()
            if len(words) > max_words:
                summary = ' '.join(words[:max_words]) + "..."
            
            return summary.strip()
            
        except Exception as e:
            logging.error(f"AI summary generation failed: {e}")
            return self._create_basic_summary(idea_data, max_words)
    
    def _create_basic_summary(self, idea_data, max_words):
        """Fallback basic summary when AI is not available"""
        title = idea_data.get('title', 'Untitled')
        description = idea_data.get('description', '')
        category = idea_data.get('category', '')
        impact = idea_data.get('impact', '')
        contributor = idea_data.get('contributor', '')
        
        # Create basic summary
        summary_parts = []
        
        if title:
            summary_parts.append(f"Idea: {title}")
        
        if description:
            # Truncate description if too long
            desc_words = description.split()
            if len(desc_words) > 50:
                description = ' '.join(desc_words[:50]) + "..."
            summary_parts.append(f"Description: {description}")
        
        if category:
            summary_parts.append(f"Category: {category}")
        
        if impact:
            summary_parts.append(f"Impact: {impact}")
            
        if contributor:
            summary_parts.append(f"By: {contributor}")
        
        basic_summary = '. '.join(summary_parts)
        
        # Ensure word limit
        words = basic_summary.split()
        if len(words) > max_words:
            basic_summary = ' '.join(words[:max_words]) + "..."
        
        return basic_summary
    
    def generate_comparison_context(self, new_idea, similar_idea, similarity_score):
        """
        Generate helpful context for why two ideas are similar
        """
        if not self.is_available():
            return f"Found {similarity_score:.1f}% similarity with existing idea."
        
        prompt = f"""
        Explain in 2-3 sentences why these two Company ideas are similar:
        
        New Idea: "{new_idea.get('title', '')}" - {new_idea.get('description', '')}
        Existing Idea: "{similar_idea.get('title', '')}" - {similar_idea.get('description', '')}
        
        Similarity Score: {similarity_score:.1f}%
        
        Help the user understand what makes them similar and suggest if they should:
        - Collaborate with the existing idea author
        - Proceed with their version highlighting differences
        - Consider merging approaches
        
        Keep it under 100 words, helpful and constructive.
        """
        
        try:
            context = self.gemini.generate_text(prompt)
            return context.strip()
        except Exception as e:
            logging.error(f"Comparison context generation failed: {e}")
            return f"Found {similarity_score:.1f}% similarity. Consider reviewing the existing idea to see if collaboration would be beneficial."
    
    def enhance_search_results(self, search_results):
        """
        Add AI-generated summaries to search results for better user understanding
        """
        if not self.is_available():
            return search_results
        
        enhanced_results = []
        
        for result in search_results:
            try:
                # Generate summary for this result
                summary = self.generate_idea_summary(result, max_words=150)
                
                enhanced_result = {
                    **result,
                    "ai_summary": summary
                }
                enhanced_results.append(enhanced_result)
                
            except Exception as e:
                logging.error(f"Error enhancing search result: {e}")
                # Add original result without enhancement
                enhanced_results.append(result)
        
        return enhanced_results

# Global instance
ai_summary_service = AISummaryService() 