# nutrition/services/pdf.py (한글 지원 버전)
from io import BytesIO
from django.http import HttpResponse
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import os

def register_korean_fonts():
    """한글 폰트 등록 (시스템 폰트 사용)"""
    try:
        # Windows 시스템 폰트 경로들
        font_paths = [
            r'C:\Windows\Fonts\malgun.ttf',      # 맑은고딕
            r'C:\Windows\Fonts\gulim.ttc',       # 굴림
            r'C:\Windows\Fonts\batang.ttc',      # 바탕
        ]
        
        for font_path in font_paths:
            if os.path.exists(font_path):
                pdfmetrics.registerFont(TTFont('Korean', font_path))
                return 'Korean'
                
        # 폰트를 찾지 못한 경우 기본 폰트 사용
        return 'Helvetica'
        
    except Exception:
        return 'Helvetica'

def generate_pdf_label(recipe, nutrition_data, allergens):
    """한글 지원 PDF 라벨 생성"""
    
    # 한글 폰트 등록
    korean_font = register_korean_fonts()
    
    # 메모리에 PDF 생성
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=2*cm, bottomMargin=2*cm)
    
    # 스타일 설정 (한글 폰트 적용)
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'KoreanTitle',
        parent=styles['Heading1'],
        fontName=korean_font,
        fontSize=18,
        spaceAfter=12,
        alignment=TA_CENTER,
        textColor=colors.black
    )
    
    subtitle_style = ParagraphStyle(
        'KoreanSubtitle',
        parent=styles['Normal'],
        fontName=korean_font,
        fontSize=12,
        spaceAfter=8,
        alignment=TA_CENTER,
        textColor=colors.grey
    )
    
    normal_style = ParagraphStyle(
        'KoreanNormal',
        parent=styles['Normal'],
        fontName=korean_font,
        fontSize=10,
        alignment=TA_LEFT
    )
    
    # PDF 내용 구성
    story = []
    
    # 제목
    story.append(Paragraph(f"<b>{recipe.title}</b>", title_style))
    story.append(Paragraph("영양성분표", subtitle_style))
    story.append(Spacer(1, 12))
    
    # 기본 정보 (한글로 표시)
    info_data = [
        ['총중량', f"{nutrition_data['total_weight_g']}g", '제공량', f"{nutrition_data['servings']}회"],
        ['1회 제공량', f"{nutrition_data['piece_weight_g']}g", '손실률', f"{nutrition_data['yield_rate']:.0f}%"]
    ]
    
    info_table = Table(info_data, colWidths=[3*cm, 3*cm, 3*cm, 3*cm])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), korean_font),  # 한글 폰트 적용
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    
    story.append(info_table)
    story.append(Spacer(1, 20))
    
    # 영양성분 테이블 (한글로 표시)
    nutrition_data_table = [
        ['영양성분', '총량', '1회 제공량'],
        ['열량(kcal)', str(nutrition_data['totals']['kcal']), str(nutrition_data['per_serving']['kcal'])],
        ['탄수화물(g)', str(nutrition_data['totals']['carbs']), str(nutrition_data['per_serving']['carbs'])],
        ['단백질(g)', str(nutrition_data['totals']['protein']), str(nutrition_data['per_serving']['protein'])],
        ['지방(g)', str(nutrition_data['totals']['fat']), str(nutrition_data['per_serving']['fat'])],
        ['당류(g)', str(nutrition_data['totals']['sugar']), str(nutrition_data['per_serving']['sugar'])],
        ['나트륨(mg)', str(nutrition_data['totals']['sodium']), str(nutrition_data['per_serving']['sodium'])],
    ]
    
    nutrition_table = Table(nutrition_data_table, colWidths=[4*cm, 3*cm, 3*cm])
    nutrition_table.setStyle(TableStyle([
        # 헤더 스타일
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), korean_font),  # 한글 폰트 적용
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        
        # 데이터 스타일
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    
    story.append(nutrition_table)
    story.append(Spacer(1, 20))
    
    # 알레르기 정보
    story.append(Paragraph("<b>⚠️ 알레르기 유발요소</b>", normal_style))
    story.append(Spacer(1, 8))
    
    if allergens:
        allergen_text = ", ".join(allergens)
        story.append(Paragraph(f"<font color='red'><b>{allergen_text}</b></font>", normal_style))
    else:
        story.append(Paragraph("<font color='green'>알레르기 유발요소 없음</font>", normal_style))
    
    story.append(Spacer(1, 20))
    
    # 주의사항
    footer_style = ParagraphStyle(
        'KoreanFooter',
        parent=styles['Normal'],
        fontName=korean_font,
        fontSize=8,
        textColor=colors.grey,
        alignment=TA_CENTER
    )
    
    story.append(Paragraph("※ 표시값은 소수점 1자리 반올림 기준", footer_style))
    story.append(Paragraph("※ 제조 과정에서 교차 오염 가능성 있음", footer_style))
    
    # PDF 생성
    doc.build(story)
    pdf_data = buffer.getvalue()
    buffer.close()
    
    return pdf_data

def create_pdf_response(pdf_data, filename):
    """PDF HTTP 응답 생성"""
    response = HttpResponse(pdf_data, content_type='application/pdf')
    # 한글 파일명을 위한 인코딩
    response['Content-Disposition'] = f'attachment; filename*=UTF-8\'\'{filename}'
    response['Content-Length'] = len(pdf_data)
    return response