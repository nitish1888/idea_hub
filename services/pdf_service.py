"""
PDF Processing Service
Extracts text from uploaded PDFs and stores in vector database
"""

import logging
import os
import fitz  # PyMuPDF
from werkzeug.utils import secure_filename
from services.huggingface_service import huggingface_service
from services.vector_service import vector_service

class PDFService:
    """Service for processing PDF uploads and extracting content"""
    
    def __init__(self, upload_folder="uploads/pdfs"):
        self.upload_folder = upload_folder
        self.allowed_extensions = {'pdf'}
        self._ensure_upload_folder()
    
    def _ensure_upload_folder(self):
        """Create upload folder if it doesn't exist"""
        os.makedirs(self.upload_folder, exist_ok=True)
    
    def is_allowed_file(self, filename):
        """Check if file has allowed extension"""
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in self.allowed_extensions
    
    def save_pdf(self, file, idea_id):
        """Save uploaded PDF file"""
        try:
            if not self.is_allowed_file(file.filename):
                raise ValueError("Invalid file type. Only PDF files are allowed.")
            
            # Create secure filename
            filename = secure_filename(file.filename)
            filename = f"idea_{idea_id}_{filename}"
            filepath = os.path.join(self.upload_folder, filename)
            
            # Save file
            file.save(filepath)
            logging.info(f"✅ PDF saved: {filepath}")
            
            return {
                "filename": filename,
                "filepath": filepath,
                "size": os.path.getsize(filepath)
            }
            
        except Exception as e:
            logging.error(f"❌ Error saving PDF: {e}")
            raise
    
    def extract_text_from_pdf(self, filepath):
        """Extract text content from PDF using PyMuPDF"""
        try:
            logging.info(f"📄 Extracting text from: {filepath}")
            
            # Open PDF
            doc = fitz.open(filepath)
            text_content = []
            
            # Extract text from each page
            for page_num in range(doc.page_count):
                page = doc[page_num]
                text = page.get_text()
                
                if text.strip():  # Only add non-empty pages
                    text_content.append({
                        "page": page_num + 1,
                        "text": text.strip()
                    })
            
            doc.close()
            
            # Combine all text
            full_text = "\n\n".join([page["text"] for page in text_content])
            
            logging.info(f"✅ Extracted {len(full_text)} characters from {len(text_content)} pages")
            
            return {
                "full_text": full_text,
                "pages": text_content,
                "total_pages": len(text_content),
                "total_characters": len(full_text)
            }
            
        except Exception as e:
            logging.error(f"❌ Error extracting text from PDF: {e}")
            raise
    
    def process_pdf_for_idea(self, file, idea_data, idea_id):
        """Complete PDF processing pipeline for an idea"""
        try:
            # 1. Save the PDF file
            file_info = self.save_pdf(file, idea_id)
            
            # 2. Extract text content
            extracted_content = self.extract_text_from_pdf(file_info["filepath"])
            
            # 3. Create enhanced idea data with PDF content
            enhanced_idea = {
                **idea_data,
                "id": idea_id,
                "pdf_content": extracted_content["full_text"],
                "pdf_filename": file_info["filename"],
                "pdf_pages": extracted_content["total_pages"]
            }
            
            # 4. Combine original abstract/description with PDF content for vector storage
            combined_text = f"""
            {idea_data.get('title', '')}
            {idea_data.get('description', '')}
            {idea_data.get('abstract', '')}
            
            PDF Content:
            {extracted_content['full_text'][:1000]}  # Limit to 5000 chars for embedding
            """.strip()
            
            # 5. Store in vector database with PDF content
            if huggingface_service.is_available():
                enhanced_idea["combined_content"] = combined_text
                vector_service.add_idea_to_vector_store(enhanced_idea)
                logging.info(f"✅ PDF content added to vector store for idea {idea_id}")
            
            return {
                "file_info": file_info,
                "extracted_content": extracted_content,
                "vector_stored": huggingface_service.is_available()
            }
            
        except Exception as e:
            logging.error(f"❌ Error processing PDF for idea {idea_id}: {e}")
            raise
    
    def search_pdf_content(self, query, top_k=5):
        """Search through PDF content using vector similarity"""
        try:
            # Use existing vector search - it will include PDF content
            results = vector_service.search_similar_ideas(query, top_k=top_k)
            
            # Filter results that have PDF content
            pdf_results = []
            for result in results:
                if result.get('pdf_filename'):
                    pdf_results.append({
                        **result,
                        "content_type": "pdf",
                        "has_pdf": True
                    })
                else:
                    pdf_results.append({
                        **result,
                        "content_type": "text",
                        "has_pdf": False
                    })
            
            return pdf_results
            
        except Exception as e:
            logging.error(f"❌ Error searching PDF content: {e}")
            return []
    
    def get_pdf_summary(self, filepath):
        """Get a summary of PDF content"""
        try:
            extracted = self.extract_text_from_pdf(filepath)
            
            # Create summary
            summary = {
                "total_pages": extracted["total_pages"],
                "total_characters": extracted["total_characters"],
                "word_count": len(extracted["full_text"].split()),
                "preview": extracted["full_text"][:500] + "..." if len(extracted["full_text"]) > 500 else extracted["full_text"]
            }
            
            return summary
            
        except Exception as e:
            logging.error(f"❌ Error creating PDF summary: {e}")
            return None

# Global instance
pdf_service = PDFService() 