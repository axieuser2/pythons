import os
import re
import json
import csv
import io
from pathlib import Path
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from openai import OpenAI
from supabase import create_client, Client

# Load environment variables
load_dotenv()

# Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

# Validate required environment variables
if not all([OPENAI_API_KEY, SUPABASE_URL, SUPABASE_SERVICE_KEY]):
    raise ValueError("Missing required environment variables. Please check your .env file.")

# Initialize clients
openai_client = OpenAI(api_key=OPENAI_API_KEY)
supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

class UniversalFileProcessor:
    def __init__(self):
        self.supported_extensions = {'.txt', '.pdf', '.doc', '.docx', '.csv'}
        self.chunks = []
        
    def extract_text_from_file(self, file_path: str, file_content: bytes = None) -> str:
        """Extract text from various file formats"""
        file_extension = Path(file_path).suffix.lower()
        
        try:
            if file_extension == '.txt':
                if file_content:
                    return file_content.decode('utf-8', errors='ignore')
                else:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        return f.read()
            
            elif file_extension == '.csv':
                if file_content:
                    content = file_content.decode('utf-8', errors='ignore')
                    csv_reader = csv.reader(io.StringIO(content))
                else:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        csv_reader = csv.reader(f)
                
                rows = list(csv_reader)
                if not rows:
                    return ""
                
                # Convert CSV to readable text format
                text_content = []
                headers = rows[0] if rows else []
                
                text_content.append("CSV Data:")
                text_content.append("Headers: " + ", ".join(headers))
                text_content.append("")
                
                for i, row in enumerate(rows[1:], 1):
                    if len(row) == len(headers):
                        row_text = f"Row {i}:"
                        for header, value in zip(headers, row):
                            if value.strip():
                                row_text += f" {header}: {value};"
                        text_content.append(row_text)
                
                return "\n".join(text_content)
            
            elif file_extension in ['.pdf', '.doc', '.docx']:
                # For PDF and Word documents, we'll extract basic text
                # In a production environment, you'd use libraries like PyPDF2, python-docx, etc.
                # For now, we'll return a placeholder that indicates the file type
                filename = Path(file_path).name
                return f"Document: {filename}\nContent: [This is a {file_extension.upper()} document. In a production environment, this would contain the extracted text content.]"
            
            else:
                return f"Unsupported file type: {file_extension}"
                
        except Exception as e:
            return f"Error reading file {file_path}: {str(e)}"
    
    def create_comprehensive_chunks(self, text: str, source: str, filename: str) -> List[Dict[str, Any]]:
        """Create comprehensive chunks from text content"""
        chunks = []
        
        if not text or len(text.strip()) < 10:
            return chunks
        
        # Clean the text
        text = self.clean_text(text)
        
        # Strategy 1: Full document chunk
        chunks.append({
            "content": text,
            "source": source,
            "title": f"Complete document: {filename}",
            "chunk_type": "full_document",
            "metadata": {
                "filename": filename,
                "word_count": len(text.split()),
                "char_count": len(text)
            }
        })
        
        # Strategy 2: Split by paragraphs
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip() and len(p.strip()) > 50]
        for i, paragraph in enumerate(paragraphs):
            chunks.append({
                "content": paragraph,
                "source": source,
                "title": f"{filename} - Section {i+1}",
                "chunk_type": "paragraph",
                "metadata": {
                    "filename": filename,
                    "section_number": i+1
                }
            })
        
        # Strategy 3: Split by sentences for detailed coverage
        sentences = self.split_into_sentences(text)
        sentence_groups = self.group_sentences(sentences, max_length=300)
        
        for i, group in enumerate(sentence_groups):
            if len(group.strip()) > 30:
                chunks.append({
                    "content": group,
                    "source": source,
                    "title": f"{filename} - Detail {i+1}",
                    "chunk_type": "sentence_group",
                    "metadata": {
                        "filename": filename,
                        "group_number": i+1
                    }
                })
        
        # Strategy 4: Extract key information
        key_info = self.extract_key_information(text)
        for info_type, content in key_info.items():
            if content:
                chunks.append({
                    "content": content,
                    "source": source,
                    "title": f"{filename} - {info_type.title()}",
                    "chunk_type": info_type,
                    "metadata": {
                        "filename": filename,
                        "info_type": info_type
                    }
                })
        
        return chunks
    
    def clean_text(self, text: str) -> str:
        """Clean text while preserving important information"""
        # Remove excessive whitespace but keep structure
        text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
        text = re.sub(r'[ \t]+', ' ', text)
        return text.strip()
    
    def split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences"""
        # Simple sentence splitting
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip() and len(s.strip()) > 10]
    
    def group_sentences(self, sentences: List[str], max_length: int = 300) -> List[str]:
        """Group sentences into chunks of appropriate length"""
        groups = []
        current_group = []
        current_length = 0
        
        for sentence in sentences:
            sentence_length = len(sentence)
            
            if current_length + sentence_length > max_length and current_group:
                groups.append('. '.join(current_group) + '.')
                current_group = [sentence]
                current_length = sentence_length
            else:
                current_group.append(sentence)
                current_length += sentence_length
        
        if current_group:
            groups.append('. '.join(current_group) + '.')
        
        return groups
    
    def extract_key_information(self, text: str) -> Dict[str, str]:
        """Extract different types of key information"""
        info = {}
        
        # Extract email addresses
        emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
        if emails:
            info['contact_emails'] = 'Email addresses found: ' + ', '.join(emails)
        
        # Extract phone numbers
        phones = re.findall(r'[\+]?[1-9]?[0-9]{7,15}', text)
        if phones:
            info['contact_phones'] = 'Phone numbers found: ' + ', '.join(phones)
        
        # Extract URLs
        urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text)
        if urls:
            info['urls'] = 'URLs found: ' + ', '.join(urls)
        
        # Extract prices/costs
        prices = re.findall(r'[\$€£¥₹]\s*\d+(?:[\.,]\d+)*|(\d+(?:[\.,]\d+)*)\s*(?:kr|SEK|USD|EUR|GBP)', text)
        if prices:
            price_strings = [p[0] if p[0] else p[1] for p in prices]
            info['pricing'] = 'Pricing information: ' + ', '.join(price_strings)
        
        # Extract numbered lists
        numbered_items = re.findall(r'\d+\.\s+([^\n]+)', text)
        if numbered_items:
            info['numbered_lists'] = 'Key points: ' + '; '.join(numbered_items[:5])
        
        # Extract bullet points
        bullet_items = re.findall(r'[•\-\*]\s+([^\n]+)', text)
        if bullet_items:
            info['bullet_points'] = 'Important items: ' + '; '.join(bullet_items[:5])
        
        return info
    
    def get_embedding(self, text: str) -> List[float]:
        """Generate embedding for text"""
        try:
            response = openai_client.embeddings.create(
                input=text[:8000],  # Limit text length for embedding
                model="text-embedding-3-small"
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"Error generating embedding: {e}")
            return None
    
    def process_file(self, file_path: str, file_content: bytes = None) -> List[Dict[str, Any]]:
        """Process a single file and return chunks"""
        filename = Path(file_path).name
        source = Path(file_path).stem.lower().replace(' ', '_')
        
        print(f"Processing file: {filename}")
        
        # Extract text content
        text_content = self.extract_text_from_file(file_path, file_content)
        
        if not text_content or len(text_content.strip()) < 10:
            print(f"No content extracted from {filename}")
            return []
        
        # Create comprehensive chunks
        file_chunks = self.create_comprehensive_chunks(text_content, source, filename)
        
        print(f"Created {len(file_chunks)} chunks from {filename}")
        return file_chunks
    
    def upload_to_supabase(self, chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Upload all chunks to Supabase with embeddings"""
        print("Starting upload to Supabase...")
        
        successful_uploads = 0
        failed_uploads = 0
        
        for i, chunk in enumerate(chunks, 1):
            try:
                # Generate embedding
                embedding = self.get_embedding(chunk["content"])
                if embedding is None:
                    print(f"Chunk {i}: Failed to generate embedding")
                    failed_uploads += 1
                    continue
                
                # Prepare data for Supabase
                data = {
                    "content": chunk["content"],
                    "embedding": embedding,
                    "source": chunk["source"],
                    "metadata": {
                        "title": chunk["title"],
                        "chunk_type": chunk["chunk_type"],
                        **chunk.get("metadata", {})
                    }
                }
                
                # Insert into Supabase
                response = supabase.table("documents").insert(data).execute()
                
                if hasattr(response, 'error') and response.error:
                    print(f"Chunk {i}: Upload failed - {response.error}")
                    failed_uploads += 1
                else:
                    successful_uploads += 1
                    if i % 10 == 0:  # Progress update every 10 chunks
                        print(f"Uploaded {i}/{len(chunks)} chunks...")
                
            except Exception as e:
                print(f"Chunk {i}: Exception during upload - {e}")
                failed_uploads += 1
        
        result = {
            "successful_uploads": successful_uploads,
            "failed_uploads": failed_uploads,
            "total_chunks": len(chunks)
        }
        
        print(f"Upload complete! Success: {successful_uploads}, Failed: {failed_uploads}")
        return result

