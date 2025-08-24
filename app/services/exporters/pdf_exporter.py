# src/exporters/pdf_exporter.py
from fpdf import FPDF

def generate_pdf(kontakte, vorlage_struktur):
    """
    Erstellt eine detaillierte PDF-Ansicht für jeden Kontakt.
    """
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)

    for kontakt in kontakte:
        pdf.add_page()
        
        # --- Kontakt-Header ---
        anrede = kontakt['daten'].get('Anrede', '')
        titel = kontakt['daten'].get('Titel', '')
        vorname = kontakt['daten'].get('Vorname', '')
        nachname = kontakt['daten'].get('Nachname', '')
        firmenname = kontakt['daten'].get('Firmenname', '')

        if vorname or nachname:
            full_name = f"{anrede} {titel} {vorname} {nachname}".strip().replace("  ", " ")
        else:
            full_name = firmenname

        pdf.set_font("Arial", 'B', 16)
        safe_full_name = full_name.encode('latin-1', 'replace').decode('latin-1')
        pdf.cell(0, 10, txt=safe_full_name, ln=True, align='L')
        pdf.line(pdf.get_x(), pdf.get_y(), pdf.get_x() + 190, pdf.get_y())
        pdf.ln(10)

        # --- Attribute in Gruppen ausgeben ---
        for gruppe in vorlage_struktur['gruppen']:
            has_content = any(kontakt['daten'].get(e['name']) for e in gruppe['eigenschaften'])

            if has_content:
                pdf.set_font("Arial", 'B', 12)
                safe_group_name = gruppe['name'].encode('latin-1', 'replace').decode('latin-1')
                pdf.cell(0, 10, txt=safe_group_name, ln=True, align='L')
                pdf.ln(2)

                for eigenschaft in gruppe['eigenschaften']:
                    prop_name = eigenschaft['name']
                    prop_value = str(kontakt['daten'].get(prop_name, ''))

                    if prop_value:
                        start_x = pdf.get_x()
                        pdf.set_font("Arial", 'B', 10)
                        safe_prop_name = prop_name.encode('latin-1', 'replace').decode('latin-1')
                        pdf.cell(60, 8, txt=safe_prop_name, align='L')
                        
                        pdf.set_font("Arial", '', 10)
                        safe_prop_value = prop_value.encode('latin-1', 'replace').decode('latin-1')
                        value_width = pdf.w - pdf.l_margin - pdf.r_margin - 60
                        pdf.multi_cell(value_width, 8, txt=safe_prop_value, align='L')
                        
                        pdf.set_x(start_x)
                        pdf.ln(5)
                pdf.ln(5)

    return bytes(pdf.output())