import re
import spacy
import logging

def split_into_chapters(text):
    """
    Intelligently splits text content into chapters.
    - Detects chapter headings using regex
    - Uses NLP to identify changes in themes if no headings are found
    - Skips table of contents sections
    - Preserves chapter structure
    - Falls back to length-based splitting if no chapters detected
    
    Args:
        text: Raw text content to split
    
    Returns:
        List of chapter contents
    """
    # Add more chapter patterns for better detection
    chapter_patterns = [
        r'\bChapter\s+\d+\b',
        r'\b\d+\.\s+',  # Matches "1. ", "2. " etc.
        r'\bPart\s+\d+\b',
        r'\bSection\s+\d+\b',
        r'\b[A-Z][a-z]+\s+\d+\b',  # Matches common headings like "Part One"
        r'\bPrologue\b',
        r'\bEpilogue\b'
    ]
    chapter_pattern = re.compile('|'.join(chapter_patterns), re.IGNORECASE)
    toc_pattern = re.compile(r'\bTable of Contents\b', re.IGNORECASE)
    chapters = []
    current_chapter = []
    in_toc_section = False

    # Load NLP model
    nlp = spacy.load('en_core_web_sm')

    for line in text.splitlines():
        if toc_pattern.match(line):
            # Skip over the Table of Contents section
            in_toc_section = True
            continue

        if in_toc_section:
            # If currently in the TOC section, check for an empty line to exit
            if line.strip() == "":
                in_toc_section = False
            continue

        if chapter_pattern.match(line):
            # Start a new chapter when a chapter heading is found
            if current_chapter:
                chapters.append('\n'.join(current_chapter))
            current_chapter = [line]
        else:
            current_chapter.append(line)
    if current_chapter:
        chapters.append('\n'.join(current_chapter))

    # If no chapters were detected, attempt NLP-based segmentation
    if len(chapters) <= 1:
        logging.info("No clear chapter headings detected, attempting NLP-based segmentation.")
        doc = nlp(text)
        paragraphs = text.split('\n\n')
        chapters = []
        current_chapter = []
        current_length = 0
        max_chapter_length = 5000  # Maximum length of each chapter in characters

        for paragraph in paragraphs:
            paragraph_length = len(paragraph)
            current_length += paragraph_length
            current_chapter.append(paragraph)

            # Split if max length is reached or a large thematic break is detected
            if current_length > max_chapter_length or (paragraph.endswith('.') and len(paragraph.split()) > 50):
                doc_chunk = nlp(' '.join(current_chapter))
                if any(sent.text.strip() for sent in doc_chunk.sents if sent.text.strip().endswith('.')):
                    chapters.append('\n\n'.join(current_chapter))
                    current_chapter = []
                    current_length = 0

        if current_chapter:
            chapters.append('\n\n'.join(current_chapter))

    return chapters

