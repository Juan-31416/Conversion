import os
import PyPDF2
from ebooklib import epub
import pathlib
import uuid
import logging
import re
import pickle

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def cache_text(pdf_path, text=None):
    """
    Caches the extracted text from a PDF to avoid reprocessing.
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
    Converts a PDF file to text, excluding headers and footers.
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
    ]
    header_footer_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in default_patterns]
    try:
        # Opens the PDF file in binary read mode
        with open(pdf_path, 'rb') as pdf_file:
            reader = PyPDF2.PdfReader(pdf_file)  # Creates a PDF reader with PyPDF2
            num_pages = len(reader.pages)  # Gets the number of pages in the PDF
            # Iterates over each page to extract the text
            for i in range(num_pages):
                page = reader.pages[i]
                page_text = page.extract_text()
                if page_text:  # Check if the extracted text is not None
                    # Filter out headers and footers using configurable patterns
                    lines = page_text.splitlines()
                    filtered_lines = [line for line in lines if not any(pattern.match(line) for pattern in header_footer_patterns)]
                    text += '\n'.join(filtered_lines) + '\n'
                else:
                    logging.warning(f"Page {i + 1} of '{pdf_path}' could not be extracted.")
    except FileNotFoundError:
        logging.error(f"Error: The file '{pdf_path}' was not found.")
    except PyPDF2.errors.PdfReadError:
        logging.error(f"Error: The file '{pdf_path}' could not be read as a PDF.")
    except Exception as e:
        # Captures any other error that occurs while reading the file
        logging.error(f"Error reading the PDF file: {e}")
    
    # Cache the extracted text
    if text:
        cache_text(pdf_path, text)
    return text

def split_into_chapters(text):
    """
    Splits the text into chapters based on common chapter headings, excluding the table of contents.
    """
    chapter_pattern = re.compile(r'\bChapter\s+\d+\b', re.IGNORECASE)
    toc_pattern = re.compile(r'\bTable of Contents\b', re.IGNORECASE)
    chapters = []
    current_chapter = []
    in_toc_section = False

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
    return chapters

def create_epub(text, epub_path, title="Untitled", author="Unknown"):
    """
    Creates an EPUB file from the given text, organizing it into chapters.
    """
    try:
        book = epub.EpubBook()  # Creates a new instance of the EPUB book
        
        # Metadata configuration
        unique_id = str(uuid.uuid4())  # Generate a unique identifier for the book
        book.set_identifier(unique_id)  # Unique identifier for the book
        book.set_title(title)  # Title of the book
        book.set_language('en')  # Language of the book
        book.add_author(author)  # Author of the book

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
    except PermissionError:
        logging.error(f"Error: Permission denied when trying to write to '{epub_path}'.")
    except Exception as e:
        # Captures any other error that occurs while creating the EPUB
        logging.error(f"Error creating the EPUB file: {e}")

def pdf_to_epub(pdf_path, epub_path, title="Untitled", author="Unknown"):
    """
    Converts a PDF file to EPUB.
    """
    try:
        text = pdf_to_text(pdf_path)  # Extract text from the PDF file
        if text:
            create_epub(text, epub_path, title, author)  # Create the EPUB file with the extracted text
            logging.info(f"EPUB successfully generated: {epub_path}")  # Success message
        else:
            logging.warning("Could not extract text from the PDF.")  # Warning message if text could not be extracted
    except Exception as e:
        # Captures any other error that occurs during the conversion process
        logging.error(f"Error during PDF to EPUB conversion: {e}")

if __name__ == "__main__":
    pdf_path = pathlib.Path(r"D:\009 Github\Conversion\PDF_EPUB\sample.pdf")  # Change to the path of your PDF file
    epub_path = pathlib.Path(r"D:\009 Github\Conversion\PDF_EPUB\output.epub")  # Change to the desired output path
    title = "My EPUB Book"  # Title of the EPUB book
    author = "Unknown Author"  # Author of the EPUB book
    
    # Check if the PDF file exists before proceeding
    if pdf_path.exists():
        pdf_to_epub(pdf_path, epub_path, title, author)  # Convert the PDF to EPUB
    else:
        logging.error(f"The PDF file does not exist: {pdf_path}")  # Message if the PDF file is not found
