from django.http import HttpResponse
# from reportlab.pdfgen import canvas
# from reportlab.lib.pagesizes import A4
# from reportlab.lib import colors
# from reportlab.lib.styles import getSampleStyleSheet
# from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from datetime import datetime
from io import BytesIO
# import pandas as pd


def generate_pdf_report(report_instance, data=None):
    """Gera um relatório em PDF básico - TEMPORARIAMENTE DESABILITADO"""
    response = HttpResponse(content_type='text/plain')
    response['Content-Disposition'] = f'attachment; filename="{report_instance.title}.txt"'
    response.write("Funcionalidade PDF temporariamente desabilitada")
    return response


def generate_excel_report(report_instance, data=None):
    """Gera um relatório em Excel - TEMPORARIAMENTE DESABILITADO"""
    response = HttpResponse(content_type='text/plain')
    response['Content-Disposition'] = f'attachment; filename="{report_instance.title}.txt"'
    response.write("Funcionalidade Excel temporariamente desabilitada")
    return response 