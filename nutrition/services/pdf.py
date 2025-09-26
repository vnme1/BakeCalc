# nutrition/services/pdf.py (완전 교체 버전)
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
    """멀티 플랫폼 한글 폰트 등록"""
    try:
        # 이미 등록된 폰트 체크
        registered_fonts = [f for f in pdfmetrics.getRegisteredFontNames() if f == 'Korean']
        if registered_fonts:
            return 'Korean'
        
        # 1. Linux/Render 환경 폰트
        linux_fonts = [
            '/usr/share/fonts/truetype/nanum/NanumGothic.ttf',
            '/usr/share/fonts/truetype/nanum/NanumBarunGothic.ttf',
            '/usr/share/fonts/truetype/nanum/NanumMyeongjo.ttf',
            '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
        ]
        
        # 2. Windows 환경 폰트
        windows_fonts = [
            r'C:\Windows\Fonts\malgun.ttf',
            r'C:\Windows\Fonts\gulim.ttc',
            r'C:\Windows\Fonts\batang.ttc'
        ]
        
        # 3. macOS 환경 폰트
        macos_fonts = [
            '/System/Library/Fonts/AppleGothic.ttf',
            '/Library/Fonts/Arial Unicode MS.ttf'
        ]
        
        # 모든 폰트 경로를 순서대로 체크
        all_fonts = linux_fonts + windows_fonts + macos_fonts
        
        for font_path in all_fonts:
            if os.path.exists(font_path):
                try:
                    pdfmetrics.registerFont(TTFont('Korean', font_path))
                    print(f"✅ 한글 폰트 등록 성공: {font_path}")
                    return 'Korean'
                except Exception as e:
                    print(f"폰트 등록 실패 {font_path}: {e}")
                    continue
        
        print("⚠️ 한글 폰트를 찾을 수 없습니다. 영문으로 표시됩니다.")
        return 'Helvetica'
        
    except Exception as e:
        print(f"폰트 등록 중 오류: {e}")
        return 'Helvetica'

def get_text_by_font(font_name, korean_text, english_text):
    """폰트에 따라 적절한 텍스트 반환"""
    return korean_text if font_name == 'Korean' else english_text

