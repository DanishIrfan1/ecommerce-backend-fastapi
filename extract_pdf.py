#!/usr/bin/env python3
import PyPDF2
import sys

def extract_pdf_text(pdf_path):
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ''
            print(f"Found {len(reader.pages)} pages")
            
            for i, page in enumerate(reader.pages):
                page_text = page.extract_text()
                text += f"\n--- Page {i+1} ---\n"
                text += page_text + '\n'
            
            return text
    except Exception as e:
        return f"Error extracting PDF: {e}"

if __name__ == "__main__":
    pdf_text = extract_pdf_text('[Forsit] Task - Back-end Developer.pdf')
    print(pdf_text)
