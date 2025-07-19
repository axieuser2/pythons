import os
import re
import json
from dotenv import load_dotenv
from typing import List, Dict, Any
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

class ComprehensiveChunkProcessor:
    def __init__(self):
        self.txt_folder = "Txt File"
        self.chunks = []
        
    def get_all_txt_files(self) -> List[str]:
        """Get all .txt files from the Txt File folder"""
        txt_files = []
        if os.path.exists(self.txt_folder):
            for file in os.listdir(self.txt_folder):
                if file.endswith('.txt'):
                    txt_files.append(os.path.join(self.txt_folder, file))
        return txt_files
    
    def clean_text(self, text: str) -> str:
        """Clean text while preserving important information"""
        # Remove excessive whitespace but keep structure
        text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
        text = re.sub(r'[ \t]+', ' ', text)
        return text.strip()
    
    def extract_structured_info(self, text: str, filename: str) -> List[Dict[str, Any]]:
        """Extract ALL information with multiple chunking strategies"""
        chunks = []
        source = self.get_source_name(filename)
        
        # Strategy 1: Extract title/header information
        title_match = re.search(r'^(\d+\.\s*[^\n]+)', text, re.MULTILINE)
        main_title = title_match.group(1) if title_match else f"Information from {filename}"
        
        # Strategy 2: Split by logical sections (headers, bullets, paragraphs)
        sections = self.split_into_sections(text)
        
        for section in sections:
            if len(section.strip()) < 10:  # Skip very short sections
                continue
                
            # Create multiple chunk types for comprehensive coverage
            chunks.extend(self.create_multiple_chunk_types(section, source, main_title))
        
        # Strategy 3: Create overview chunks for entire file
        chunks.append({
            "content": self.clean_text(text),
            "source": source,
            "title": main_title,
            "chunk_type": "full_document",
            "metadata": {
                "filename": filename,
                "word_count": len(text.split()),
                "char_count": len(text)
            }
        })
        
        return chunks
    
    def split_into_sections(self, text: str) -> List[str]:
        """Split text into logical sections using multiple delimiters"""
        sections = []
        
        # Split by headers (numbered sections)
        header_pattern = r'(\d+\.\s*[^\n]+)'
        parts = re.split(header_pattern, text)
        
        current_section = ""
        for i, part in enumerate(parts):
            if re.match(r'\d+\.\s*', part):  # This is a header
                if current_section.strip():
                    sections.append(current_section.strip())
                current_section = part
            else:
                current_section += part
        
        if current_section.strip():
            sections.append(current_section.strip())
        
        # Also split by bullet points and paragraphs
        for section in sections[:]:  # Copy list to avoid modification during iteration
            bullet_sections = self.split_by_bullets(section)
            if len(bullet_sections) > 1:
                sections.extend(bullet_sections)
        
        return list(set(sections))  # Remove duplicates
    
    def split_by_bullets(self, text: str) -> List[str]:
        """Split text by bullet points and list items"""
        bullet_patterns = [
            r'[•\-\*]\s+',  # Bullet points
            r'✅\s+',       # Checkmarks
            r'🌐\s+',       # Emojis as bullets
            r'📱\s+',
            r'📅\s+',
            r'🛒\s+',
            r'✔\s+',
        ]
        
        sections = []
        for pattern in bullet_patterns:
            parts = re.split(pattern, text)
            if len(parts) > 1:
                for part in parts[1:]:  # Skip first empty part
                    if len(part.strip()) > 20:
                        sections.append(part.strip())
        
        return sections
    
    def create_multiple_chunk_types(self, section: str, source: str, main_title: str) -> List[Dict[str, Any]]:
        """Create multiple types of chunks for comprehensive coverage"""
        chunks = []
        
        # Type 1: Original section
        chunks.append({
            "content": section,
            "source": source,
            "title": main_title,
            "chunk_type": "section",
            "metadata": {"length": len(section)}
        })
        
        # Type 2: Extract key facts and features
        facts = self.extract_key_facts(section)
        for fact in facts:
            chunks.append({
                "content": fact,
                "source": source,
                "title": f"{main_title} - Key Fact",
                "chunk_type": "key_fact",
                "metadata": {"extracted_from": "automated_extraction"}
            })
        
        # Type 3: Extract pricing and numerical information
        pricing_info = self.extract_pricing_info(section)
        for price in pricing_info:
            chunks.append({
                "content": price,
                "source": source,
                "title": f"{main_title} - Pricing",
                "chunk_type": "pricing",
                "metadata": {"type": "pricing_information"}
            })
        
        # Type 4: Extract contact and company information
        contact_info = self.extract_contact_info(section)
        for contact in contact_info:
            chunks.append({
                "content": contact,
                "source": source,
                "title": f"{main_title} - Contact",
                "chunk_type": "contact",
                "metadata": {"type": "contact_information"}
            })
        
        return chunks
    
    def extract_key_facts(self, text: str) -> List[str]:
        """Extract key facts and features from text"""
        facts = []
        
        # Extract emoji-prefixed items
        emoji_pattern = r'[🌐📱📅🛒✅✔🎯🌍💡🛠📊⚙️💬📍❓]\s*([^\n]+)'
        emoji_matches = re.findall(emoji_pattern, text)
        facts.extend(emoji_matches)
        
        # Extract bullet points
        bullet_pattern = r'[-•*]\s*([^\n]+)'
        bullet_matches = re.findall(bullet_pattern, text)
        facts.extend(bullet_matches)
        
        # Extract quoted text
        quote_pattern = r'"([^"]+)"'
        quote_matches = re.findall(quote_pattern, text)
        facts.extend(quote_matches)
        
        return [fact.strip() for fact in facts if len(fact.strip()) > 10]
    
    def extract_pricing_info(self, text: str) -> List[str]:
        """Extract pricing and cost information"""
        pricing = []
        
        # Extract price patterns
        price_patterns = [
            r'(\d+\s*\d*\s*kr[^\n]*)',
            r'(Startavgift[^\n]*)',
            r'(Månadsavgift[^\n]*)',
            r'(\d+\s*995[^\n]*)',
        ]
        
        for pattern in price_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            pricing.extend(matches)
        
        return [price.strip() for price in pricing if len(price.strip()) > 5]
    
    def extract_contact_info(self, text: str) -> List[str]:
        """Extract contact information"""
        contact = []
        
        # Extract email addresses
        email_pattern = r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})'
        emails = re.findall(email_pattern, text)
        contact.extend([f"Email: {email}" for email in emails])
        
        # Extract phone numbers
        phone_pattern = r'(\+\d{2}\s*\d{3}\s*\d{3}\s*\d{3})'
        phones = re.findall(phone_pattern, text)
        contact.extend([f"Phone: {phone}" for phone in phones])
        
        # Extract websites
        website_pattern = r'(www\.[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})'
        websites = re.findall(website_pattern, text)
        contact.extend([f"Website: {website}" for website in websites])
        
        return contact
    
    def get_source_name(self, filename: str) -> str:
        """Extract clean source name from filename"""
        basename = os.path.basename(filename)
        # Remove file extension and clean up
        source = re.sub(r'\.txt$', '', basename)
        source = re.sub(r'^\d+_', '', source)  # Remove number prefix
        return source.lower().replace(' ', '_')
    
    def get_embedding(self, text: str) -> List[float]:
        """Generate embedding for text"""
        try:
            response = openai_client.embeddings.create(
                input=text,
                model="text-embedding-3-small"
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"Error generating embedding: {e}")
            return None
    
    def process_all_files(self) -> List[Dict[str, Any]]:
        """Process all txt files and create comprehensive chunks"""
        all_chunks = []
        txt_files = self.get_all_txt_files()
        
        print(f"Found {len(txt_files)} txt files to process")
        
        for file_path in txt_files:
            print(f"Processing: {file_path}")
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                file_chunks = self.extract_structured_info(content, file_path)
                all_chunks.extend(file_chunks)
                
                print(f"  Created {len(file_chunks)} chunks from {file_path}")
                
            except Exception as e:
                print(f"Error processing {file_path}: {e}")
        
        print(f"Total chunks created: {len(all_chunks)}")
        return all_chunks
    
    def upload_to_supabase(self, chunks: List[Dict[str, Any]]) -> None:
        """Upload all chunks to Supabase with embeddings"""
        print("Starting upload to Supabase...")
        
        # Clear existing data (optional - remove if you want to keep existing data)
        try:
            supabase.table("documents").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
            print("Cleared existing documents")
        except Exception as e:
            print(f"Note: Could not clear existing data: {e}")
        
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
        
        print(f"\nUpload complete!")
        print(f"Successful uploads: {successful_uploads}")
        print(f"Failed uploads: {failed_uploads}")
        print(f"Total processed: {len(chunks)}")

def main():
    processor = ComprehensiveChunkProcessor()
    
    # Process all files
    chunks = processor.process_all_files()
    
    if not chunks:
        print("No chunks were created. Please check your txt files.")
        return
    
    # Save chunks to JSON for review
    with open("comprehensive_chunks.json", "w", encoding="utf-8") as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)
    print(f"Saved {len(chunks)} chunks to comprehensive_chunks.json")
    
    # Upload to Supabase
    processor.upload_to_supabase(chunks)
    
    print("\nProcess completed! All information from txt files has been uploaded to Supabase.")

if __name__ == "__main__":
    main()