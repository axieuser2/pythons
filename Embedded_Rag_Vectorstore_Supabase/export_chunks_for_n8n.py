import os
import re
import json

# Configuration
FILES = [
    ("Txt File/01_Intro_Vad_Är_Axie_Studio.txt", "intro"),
    ("Txt File/02_Tjänster_Översikt.txt", "tjanster_oversikt"),
    ("Txt File/03_Paket_och_Priser.txt", "paket_och_priser"),
    ("Txt File/04_Teknik_och_Stabilitet.txt", "teknik_och_stabilitet"),
    ("Txt File/05_Support_och_Samarbete.txt", "support_och_samarbete"),
    ("Txt File/06_Mobilappar_och_Ehandel.txt", "mobilappar_och_ehandel"),
    ("Txt File/07_FAQ_Vanliga_Frågor.txt", "faq_vanliga_fragor"),
    ("Txt File/08_Kontakt_och_Företagsinfo.txt", "kontakt_och_foretagsinfo"),
]
OUTPUT_FILE = "chunks_for_n8n.jsonl"
MAX_CONTENT_LENGTH = 1000  # Optional: truncate long chunks for embedding

# Only include these section keywords (case-insensitive)
INCLUDE_SECTIONS = ["service", "tjänst", "pricing", "pris", "identity", "vad är axie", "about", "om oss", "slogan"]

def should_include_section(title):
    t = title.lower()
    return any(key in t for key in INCLUDE_SECTIONS)

def read_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()

def clean_line(line):
    return re.sub(r"\s+", " ", line.strip())

def section_chunk_text(text, source):
    """
    Splits text into sections and further into content chunks.
    Supports headers, bullets, and fallback to paragraph blocks.
    Only includes sections matching INCLUDE_SECTIONS.
    """
    section_pattern = re.compile(
        r"(^[^\n]+[\n=]{2,}$|^[^\n]+[\n\-]{2,}$|^\d+\.\s[^\n]+$)", re.MULTILINE
    )
    matches = list(section_pattern.finditer(text))
    chunks = []

    for i, match in enumerate(matches):
        start = match.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        section_text = text[start:end].strip()
        if not section_text:
            continue

        lines = section_text.splitlines()
        title = clean_line(lines[0])

        # Only include relevant sections
        if not should_include_section(title):
            continue

        # Split section body into bullets or paragraphs
        bullets = []
        for line in lines[1:]:
            line = clean_line(line)
            if not line or re.match(r"^[=\-]{3,}$", line):  # Skip separators
                continue
            if re.match(r"^[-*•]\s+", line):  # Bullet points
                bullets.append(line[2:].strip())
            else:
                bullets.append(line)

        # Fallback: if no real content found
        if not bullets:
            bullets = [section_text]

        # Create chunk for each bullet/paragraph
        for content in bullets:
            content = content.strip()
            if not content:
                continue
            if len(content) > MAX_CONTENT_LENGTH:
                content = content[:MAX_CONTENT_LENGTH] + "…"
            chunks.append({
                "title": title,
                "source": source,
                "content": content
            })

    return chunks

def main():
    all_chunks = []
    for filepath, source in FILES:
        text = read_file(filepath)
        chunks = section_chunk_text(text, source)
        all_chunks.extend(chunks)
    
        # Add pricing chunks (well-categorized for RAG)
        PRICING_BLOCKS = [
            {
                "service": "Webbplats",
                "start_fee": "8 995 kr",
                "monthly_fee": "495 kr",
                "description": "Inkluderar responsiv design, SEO, bokningssystem och mobilapp."
            },
            {
                "service": "Commerce (E-handel)",
                "start_fee": "10 995 kr",
                "monthly_fee": "895 kr",
                "description": "Allt i webbplats + e-handelsfunktioner"
            },
            {
                "service": "Bokningssystem",
                "start_fee": "10 995 kr",
                "monthly_fee": "995 kr",
                "description": "Inkluderar CRM, SMS-notifieringar, analys och kalendersynk"
            },
            {
                "service": "Komplett (Allt-i-ett)",
                "start_fee": "14 995 kr",
                "monthly_fee": "1 495 kr",
                "description": "Webb, app, bokningssystem, marknadsföring, white-label m.m."
            }
        ]
        for p in PRICING_BLOCKS:
            all_chunks.append({
                "title": f"Pricing: {p['service']}",
                "source": "pricing",
                "category": "pricing",
                "service": p["service"],
                "start_fee": p["start_fee"],
                "monthly_fee": p["monthly_fee"],
                "description": p["description"],
                "content": (
                    f"{p['service']} - Startavgift: {p['start_fee']}, Månadsavgift: {p['monthly_fee']}. {p['description']}"
                )
            })
    
        # Navigation and social links as extra chunks have been removed to focus on main content only.
    
        print(f"Total chunks: {len(all_chunks)}")

    # Deduplicate links: ensure "www.axiestudio.se" appears in only one chunk
    seen_links = set()
    LINK = "www.axiestudio.se"
    for chunk in all_chunks:
        if LINK in chunk["content"]:
            if LINK in seen_links:
                # Remove the link from this chunk's content
                chunk["content"] = chunk["content"].replace(LINK, "")
                chunk["content"] = chunk["content"].replace("  ", " ").strip()
            else:
                seen_links.add(LINK)

    # Write as JSONL (one JSON object per line)
    with open("chunks_for_n8n.jsonl", "w", encoding="utf-8") as f:
        for chunk in all_chunks:
            json.dump(
                {
                    "content": chunk["content"],
                    "source": chunk["source"],
                    "title": chunk["title"]
                },
                f,
                ensure_ascii=False
            )
            f.write("\n")
    print("Saved section-based chunks to chunks_for_n8n.jsonl")

if __name__ == "__main__":
    main()