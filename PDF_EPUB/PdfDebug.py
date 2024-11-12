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
