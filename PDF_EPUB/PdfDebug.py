'''
import pdfplumber
import re

chapter_pattern = re.compile(r'CHAPTER\s+\d+', re.IGNORECASE)

chapters = []
full_text = []  # Lista para almacenar todo el texto

with pdfplumber.open(r"D:\009 Github\Conversion\PDF_EPUB\Sample.pdf") as pdf:
    for page_num, page in enumerate(pdf.pages, start=1):
        text = page.extract_text()
        if not text:
            continue
            
        full_text.append(text)  # Guardamos el texto de cada página

        # Buscar capítulos y segmentar
        matches = chapter_pattern.findall(text)
        if matches:
            # Si encontramos un capítulo, almacenamos la página y el texto correspondiente
            chapters.append((page_num, matches, text))

# Escribir el texto completo en un archivo
output_path = r"D:\009 Github\Conversion\PDF_EPUB\Sample_extracted.txt"
with open(output_path, 'w', encoding='utf-8') as f:
    f.write('\n'.join(full_text))

print(f"Texto extraído guardado en: {output_path}")

# Mostrar capítulos encontrados
for chapter in chapters:
    print(f"Capítulo encontrado en la página {chapter[0]}: {chapter[1]}")
    # Puedes procesar el contenido como desees
'''

import re
import pdfplumber

file_path = r"D:\009 Github\Conversion\PDF_EPUB\Sample.pdf"

with pdfplumber.open(file_path) as pdf:
    extracted_text = ""
    for page in pdf.pages:
        text = page.extract_text()
        if text:
            extracted_text += text

# 1. Añadir un espacio faltante antes de "C" si es parte de un encabezado mal segmentado
# Buscar casos en los que "Orwell" (o cualquier texto sin espacio) sea seguido directamente por "C"
clean_text = re.sub(r'([a-zA-Z])C\s*(\d+)\s*HAPTER', r'\1 C \2 HAPTER', extracted_text)

# 2. Corregir patrones tipo "C 1 HAPTER" a "CHAPTER 1"
clean_text = re.sub(r'C\s*(\d+)\s*HAPTER', r'CHAPTER \1', clean_text, flags=re.IGNORECASE)

# 3. Corregir el encabezado de capítulos espaciado
clean_text = re.sub(r'C\s*H\s*A\s*P\s*T\s*E\s*R\s+(\d+)', r'CHAPTER \1', clean_text, flags=re.IGNORECASE)

# Limpiar "T C ABLE OF ONTENTS" por "TABLE OF CONTENTS"
clean_text = re.sub(r'\bT\s*C\s*ABLE\s*OF\s*ONTENTS\b', 'TABLE OF CONTENTS', clean_text)

# Eliminar espacios y saltos de línea adicionales que no sean necesarios
clean_text = re.sub(r'\s{2,}', ' ', clean_text)

# Guardar el texto limpio en un archivo
output_path = r"D:\009 Github\Conversion\PDF_EPUB\Sample_extracted_v2.txt"
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(clean_text)

print(f"Texto extraído guardado en: {output_path}")


'''
import fitz  # PyMuPDF

file_path = r"D:\009 Github\Conversion\PDF_EPUB\Sample.pdf"
doc = fitz.open(file_path)
extracted_text = ""

for page_num in range(len(doc)):
    page = doc.load_page(page_num)
    text = page.get_text()
    extracted_text += text

#print(extracted_text)
# Escribir el texto completo en un archivo
output_path = r"D:\009 Github\Conversion\PDF_EPUB\Sample_extracted_v3.txt"
with open(output_path, 'w', encoding='utf-8') as f:
    f.write('\n'.join(extracted_text))

print(f"Texto extraído guardado en: {output_path}")
'''