def generate_pdf_label(recipe, nutrition_data, allergens):
    """한글 지원 PDF 라벨 생성"""
    
    # 폰트 등록
    font_name = register_korean_fonts()
    is_korean = (font_name == 'Korean')
    
    # PDF 문서 생성
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=A4, 
        topMargin=2*cm, 
        bottomMargin=2*cm,
        leftMargin=2*cm,
        rightMargin=2*cm
    )
    
    # 스타일 정의
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontName=font_name,
        fontSize=20,
        spaceAfter=12,
        alignment=TA_CENTER,
        textColor=colors.black
    )
    
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Normal'],
        fontName=font_name,
        fontSize=14,
        spaceAfter=16,
        alignment=TA_CENTER,
        textColor=colors.grey
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontName=font_name,
        fontSize=11,
        alignment=TA_LEFT
    )
    
    # PDF 내용 생성
    story = []
    
    # 제목
    title_text = get_text_by_font(font_name, 
        f"<b>{recipe.title}</b>", 
        f"<b>{recipe.title} - Nutrition Facts</b>"
    )
    story.append(Paragraph(title_text, title_style))
    
    subtitle_text = get_text_by_font(font_name, "영양성분표", "Nutrition Information")
    story.append(Paragraph(subtitle_text, subtitle_style))
    
    # 기본 정보 테이블
    if is_korean:
        info_headers = ['항목', '값', '항목', '값']
        info_data = [
            info_headers,
            ['총중량', f"{nutrition_data['total_weight_g']}g", '제공량', f"{nutrition_data['servings']}회"],
            ['1회 분량', f"{nutrition_data['piece_weight_g']}g", '수율', f"{nutrition_data['yield_rate']:.0f}%"]
        ]
    else:
        info_headers = ['Item', 'Value', 'Item', 'Value']
        info_data = [
            info_headers,
            ['Total Weight', f"{nutrition_data['total_weight_g']}g", 'Servings', f"{nutrition_data['servings']}"],
            ['Per Serving', f"{nutrition_data['piece_weight_g']}g", 'Yield Rate', f"{nutrition_data['yield_rate']:.0f}%"]
        ]
    
    info_table = Table(info_data, colWidths=[3.5*cm, 3*cm, 3.5*cm, 3*cm])
    info_table.setStyle(TableStyle([
        # 헤더 스타일
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('FONTNAME', (0, 0), (-1, 0), font_name),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('FONTWEIGHT', (0, 0), (-1, 0), 'BOLD'),
        
        # 데이터 스타일
        ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('FONTNAME', (0, 1), (-1, -1), font_name),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        
        # 전체 스타일
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
    ]))
    
    story.append(info_table)
    story.append(Spacer(1, 24))
    
    # 영양성분 테이블
    if is_korean:
        nutrition_headers = ['영양성분', '총량', '1회 제공량']
        nutrition_rows = [
            ['열량(kcal)', str(nutrition_data['totals']['kcal']), str(nutrition_data['per_serving']['kcal'])],
            ['탄수화물(g)', str(nutrition_data['totals']['carbs']), str(nutrition_data['per_serving']['carbs'])],
            ['단백질(g)', str(nutrition_data['totals']['protein']), str(nutrition_data['per_serving']['protein'])],
            ['지방(g)', str(nutrition_data['totals']['fat']), str(nutrition_data['per_serving']['fat'])],
            ['당류(g)', str(nutrition_data['totals']['sugar']), str(nutrition_data['per_serving']['sugar'])],
            ['나트륨(mg)', str(nutrition_data['totals']['sodium']), str(nutrition_data['per_serving']['sodium'])],
        ]
    else:
        nutrition_headers = ['Nutrition Facts', 'Total', 'Per Serving']
        nutrition_rows = [
            ['Calories(kcal)', str(nutrition_data['totals']['kcal']), str(nutrition_data['per_serving']['kcal'])],
            ['Carbohydrates(g)', str(nutrition_data['totals']['carbs']), str(nutrition_data['per_serving']['carbs'])],
            ['Protein(g)', str(nutrition_data['totals']['protein']), str(nutrition_data['per_serving']['protein'])],
            ['Fat(g)', str(nutrition_data['totals']['fat']), str(nutrition_data['per_serving']['fat'])],
            ['Sugar(g)', str(nutrition_data['totals']['sugar']), str(nutrition_data['per_serving']['sugar'])],
            ['Sodium(mg)', str(nutrition_data['totals']['sodium']), str(nutrition_data['per_serving']['sodium'])],
        ]
    
    nutrition_data_table = [nutrition_headers] + nutrition_rows
    
    nutrition_table = Table(nutrition_data_table, colWidths=[5*cm, 3.5*cm, 3.5*cm])
    nutrition_table.setStyle(TableStyle([
        # 헤더 스타일
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), font_name),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('FONTWEIGHT', (0, 0), (-1, 0), 'BOLD'),
        
        # 데이터 스타일
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('FONTNAME', (0, 1), (-1, -1), font_name),
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
    
    # 알레르기 정보
    allergen_title = get_text_by_font(font_name, 
        "<b>⚠️ 알레르기 유발요소</b>", 
        "<b>⚠️ Allergen Information</b>"
    )
    story.append(Paragraph(allergen_title, normal_style))
    story.append(Spacer(1, 8))
    
    if allergens:
        allergen_list = ", ".join(allergens)
        if not is_korean:
            allergen_list = f"Contains: {allergen_list}"
        story.append(Paragraph(f"<font color='red'><b>{allergen_list}</b></font>", normal_style))
    else:
        no_allergen_text = get_text_by_font(font_name,
            "알레르기 유발요소 없음",
            "No known allergens"
        )
        story.append(Paragraph(f"<font color='green'><b>{no_allergen_text}</b></font>", normal_style))
    
    story.append(Spacer(1, 24))
    
    # 하단 주의사항
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontName=font_name,
        fontSize=9,
        textColor=colors.grey,
        alignment=TA_CENTER
    )
    
    if is_korean:
        footer_text = [
            "※ 표시값은 소수점 1자리 반올림 기준입니다",
            "※ 제조 과정에서 교차 오염 가능성이 있습니다"
        ]
    else:
        footer_text = [
            "※ Values are rounded to 1 decimal place",
            "※ Cross-contamination possible during manufacturing"
        ]
    
    for text in footer_text:
        story.append(Paragraph(text, footer_style))
    
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
    """PDF HTTP 응답 생성"""
    response = HttpResponse(pdf_data, content_type='application/pdf')
    
    # 파일명 안전하게 처리 (한글 문제 방지)
    safe_filename = filename.encode('utf-8', errors='ignore').decode('utf-8')
    response['Content-Disposition'] = f'attachment; filename="{safe_filename}"'
    response['Content-Length'] = len(pdf_data)
    
    return response