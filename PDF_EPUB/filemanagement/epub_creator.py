from ebooklib import epub
import uuid
import logging
from text_splitter import split_into_chapters

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
