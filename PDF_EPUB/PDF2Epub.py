import os
import pdfplumber  # Added to use as an alternative for text extraction
from ebooklib import epub
import pathlib
import uuid
import logging
import re
import pickle
import spacy  # Added for NLP-based chapter detection

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def cache_text(pdf_path, text=None):
    """
    Manages PDF text caching to improve performance on subsequent runs.
    
    Args:
        pdf_path: Path to the PDF file
        text: Optional text content to cache. If None, attempts to load cached content
    
    Returns:
        Cached text content if loading, None if saving or no cache exists
    """

    cache_file = pdf_path.with_suffix('.pkl')
    if text is not None:
        # Save the text to the cache file
        with open(cache_file, 'wb') as f:
            pickle.dump(text, f)
    elif cache_file.exists():
        # Load the text from the cache file if it exists
        with open(cache_file, 'rb') as f:
            return pickle.load(f)
    return None

def pdf_to_text(pdf_path):
    """
    Extracts and processes text content from a PDF file.
    - Checks for cached version first
    - Removes headers/footers using regex patterns
    - Handles common PDF reading errors
        
    Args:
        pdf_path: Path to the PDF file
    
    Returns:
        Extracted and cleaned text content
    """

    # Check if cached text is available
    cached_text = cache_text(pdf_path)
    if cached_text:
        logging.info(f"Loaded cached text for '{pdf_path}'.")
        return cached_text
    
    text = ""
    # Allowing configurable patterns for header and footer detection
    default_patterns = [
        r'^(Page \d+|\s*Copyright.*)$',
        r'^\s*Confidential.*$',
        r'^(Animal Farm, by George Orwell.*)$',  # Example pattern for book title headers
        r'^(\s*Last updated.*)$',  # Additional pattern for footer texts like "last updated"
    ]
    header_footer_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in default_patterns]
    try:
        with pdfplumber.open(pdf_path) as pdf:
            # Validate PDF is not empty
            if len(pdf.pages) == 0:
                logging.error(f"PDF file '{pdf_path}' appears to be empty.")
                return None
                
            for i, page in enumerate(pdf.pages):
                page_text = page.extract_text()
                if page_text:
                    lines = page_text.splitlines()
                    filtered_lines = [line for line in lines if not any(pattern.match(line) for pattern in header_footer_patterns)]
                    text += '\n'.join(filtered_lines) + '\n'
                else:
                    logging.warning(f"Page {i + 1} of '{pdf_path}' could not be extracted.")
    except Exception as e:
        logging.error(f"Error reading the PDF file: {e}")
    
    # Cache the extracted text
    if text:
        cache_text(pdf_path, text)
    return text

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

def create_epub(text, epub_path, title="Untitled", author="Unknown"):
    """
    Generates an EPUB file with proper structure and metadata.
    - Creates chapter navigation
    - Adds metadata (title, author, language)
    - Generates unique identifier
    - Handles content formatting
    - Creates table of contents
    
    Args:
        text: Processed text content
        epub_path: Output path for EPUB file
        title: Book title
        author: Book author
    """
    try:
        book = epub.EpubBook()  # Creates a new instance of the EPUB book
        
        # Metadata configuration
        unique_id = str(uuid.uuid4())  # Generate a unique identifier for the book
        book.set_identifier(unique_id)  # Unique identifier for the book
        book.set_title(title)  # Title of the book
        book.set_language('en')  # Language of the book
        book.add_author(author)  # Author of the book

        # Add basic CSS styling
        style = 'BODY {color: black; font-family: Arial, sans-serif;} h1 {text-align: center;}'
        nav_css = epub.EpubItem(uid="style_nav", file_name="style/nav.css", media_type="text/css", content=style)
        book.add_item(nav_css)

        # Split text into chapters based on chapter headings
        chapters = split_into_chapters(text)
        if not chapters:  # If no chapters found, split by length
            logging.info("No chapter headings detected, splitting text by length instead.")
            max_chapter_length = 5000  # Define maximum length of each chapter
            paragraphs = text.split('\n\n')  # Split text into paragraphs
            chapters = []
            current_chapter = []
            current_length = 0

            for paragraph in paragraphs:
                paragraph_length = len(paragraph)
                if current_length + paragraph_length > max_chapter_length:
                    # Start a new chapter if the current length exceeds the max length
                    chapters.append('\n\n'.join(current_chapter))
                    current_chapter = [paragraph]
                    current_length = paragraph_length
                else:
                    current_chapter.append(paragraph)
                    current_length += paragraph_length

            if current_chapter:
                chapters.append('\n\n'.join(current_chapter))

        # Create and add chapters to the book
        epub_chapters = []
        for idx, chapter_text in enumerate(chapters):
            chapter_title = f'Chapter {idx + 1}'
            chapter_file_name = f'chap_{idx + 1:02d}.xhtml'
            chapter = epub.EpubHtml(title=chapter_title, file_name=chapter_file_name, lang='en')
            chapter.content = f'<h1>{chapter_title}</h1><p>' + '<br/>'.join(chapter_text.split('\n')) + '</p>'

            book.add_item(chapter)  # Add the chapter to the book
            epub_chapters.append(chapter)  # Keep track of chapters for TOC and spine

        # Add chapters to table of contents and to the book spine
        book.toc = [epub.Link(ch.file_name, ch.title, f'chap_{idx + 1:02d}') for idx, ch in enumerate(epub_chapters)]
        book.add_item(epub.EpubNcx())  # Add NCX index for navigation
        book.add_item(epub.EpubNav())  # Add navigation index
        book.spine = ['nav'] + epub_chapters  # Define the structure of the book (spine)

        # Create the EPUB file
        epub.write_epub(epub_path, book, {})  # Write the EPUB file to the specified path
        logging.info(f"EPUB successfully generated: {epub_path}")
    except PermissionError:
        logging.error(f"Error: Permission denied when trying to write to '{epub_path}'.")
    except Exception as e:
        # Captures any other error that occurs while creating the EPUB
        logging.error(f"Error creating the EPUB file: {e}")

if __name__ == "__main__":
    pdf_path = pathlib.Path(r"D:\009 Github\Conversion\PDF_EPUB\sample.pdf")  # Change to the path of your PDF file
    epub_path = pathlib.Path(r"D:\009 Github\Conversion\PDF_EPUB\output.epub")  # Change to the desired output path
    title = "My EPUB Book"  # Title of the EPUB book
    author = "Unknown Author"  # Author of the EPUB book
    
    # Check if the PDF file exists before proceeding
    if pdf_path.exists():
        text = pdf_to_text(pdf_path)  # Extract text from the PDF
        if text:
            logging.info(f"Text extraction complete. Length: {len(text)} characters.")
            chapters = split_into_chapters(text)  # Split text into chapters
            logging.info(f"Detected {len(chapters)} chapters.")
            create_epub(text, epub_path, title, author)  # Create the EPUB file with the extracted text
        else:
            logging.error("Text extraction failed.")
    else:
        logging.error(f"The PDF file does not exist: {pdf_path}")  # Message if the PDF file is not found
