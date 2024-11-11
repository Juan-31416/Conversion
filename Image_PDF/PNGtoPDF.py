import os
from PIL import Image
from fpdf import FPDF

# Path to the folder containing PNG files
ruta_carpeta = r"c:\Documents"

# Create a list of files in the folder and sort them alphabetically
archivos = sorted([archivo for archivo in os.listdir(ruta_carpeta) if archivo.lower().endswith('.png')])

# Set up the PDF
pdf = FPDF()

for archivo in archivos:
    img_path = os.path.join(ruta_carpeta, archivo)
    
    try:
        # Open the image and validate that it is a PNG file
        imagen = Image.open(img_path)
        
        # Check if the file is actually PNG
        if imagen.format != 'PNG':
            print(f"The file {archivo} is not a valid PNG. It will be skipped.")
            continue
        
        # Convert the image to RGB mode (necessary because PDFs don’t support RGBA)
        if imagen.mode in ('RGBA', 'P'):  # Convert RGBA or P mode to RGB
            imagen = imagen.convert('RGB')
        
        # Save the converted image as a temporary JPEG file
        temp_path = img_path.replace('.png', '_temp.jpg')
        imagen.save(temp_path, 'JPEG')
        
        # Add a page to the PDF with the correct size to preserve the image's aspect ratio
        # Calculate image aspect ratio
        width, height = imagen.size
        aspect_ratio = width / height
        
        # Set the PDF page dimensions to match the image aspect ratio
        # Assuming we want a maximum page width of 210mm (A4 width) and height proportional
        pdf_width, pdf_height = pdf.w, pdf.w / aspect_ratio
        
        # Ensure that the image height does not exceed the page height (297mm for A4)
        if pdf_height > pdf.h:
            pdf_height = pdf.h
            pdf_width = pdf.h * aspect_ratio
        
        # Add a new page with custom size
        pdf.add_page()
        pdf.image(temp_path, x=0, y=0, w=pdf_width, h=pdf_height)
        
        # Remove the temporary JPEG file
        os.remove(temp_path)
    
    except Exception as e:
        # Error handling in case the file is not a valid PNG or is corrupted
        print(f"Error processing the file {archivo}: {e}")
        continue

# Save the PDF
pdf.output("NewPDF.pdf")

print("PDF created successfully.")