def process_files_from_directory(directory_path: str = "uploaded_files") -> Dict[str, Any]:
    """Process all files from a directory"""
    processor = UniversalFileProcessor()
    all_chunks = []
    files_processed = 0
    
    if not os.path.exists(directory_path):
        return {
            "success": False,
            "message": "Upload directory not found",
            "error": f"Directory {directory_path} does not exist"
        }
    
    # Process all files in the directory
    for filename in os.listdir(directory_path):
        file_path = os.path.join(directory_path, filename)
        
        if os.path.isfile(file_path):
            file_extension = Path(file_path).suffix.lower()
            
            if file_extension in processor.supported_extensions:
                try:
                    file_chunks = processor.process_file(file_path)
                    all_chunks.extend(file_chunks)
                    files_processed += 1
                except Exception as e:
                    print(f"Error processing {filename}: {e}")
    
    if not all_chunks:
        return {
            "success": False,
            "message": "No content could be extracted from the uploaded files",
            "files_processed": files_processed
        }
    
    # Upload to Supabase
    upload_result = processor.upload_to_supabase(all_chunks)
    
    return {
        "success": True,
        "message": f"Successfully processed {files_processed} files and created {len(all_chunks)} chunks",
        "files_processed": files_processed,
        "chunks_created": len(all_chunks),
        "upload_stats": upload_result
    }

def main():
    """Main function for testing"""
    # Test with existing txt files
    txt_folder = "Txt File"
    if os.path.exists(txt_folder):
        result = process_files_from_directory(txt_folder)
        print(json.dumps(result, indent=2))
    else:
        print("Txt File folder not found. Please upload files through the web interface.")

if __name__ == "__main__":
    main()