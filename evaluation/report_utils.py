"""
Helper functions for PDF report generation.
Centralizes common logic for employee, manager, and trends reports.
"""

import logging
from datetime import datetime, timedelta
from django.utils import timezone
from reportlab.lib import colors as pdf_colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER
from authentication.models import Department
from .models import ReportHistory

logger = logging.getLogger(__name__)


def get_pdf_styles():
    """Get common PDF styles for reports."""
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=pdf_colors.HexColor('#DC2626'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=pdf_colors.HexColor('#1a1a1a'),
        spaceAfter=12,
    )
    
    return styles, title_style, heading_style


def parse_date_range(date_range, start_date_str, end_date_str):
    """Parse date range parameters and return start_date, end_date."""
    end_date = timezone.now().date()
    if date_range == 'custom' and start_date_str and end_date_str:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
    else:
        days = int(date_range)
        start_date = end_date - timedelta(days=days)
    return start_date, end_date


def get_department_info(department_id):
    """Get department name and object for report. Returns (dept_name, dept_obj)."""
    if department_id == 'all':
        return "All Departments", None
    else:
        dept = Department.objects.get(id=department_id)
        return dept.title, dept


def create_summary_table(summary_data, col_widths):
    """Create a standardized summary table with red/grey/white theme."""
    summary_table = Table(summary_data, colWidths=col_widths)
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), pdf_colors.HexColor('#DC2626')),
        ('TEXTCOLOR', (0, 0), (-1, 0), pdf_colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), pdf_colors.HexColor('#F3F4F6')),
        ('GRID', (0, 0), (-1, -1), 1, pdf_colors.HexColor('#D1D5DB'))
    ]))
    return summary_table


def create_detail_table(table_data, col_widths):
    """Create a standardized detail table with red/grey/white theme."""
    table = Table(table_data, colWidths=col_widths)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), pdf_colors.HexColor('#DC2626')),
        ('TEXTCOLOR', (0, 0), (-1, 0), pdf_colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('FONTSIZE', (0, 1), (-1, -1), 7),
        ('TOPPADDING', (0, 0), (-1, 0), 8),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('BACKGROUND', (0, 1), (-1, -1), pdf_colors.white),
        ('GRID', (0, 0), (-1, -1), 0.5, pdf_colors.HexColor('#D1D5DB')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [pdf_colors.white, pdf_colors.HexColor('#F3F4F6')]),
        ('VALIGN', (0, 0), (-1, -1), 'TOP')
    ]))
    return table


def create_chart_metrics_table(table_data, col_widths):
    """Create a table for chart metrics with optimized styling."""
    table = Table(table_data, colWidths=col_widths)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), pdf_colors.HexColor('#DC2626')),
        ('TEXTCOLOR', (0, 0), (-1, 0), pdf_colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, 0), 8),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('BACKGROUND', (0, 1), (-1, -1), pdf_colors.white),
        ('GRID', (0, 0), (-1, -1), 0.5, pdf_colors.HexColor('#D1D5DB')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [pdf_colors.white, pdf_colors.HexColor('#F3F4F6')]),
        ('VALIGN', (0, 0), (-1, -1), 'TOP')
    ]))
    return table


def create_person_header(name, department):
    """Create a red header table for individual person sections."""
    header = Table([[name], [department]], colWidths=[6.5*inch])
    header.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), pdf_colors.HexColor('#DC2626')),
        ('TEXTCOLOR', (0, 0), (-1, -1), pdf_colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 13),
        ('FONTSIZE', (0, 1), (-1, 1), 10),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('TOPPADDING', (0, 0), (-1, 0), 8),
        ('BOTTOMPADDING', (0, 1), (-1, 1), 8),
    ]))
    return header


def create_individual_question_table(table_data, col_widths):
    """Create a grey-header table for individual questions."""
    table = Table(table_data, colWidths=col_widths, repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), pdf_colors.HexColor('#6B7280')),
        ('TEXTCOLOR', (0, 0), (-1, 0), pdf_colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (2, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, 0), 8),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('BACKGROUND', (0, 1), (-1, -1), pdf_colors.white),
        ('GRID', (0, 0), (-1, -1), 0.5, pdf_colors.HexColor('#D1D5DB')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [pdf_colors.white, pdf_colors.HexColor('#F9FAFB')]),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    return table


def save_report_history(report_type, user_profile, dept_obj, start_date, end_date):
    """Save report generation to history."""
    ReportHistory.objects.create(
        report_type=report_type,
        generated_by=user_profile,
        department=dept_obj,
        date_from=start_date,
        date_to=end_date
    )
    dept_name = dept_obj.title if dept_obj else "All Departments"
    logger.info(f"Report saved: {report_type} | {dept_name} | {start_date} to {end_date} | by {user_profile.user.get_full_name()}")


def create_question_paragraph(question_text, font_size=8):
    """Create a paragraph for question text with proper wrapping."""
    styles = getSampleStyleSheet()
    return Paragraph(
        question_text, 
        ParagraphStyle(
            'QuestionText', 
            parent=styles['Normal'],
            fontSize=font_size, 
            leading=9, 
            wordWrap='CJK'
        )
    )

