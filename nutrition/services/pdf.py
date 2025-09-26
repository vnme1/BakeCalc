# nutrition/services/pdf.py (완전한 영문 버전 - 전체 교체)
from io import BytesIO
from django.http import HttpResponse
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import os

def register_korean_fonts():
    """영문 전용 처리 - Render Free 안전 버전"""
    return 'Helvetica'

def translate_allergen(korean_allergen):
    """한글 알레르기 정보를 영문으로 변환"""
    allergen_map = {
        '유제품': 'Dairy/Milk',
        '유제품 포함': 'Dairy/Milk', 
        '계란': 'Eggs',
        '계란 포함': 'Eggs',
        '글루텐': 'Gluten/Wheat',
        '글루텐 포함': 'Gluten/Wheat',
        '견과류': 'Tree Nuts',
        '견과류 포함': 'Tree Nuts',
        '대두': 'Soy',
        '대두 포함': 'Soy',
        '갑각류': 'Shellfish',
        '갑각류 포함': 'Shellfish'
    }
    return allergen_map.get(korean_allergen, korean_allergen)

def generate_pdf_label(recipe, nutrition_data, allergens):
    """영문 전용 PDF 라벨 생성 - Render Free 완전 호환 버전"""
    
    # 메모리에 PDF 생성
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=A4, 
        topMargin=1.5*cm, 
        bottomMargin=1.5*cm,
        leftMargin=2*cm,
        rightMargin=2*cm
    )
    
    # 스타일 정의 (Helvetica 전용)
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        spaceAfter=8,
        alignment=TA_CENTER,
        textColor=colors.black
    )
    
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=14,
        spaceAfter=16,
        alignment=TA_CENTER,
        textColor=colors.grey
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=11,
        alignment=TA_LEFT,
        textColor=colors.black
    )
    
    bold_style = ParagraphStyle(
        'CustomBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        alignment=TA_LEFT,
        textColor=colors.black
    )
    
    # PDF 내용 생성
    story = []
    
    # 메인 제목
    story.append(Paragraph(f"<b>{recipe.title}</b>", title_style))
    story.append(Paragraph("Nutrition Facts Label", subtitle_style))
    
    # 구분선
    story.append(Spacer(1, 8))
    
    # 기본 정보 섹션
    basic_info_style = ParagraphStyle(
        'BasicInfo',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        spaceAfter=8,
        textColor=colors.darkblue
    )
    
    story.append(Paragraph("Product Information", basic_info_style))
    
    # 기본 정보 테이블
    info_data = [
        ['Item', 'Value', 'Item', 'Value'],
        ['Total Weight', f"{nutrition_data['total_weight_g']} g", 'Total Servings', f"{nutrition_data['servings']}"],
        ['Weight per Serving', f"{nutrition_data['piece_weight_g']} g", 'Yield Rate', f"{nutrition_data['yield_rate']:.0f}%"]
    ]
    
    info_table = Table(info_data, colWidths=[3.5*cm, 3*cm, 3.5*cm, 3*cm])
    info_table.setStyle(TableStyle([
        # 헤더 스타일
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        
        # 데이터 스타일
        ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        
        # 전체 스타일
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
    ]))
    
    story.append(info_table)
    story.append(Spacer(1, 20))
    
    # 영양성분 섹션 제목
    story.append(Paragraph("Nutritional Information", basic_info_style))
    
    # 영양성분 테이블
    nutrition_table_data = [
        ['Nutrition Facts', 'Total Amount', 'Per Serving'],
        ['Calories (kcal)', str(nutrition_data['totals']['kcal']), str(nutrition_data['per_serving']['kcal'])],
        ['Carbohydrates (g)', str(nutrition_data['totals']['carbs']), str(nutrition_data['per_serving']['carbs'])],
        ['Protein (g)', str(nutrition_data['totals']['protein']), str(nutrition_data['per_serving']['protein'])],
        ['Total Fat (g)', str(nutrition_data['totals']['fat']), str(nutrition_data['per_serving']['fat'])],
        ['Total Sugars (g)', str(nutrition_data['totals']['sugar']), str(nutrition_data['per_serving']['sugar'])],
        ['Sodium (mg)', str(nutrition_data['totals']['sodium']), str(nutrition_data['per_serving']['sodium'])],
    ]
    
    nutrition_table = Table(nutrition_table_data, colWidths=[5*cm, 3.5*cm, 3.5*cm])
    nutrition_table.setStyle(TableStyle([
        # 헤더 스타일
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        
        # 데이터 스타일
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 11),
        
        # 정렬
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),   # 첫 번째 컬럼은 왼쪽 정렬
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'), # 나머지는 중앙 정렬
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        
        # 테두리
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
    ]))
    
    story.append(nutrition_table)
    story.append(Spacer(1, 24))
    
    # 알레르기 정보 섹션
    allergen_style = ParagraphStyle(
        'AllergenTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        spaceAfter=8,
        textColor=colors.red
    )
    
    story.append(Paragraph("⚠️ Allergen Information", allergen_style))
    
    if allergens:
        # 한글 알레르기 정보를 영문으로 변환
        english_allergens = [translate_allergen(allergen) for allergen in allergens]
        allergen_text = f"<b>Contains: {', '.join(english_allergens)}</b>"
        
        allergen_content_style = ParagraphStyle(
            'AllergenContent',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=11,
            textColor=colors.red,
            leftIndent=20
        )
        
        story.append(Paragraph(allergen_text, allergen_content_style))
    else:
        no_allergen_style = ParagraphStyle(
            'NoAllergen',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=11,
            textColor=colors.green,
            leftIndent=20
        )
        story.append(Paragraph("<b>✓ No known allergens</b>", no_allergen_style))
    
    story.append(Spacer(1, 24))
    
    # 추가 정보 섹션
    additional_info_style = ParagraphStyle(
        'AdditionalInfo',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        textColor=colors.darkblue,
        leftIndent=10
    )
    
    story.append(Paragraph("<b>Additional Information:</b>", additional_info_style))
    story.append(Spacer(1, 8))
    
    # 카테고리 정보 (있는 경우)
    if hasattr(recipe, 'category') and recipe.category:
        category_display = dict(recipe.Category.choices).get(recipe.category, recipe.category)
        story.append(Paragraph(f"• Product Category: {category_display}", additional_info_style))
    
    # 레시피 노트 (있는 경우)
    if recipe.notes:
        notes_text = recipe.notes[:200] + "..." if len(recipe.notes) > 200 else recipe.notes
        story.append(Paragraph(f"• Notes: {notes_text}", additional_info_style))
    
    story.append(Spacer(1, 20))
    
    # 하단 면책조항
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        textColor=colors.grey,
        alignment=TA_CENTER,
        spaceAfter=4
    )
    
    disclaimer_text = [
        "※ Nutritional values are rounded to 1 decimal place",
        "※ Cross-contamination with allergens may occur during manufacturing",
        "※ This label is generated for informational purposes",
        "※ Values may vary slightly from actual product"
    ]
    
    for text in disclaimer_text:
        story.append(Paragraph(text, footer_style))
    
    # 생성 정보
    from datetime import datetime
    generation_info = f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M')} UTC"
    generation_style = ParagraphStyle(
        'Generation',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        textColor=colors.lightgrey,
        alignment=TA_CENTER
    )
    story.append(Spacer(1, 12))
    story.append(Paragraph(generation_info, generation_style))
    
    # PDF 생성
    try:
        doc.build(story)
        pdf_data = buffer.getvalue()
        buffer.close()
        return pdf_data
    except Exception as e:
        print(f"PDF 생성 오류: {e}")
        buffer.close()
        raise

def create_pdf_response(pdf_data, filename):
    """PDF HTTP 응답 생성 - 영문 파일명"""
    response = HttpResponse(pdf_data, content_type='application/pdf')
    
    # 영문 파일명으로 안전하게 처리
    safe_filename = filename.replace(' ', '_').replace('/', '_').replace('\\', '_')
    # 특수문자 제거
    safe_filename = ''.join(c for c in safe_filename if c.isalnum() or c in '._-')
    
    response['Content-Disposition'] = f'attachment; filename="{safe_filename}"'
    response['Content-Length'] = len(pdf_data)
    
    return response