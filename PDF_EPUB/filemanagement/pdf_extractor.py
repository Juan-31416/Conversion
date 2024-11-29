import pdfplumber
import pickle
import re
import logging

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
    logging.info(f"Loaded header and footer patterns for '{pdf_path}'.")
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
                    logging.info(f"Page {i + 1} of '{pdf_path}' extracted.")
                else:
                    logging.warning(f"Page {i + 1} of '{pdf_path}' could not be extracted.")
    
            # Add text cleaning steps
            # 1. Fix missing space before "C" in headers
            text = re.sub(r'([a-zA-Z])C\s*(\d+)\s*HAPTER', r'\1 C \2 HAPTER', text)
            
            # 2. Fix "C 1 HAPTER" patterns to "CHAPTER 1"
            text = re.sub(r'C\s*(\d+)\s*HAPTER', r'CHAPTER \1', text, flags=re.IGNORECASE)
            
            # 3. Fix spaced chapter headers
            text = re.sub(r'C\s*H\s*A\s*P\s*T\s*E\s*R\s+(\d+)', r'CHAPTER \1', text, flags=re.IGNORECASE)
            
            # 4. Fix table of contents header
            text = re.sub(r'\bT\s*C\s*ABLE\s*OF\s*ONTENTS\b', 'TABLE OF CONTENTS', text)
            
            # 5. Clean up extra whitespace
            text = re.sub(r'\s{2,}', ' ', text)
            
            # Save the cleaned text to a file
            output_txt_path = pdf_path.with_suffix('.txt')
            try:
                with open(output_txt_path, 'w', encoding='utf-8') as f:
                    f.write(text)
                logging.info(f"Extracted text saved to: {output_txt_path}")
            except Exception as e:
                logging.error(f"Error saving text file: {e}")
            
    except Exception as e:
        logging.error(f"Error reading the PDF file: {e}")
    
    # Cache the extracted text
    if text:
        cache_text(pdf_path, text)
    return text
