from docx import Document
import os

def create_mock_docx(filepath):
    doc = Document()
    doc.add_heading('RED HERRING PROSPECTUS', 0)
    
    p = doc.add_paragraph('Dated December 10, 2025\n')
    p.add_run('Please read section 32 of the Companies Act, 2013').bold = True
    
    doc.add_heading('KSH INTERNATIONAL LIMITED', 1)
    doc.add_paragraph('CORPORATE IDENTITY NUMBER: U28129PN1979PLC141032')
    
    # Table 1: Contacts
    table = doc.add_table(rows=2, cols=3)
    hdr_cells = table.rows[0].cells
    hdr_cells[0].text = 'REGISTERED OFFICE'
    hdr_cells[1].text = 'CONTACT PERSON'
    hdr_cells[2].text = 'E-MAIL AND TELEPHONE'
    
    row_cells = table.rows[1].cells
    row_cells[0].text = '11/3, 11/4 and 11/5 Village Birdewadi Chakan Taluka - Khed Pune – 410 501 Maharashtra, India'
    row_cells[1].text = 'Sarthak Malvadkar Company Secretary and Compliance Officer'
    row_cells[2].text = 'Email: cs.connect@kshinternational.com Telephone: +91 20 4505 3237'
    
    doc.add_paragraph('\nOUR PROMOTERS: KUSHAL SUBBAYYA HEGDE, PUSHPA KUSHAL HEGDE, RAJESH KUSHAL HEGDE, ROHIT KUSHAL HEGDE, RAKHI GIRIJA SHETTY')
    
    # Financial details
    doc.add_heading('DETAILS OF THE OFFER TO PUBLIC', 2)
    doc.add_paragraph('Fresh Issue and Offer for Sale: Up to [●] Equity Shares of face value of ₹5 each aggregating up to ₹4,200.00 million. The face value of the Equity Shares is ₹5 each.')
    
    # Some Indian PII specifics
    doc.add_paragraph('Other contacts:')
    doc.add_paragraph('Rashi Patil: John Doe, rashhi.patil@gmail.com, john.doe@example.com')
    doc.add_paragraph('Rohan Dey: rohan.dey@gmail.com, peter.parker@example.com, +91 9876543210, +91 1234567645')
    
    # Tricky Non-PII
    doc.add_paragraph('Offer Price: ₹7,100 million. IPO Date: December 16, 2025.')
    doc.add_paragraph('The Red Herring Prospectus has been filed with the Book Running Lead Managers.')
    doc.add_paragraph('Date of Birth: December 10, 1998.')
    
    doc.save(filepath)

if __name__ == '__main__':
    filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Red_Herring_Prospectus.docx')
    create_mock_docx(filepath)
    print(f'Created {filepath}')
