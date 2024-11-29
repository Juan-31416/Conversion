import pathlib
import logging
from filemanagement.pdf_extractor import pdf_to_text
from filemanagement.text_splitter import split_into_chapters
from filemanagement.epub_creator import create_epub

if __name__ == "__main__":
    pdf_path = pathlib.Path(r"D:\009 Github\Conversion\PDF_EPUB\sample.pdf")
    epub_path = pathlib.Path(r"D:\009 Github\Conversion\PDF_EPUB\output.epub")
    title = "My EPUB Book"
    author = "Unknown Author"
    
    if pdf_path.exists():
        text = pdf_to_text(pdf_path)
        if text:
            logging.info(f"Text extraction complete. Length: {len(text)} characters.")
            chapters = split_into_chapters(text)
            logging.info(f"Detected {len(chapters)} chapters.")
            create_epub(text, epub_path, title=title, author=author)
        else:
            logging.error("Text extraction failed.")
    else:
        logging.error(f"The PDF file does not exist: {pdf_path}")
