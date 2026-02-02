import os                   # For file and directory handling
from PIL import Image       # For image processing (part of Pillow library)
from fpdf import FPDF       # For creating the PDF

# Define the path to the folder containing the JPG files
folder_path = r"c:\Users\Usuario\Documents"

# Get a sorted list of all JPG files in the folder
archives = sorted([archive for archive in os.listdir(folder_path) if archive.lower().endswith('.jpg')])

# Initialize the PDF object
pdf = FPDF()

# Loop through each file in the sorted list
for archive in archives:
    img_path = os.path.join(folder_path, archive)  # Get the full path of the image
    
    try:
        # Open the image and validate that it is a JPEG file
        image = Image.open(img_path)
        
        # Check if the file is actually JPEG
        if image.format != 'JPEG':
            print(f"The file {archive} is not a valid JPEG. It will be skipped.")
            continue
        
        # Convert the image to RGB mode if it's not already in that mode
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Add a page to the PDF and set the image size
        pdf.add_page()
        pdf.image(img_path, x=0, y=0, w=pdf.w, h=pdf.h)
    
    except Exception as e:
        # Error handling in case the file is not a valid JPEG or is corrupted
        print(f"Error processing the file {archive}: {e}")
        continue

# Save the final PDF with the it's name in the current working directory
pdf.output("PDF_File.pdf")

print("PDF correctly created.")
