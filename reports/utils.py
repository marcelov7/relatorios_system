from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from datetime import datetime
from io import BytesIO
import pandas as pd


def generate_pdf_report(report_instance, data=None):
    """Gera um relatório em PDF básico"""
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{report_instance.title}.pdf"'
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []
    
    # Título
    title = Paragraph(report_instance.title, styles['Title'])
    story.append(title)
    story.append(Spacer(1, 12))
    
    # Informações básicas
    info = f"""
    <b>Autor:</b> {report_instance.author.get_full_name()}<br/>
    <b>Categoria:</b> {report_instance.category.name}<br/>
    <b>Período:</b> {report_instance.start_date} - {report_instance.end_date}<br/>
    <b>Gerado em:</b> {datetime.now().strftime('%d/%m/%Y %H:%M')}<br/>
    """
    
    info_para = Paragraph(info, styles['Normal'])
    story.append(info_para)
    story.append(Spacer(1, 12))
    
    # Descrição
    if report_instance.description:
        desc = Paragraph(f"<b>Descrição:</b><br/>{report_instance.description}", styles['Normal'])
        story.append(desc)
        story.append(Spacer(1, 12))
    
    # Dados
    if data:
        data_title = Paragraph("<b>Dados do Relatório:</b>", styles['Heading2'])
        story.append(data_title)
        
        for key, value in data.items():
            item = Paragraph(f"<b>{key}:</b> {value}", styles['Normal'])
            story.append(item)
            story.append(Spacer(1, 6))
    
    doc.build(story)
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    
    return response


def generate_excel_report(report_instance, data=None):
    """Gera um relatório em Excel"""
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename="{report_instance.title}.xlsx"'
    
    # Criar DataFrame com informações básicas
    info_data = {
        'Título': [report_instance.title],
        'Autor': [report_instance.author.get_full_name()],
        'Categoria': [report_instance.category.name],
        'Data Inicial': [report_instance.start_date],
        'Data Final': [report_instance.end_date],
        'Gerado em': [datetime.now().strftime('%d/%m/%Y %H:%M')]
    }
    
    df_info = pd.DataFrame(info_data)
    
    with pd.ExcelWriter(response, engine='openpyxl') as writer:
        df_info.to_excel(writer, sheet_name='Informações', index=False)
        
        if data:
            df_data = pd.DataFrame([data])
            df_data.to_excel(writer, sheet_name='Dados', index=False)
    
    return response 