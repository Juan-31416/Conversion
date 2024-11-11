import os
import PyPDF2
from ebooklib import epub
import pathlib
import uuid
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def pdf_to_text(pdf_path):
    """
    Converts a PDF file to text.
    """
    text = ""
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
                    text += page_text + '\n'  # Adds the page text to the total content
                else:
                    logging.warning(f"Page {i + 1} of '{pdf_path}' could not be extracted.")
    except FileNotFoundError:
        logging.error(f"Error: The file '{pdf_path}' was not found.")
    except PyPDF2.errors.PdfReadError:
        logging.error(f"Error: The file '{pdf_path}' could not be read as a PDF.")
    except Exception as e:
        # Captures any other error that occurs while reading the file
        logging.error(f"Error reading the PDF file: {e}")
    return text

def create_epub(text, epub_path, title="Untitled", author="Unknown"):
    """
    Creates an EPUB file from the given text.
    """
    try:
        book = epub.EpubBook()  # Creates a new instance of the EPUB book
        
        # Metadata configuration
        unique_id = str(uuid.uuid4())  # Generate a unique identifier for the book
        book.set_identifier(unique_id)  # Unique identifier for the book
        book.set_title(title)  # Title of the book
        book.set_language('en')  # Language of the book
        book.add_author(author)  # Author of the book

        # Split text into chapters if the text is long
        max_chapter_length = 5000  # Define maximum length of each chapter
        chapters = [text[i:i + max_chapter_length] for i in range(0, len(text), max_chapter_length)]

        # Create and add chapters to the book
        for idx, chapter_text in enumerate(chapters):
            chapter_title = f'Chapter {idx + 1}'
            chapter_file_name = f'chap_{idx + 1:02d}.xhtml'
            chapter = epub.EpubHtml(title=chapter_title, file_name=chapter_file_name, lang='en')
            chapter.content = f'<h1>{chapter_title}</h1><p>{chapter_text}</p>'
            book.add_item(chapter)  # Add the chapter to the book

        # Add chapters to table of contents and to the book spine
        book.toc = [epub.Link(f'chap_{idx + 1:02d}.xhtml', f'Chapter {idx + 1}', f'chap_{idx + 1:02d}') for idx in range(len(chapters))]
        book.add_item(epub.EpubNcx())  # Add NCX index for navigation
        book.add_item(epub.EpubNav())  # Add navigation index
        book.spine = ['nav'] + [f'chap_{idx + 1:02d}' for idx in range(len(chapters))]  # Define the structure of the book (spine)

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
    
    pdf_path = pathlib.Path(r"D:\009 Github\Conversion\PDF_EPUB\GeorgeOrwell_AnimalFarm.pdf")  # Change to the path of your PDF file
    epub_path = pathlib.Path(r"D:\009 Github\Conversion\PDF_EPUB\GeorgeOrwell_AnimalFarm.epub")  # Change to the desired output path
    
    title = "AnimalFarm"  # Title of the EPUB book
    author = "GeorgeOrwell"  # Author of the EPUB book
    
    # Check if the PDF file exists before proceeding
    if pdf_path.exists():
        pdf_to_epub(pdf_path, epub_path, title, author)  # Convert the PDF to EPUB
    else:
        logging.error(f"The PDF file does not exist: {pdf_path}")  # Message if the PDF file is not found

