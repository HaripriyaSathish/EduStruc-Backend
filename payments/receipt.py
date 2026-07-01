from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor, white, black
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import io
from datetime import datetime

PRIMARY = HexColor('#004AC6')
SUCCESS = HexColor('#009668')
DARK = HexColor('#0B1C30')
GRAY = HexColor('#737686')
LIGHT_BLUE = HexColor('#EFF4FF')
WHITE = HexColor('#FFFFFF')
BORDER = HexColor('#C6C6CD')

def generate_receipt_pdf(payment, parent, fee_items):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=20*mm,
        leftMargin=20*mm,
        topMargin=20*mm,
        bottomMargin=20*mm,
    )

    styles = getSampleStyleSheet()
    elements = []

    # ─── HEADER BACKGROUND ───
    header_data = [[
        Paragraph(
            '<font color="white" size="22"><b>EduParent</b></font><br/>'
            '<font color="#DCE9FF" size="10">Student Management System</font>',
            ParagraphStyle('header', alignment=TA_LEFT, leading=28)
        ),
        Paragraph(
            '<font color="white" size="14"><b>Payment Receipt</b></font><br/>'
            f'<font color="#DCE9FF" size="9">#{payment.order_id[-8:].upper()}</font>',
            ParagraphStyle('header_right', alignment=TA_RIGHT, leading=22)
        ),
    ]]
    header_table = Table(header_data, colWidths=[95*mm, 75*mm])
    header_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), PRIMARY),
        ('PADDING', (0, 0), (-1, -1), 16),
        ('ROWBACKGROUNDS', (0, 0), (-1, -1), [PRIMARY]),
        ('ROUNDEDCORNERS', [8]),
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 8*mm))

    # ─── SUCCESS BADGE ───
    success_data = [[
        Paragraph(
            '✓  PAYMENT SUCCESSFUL',
            ParagraphStyle('success', alignment=TA_CENTER,
                         textColor=SUCCESS, fontSize=14,
                         fontName='Helvetica-Bold')
        )
    ]]
    success_table = Table(success_data, colWidths=[170*mm])
    success_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), HexColor('#E5FFE5')),
        ('PADDING', (0, 0), (-1, -1), 10),
        ('ROUNDEDCORNERS', [6]),
        ('BOX', (0, 0), (-1, -1), 1, SUCCESS),
    ]))
    elements.append(success_table)
    elements.append(Spacer(1, 6*mm))

    # ─── TRANSACTION DETAILS ───
    elements.append(Paragraph(
        'TRANSACTION DETAILS',
        ParagraphStyle('section_title', fontSize=10, fontName='Helvetica-Bold',
                      textColor=GRAY, spaceAfter=4)
    ))
    elements.append(HRFlowable(width='100%', thickness=1, color=BORDER))
    elements.append(Spacer(1, 4*mm))

    transaction_data = [
        ['Transaction ID', f'#{payment.order_id[-8:].upper()}'],
        ['Order ID', payment.order_id],
        ['Date & Time', payment.created_at.strftime('%B %d, %Y at %I:%M %p')],
        ['Payment Status', 'PAID ✓'],
        ['Paid To', 'EduStruc School'],
        ['Parent Name', parent.full_name],
        ['Email', parent.email],
    ]

    detail_table = Table(transaction_data, colWidths=[60*mm, 110*mm])
    detail_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TEXTCOLOR', (0, 0), (0, -1), GRAY),
        ('TEXTCOLOR', (1, 0), (1, -1), DARK),
        ('TEXTCOLOR', (1, 3), (1, 3), SUCCESS),
        ('PADDING', (0, 0), (-1, -1), 8),
        ('ROWBACKGROUNDS', (0, 0), (-1, -1), [WHITE, LIGHT_BLUE]),
        ('LINEBELOW', (0, 0), (-1, -2), 0.5, BORDER),
    ]))
    elements.append(detail_table)
    elements.append(Spacer(1, 6*mm))

    # ─── FEE BREAKDOWN ───
    elements.append(Paragraph(
        'FEE BREAKDOWN',
        ParagraphStyle('section_title', fontSize=10, fontName='Helvetica-Bold',
                      textColor=GRAY, spaceAfter=4)
    ))
    elements.append(HRFlowable(width='100%', thickness=1, color=BORDER))
    elements.append(Spacer(1, 4*mm))

    fee_header = [['#', 'Description', 'Amount']]
    fee_rows = []
    total = 0
    for i, fee in enumerate(fee_items, 1):
        amount = float(fee.amount)
        total += amount
        fee_rows.append([
            str(i),
            Paragraph(f'<b>{fee.title}</b><br/><font size="8" color="#737686">{fee.description or ""}</font>',
                     ParagraphStyle('fee_desc', leading=14)),
            f'₹{amount:,.2f}',
        ])

    fee_data = fee_header + fee_rows
    fee_table = Table(fee_data, colWidths=[10*mm, 125*mm, 35*mm])
    fee_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), PRIMARY),
        ('TEXTCOLOR', (0, 0), (-1, 0), WHITE),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
        ('ALIGN', (0, 0), (0, -1), 'CENTER'),
        ('PADDING', (0, 0), (-1, -1), 8),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [WHITE, LIGHT_BLUE]),
        ('LINEBELOW', (0, 0), (-1, -2), 0.5, BORDER),
        ('BOX', (0, 0), (-1, -1), 1, BORDER),
    ]))
    elements.append(fee_table)
    elements.append(Spacer(1, 4*mm))

    # ─── TOTAL ───
    total_data = [[
        Paragraph('<b>TOTAL AMOUNT PAID</b>',
                 ParagraphStyle('total_label', textColor=WHITE, fontSize=12)),
        Paragraph(f'<b>₹{total:,.2f}</b>',
                 ParagraphStyle('total_amount', textColor=WHITE, fontSize=14, alignment=TA_RIGHT)),
    ]]
    total_table = Table(total_data, colWidths=[120*mm, 50*mm])
    total_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), PRIMARY),
        ('PADDING', (0, 0), (-1, -1), 12),
        ('ROUNDEDCORNERS', [6]),
    ]))
    elements.append(total_table)
    elements.append(Spacer(1, 8*mm))

    # ─── SECURITY NOTICE ───
    security_data = [[
        Paragraph(
            '🔒  <b>Secure Payment</b> — This transaction was processed securely '
            'with 256-bit SSL encryption. EduParent never stores your full card details.',
            ParagraphStyle('security', fontSize=9, textColor=GRAY, leading=14)
        )
    ]]
    security_table = Table(security_data, colWidths=[170*mm])
    security_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), LIGHT_BLUE),
        ('PADDING', (0, 0), (-1, -1), 10),
        ('BOX', (0, 0), (-1, -1), 1, BORDER),
        ('ROUNDEDCORNERS', [6]),
    ]))
    elements.append(security_table)
    elements.append(Spacer(1, 8*mm))

    # ─── FOOTER ───
    elements.append(HRFlowable(width='100%', thickness=1, color=BORDER))
    elements.append(Spacer(1, 4*mm))
    elements.append(Paragraph(
        'EduParent — Student Management System | edustruc.com<br/>'
        f'Receipt generated on {datetime.now().strftime("%B %d, %Y at %I:%M %p")}',
        ParagraphStyle('footer', fontSize=8, textColor=GRAY,
                      alignment=TA_CENTER, leading=14)
    ))

    doc.build(elements)
    buffer.seek(0)
    return buffer