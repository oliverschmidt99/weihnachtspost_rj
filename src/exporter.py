# src/exporter.py
import csv
import openpyxl
from fpdf import FPDF
import io

def generate_csv(kontakte, eigenschaften):
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Header schreiben
    headers = [e['name'] for e in eigenschaften]
    writer.writerow(headers)
    
    # Daten schreiben
    for kontakt in kontakte:
        row = [kontakt['daten'].get(h, '') for h in headers]
        writer.writerow(row)
        
    output.seek(0)
    return output.getvalue()

def generate_xlsx(kontakte, eigenschaften):
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    
    headers = [e['name'] for e in eigenschaften]
    sheet.append(headers)
    
    for kontakt in kontakte:
        row = [kontakt['daten'].get(h, '') for h in headers]
        sheet.append(row)
        
    output = io.BytesIO()
    workbook.save(output)
    output.seek(0)
    return output.getvalue()

def generate_pdf(kontakte, eigenschaften, vorlage_name):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    pdf.cell(200, 10, txt=f"Kontakte für Vorlage: {vorlage_name}", ln=True, align='C')
    
    col_width = pdf.w / (len(eigenschaften) + 0.5)
    
    # Header
    pdf.set_font("Arial", 'B', 8)
    for e in eigenschaften:
        pdf.cell(col_width, 10, e['name'], border=1)
    pdf.ln()
    
    # Daten
    pdf.set_font("Arial", '', 8)
    for kontakt in kontakte:
        for e in eigenschaften:
            value = str(kontakt['daten'].get(e['name'], ''))
            pdf.cell(col_width, 10, value, border=1)
        pdf.ln()

    return pdf.output(dest='S').encode('latin-1')