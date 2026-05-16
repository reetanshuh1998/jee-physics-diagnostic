import PyPDF2
import sys

pdf_path = "/home/reet/jee/jee question/2024_01_27_Shift1.pdf"

try:
    print(f"Opening PDF: {pdf_path}")
    reader = PyPDF2.PdfReader(pdf_path)
    num_pages = len(reader.pages)
    print(f"Number of pages: {num_pages}")
    
    # Read first 3 pages
    for i in range(min(3, num_pages)):
        print(f"\n--- Page {i+1} ---")
        page = reader.pages[i]
        text = page.extract_text()
        print(text)
        
except Exception as e:
    print(f"Error: {e}")
