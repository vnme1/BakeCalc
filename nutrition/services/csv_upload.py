# nutrition/services/csv_upload.py
import pandas as pd
import io
from django.core.exceptions import ValidationError
from ..models import Ingredient
from decimal import Decimal, InvalidOperation

def validate_csv_headers(df):
    """CSV 헤더 검증"""
    required_headers = [
        'brand', 'name', 'kcal_per100g', 'carbs_per100g', 
        'protein_per100g', 'fat_per100g', 'sugar_per100g', 'sodium_per100g'
    ]
    
    optional_headers = [
        'unit', 'density_g_per_ml', 'price_per_100g',
        'contains_milk', 'contains_egg', 'contains_gluten', 
        'contains_nuts', 'contains_soy', 'contains_shellfish'
    ]
    
    # 헤더 정규화 (공백 제거, 소문자 변환)
    df.columns = df.columns.str.strip().str.lower()
    
    missing_headers = [h for h in required_headers if h not in df.columns]
    
    if missing_headers:
        raise ValidationError(f"필수 컬럼이 누락되었습니다: {', '.join(missing_headers)}")
    
    return df

def clean_decimal_field(value, field_name):
    """숫자 필드 정리 및 검증"""
    if pd.isna(value) or value == '':
        return Decimal('0')
    
    try:
        # 문자열에서 숫자가 아닌 문자 제거 (쉼표, 공백 등)
        if isinstance(value, str):
            value = value.replace(',', '').replace(' ', '').strip()
        
        decimal_value = Decimal(str(value))
        
        if decimal_value < 0:
            raise ValidationError(f"{field_name}은(는) 음수일 수 없습니다.")
        
        return decimal_value
    
    except (ValueError, InvalidOperation):
        raise ValidationError(f"{field_name}의 값이 올바르지 않습니다: {value}")

def clean_boolean_field(value):
    """불린 필드 정리"""
    if pd.isna(value) or value == '':
        return False
    
    if isinstance(value, bool):
        return value
    
    # 문자열 처리
    if isinstance(value, str):
        value = value.strip().lower()
        return value in ['true', '1', 'yes', 'y', '예', 'o', 'x']
    
    # 숫자 처리
    return bool(value)

def process_csv_data(file_content, file_extension):
    """CSV/Excel 데이터 처리"""
    
    try:
        # 파일 형식에 따른 읽기
        if file_extension.lower() in ['.xlsx', '.xls']:
            df = pd.read_excel(io.BytesIO(file_content))
        else:  # CSV
            # 인코딩 자동 감지
            try:
                df = pd.read_csv(io.StringIO(file_content.decode('utf-8')))
            except UnicodeDecodeError:
                try:
                    df = pd.read_csv(io.StringIO(file_content.decode('cp949')))
                except UnicodeDecodeError:
                    df = pd.read_csv(io.StringIO(file_content.decode('latin-1')))
        
        # 빈 행 제거
        df = df.dropna(how='all')
        
        if df.empty:
            raise ValidationError("파일에 데이터가 없습니다.")
        
        # 헤더 검증
        df = validate_csv_headers(df)
        
        processed_data = []
        errors = []
        
        for index, row in df.iterrows():
            try:
                # 필수 필드 검증
                if pd.isna(row.get('name')) or str(row.get('name')).strip() == '':
                    errors.append(f"행 {index + 2}: 제품명이 필요합니다.")
                    continue
                
                # 데이터 정리
                ingredient_data = {
                    'brand': str(row.get('brand', '')).strip(),
                    'name': str(row['name']).strip(),
                    'unit': str(row.get('unit', 'g')).strip(),
                    'kcal_per100g': clean_decimal_field(row['kcal_per100g'], '칼로리'),
                    'carbs_per100g': clean_decimal_field(row['carbs_per100g'], '탄수화물'),
                    'protein_per100g': clean_decimal_field(row['protein_per100g'], '단백질'),
                    'fat_per100g': clean_decimal_field(row['fat_per100g'], '지방'),
                    'sugar_per100g': clean_decimal_field(row['sugar_per100g'], '당류'),
                    'sodium_per100g': clean_decimal_field(row['sodium_per100g'], '나트륨'),
                    'density_g_per_ml': clean_decimal_field(row.get('density_g_per_ml', 0), '밀도') or None,
                    'price_per_100g': clean_decimal_field(row.get('price_per_100g', 0), '가격'),
                    'contains_milk': clean_boolean_field(row.get('contains_milk', False)),
                    'contains_egg': clean_boolean_field(row.get('contains_egg', False)),
                    'contains_gluten': clean_boolean_field(row.get('contains_gluten', False)),
                    'contains_nuts': clean_boolean_field(row.get('contains_nuts', False)),
                    'contains_soy': clean_boolean_field(row.get('contains_soy', False)),
                    'contains_shellfish': clean_boolean_field(row.get('contains_shellfish', False)),
                }
                
                processed_data.append(ingredient_data)
                
            except ValidationError as e:
                errors.append(f"행 {index + 2}: {str(e)}")
            except Exception as e:
                errors.append(f"행 {index + 2}: 처리 중 오류 - {str(e)}")
        
        return processed_data, errors
        
    except Exception as e:
        raise ValidationError(f"파일 처리 중 오류가 발생했습니다: {str(e)}")

def bulk_create_ingredients(processed_data, update_existing=False):
    """재료 대량 생성"""
    created_count = 0
    updated_count = 0
    skipped_count = 0
    errors = []
    
    for data in processed_data:
        try:
            # 중복 체크
            existing = Ingredient.objects.filter(
                brand=data['brand'], 
                name=data['name']
            ).first()
            
            if existing:
                if update_existing:
                    # 기존 데이터 업데이트
                    for key, value in data.items():
                        setattr(existing, key, value)
                    existing.save()
                    updated_count += 1
                else:
                    skipped_count += 1
                    continue
            else:
                # 새 데이터 생성
                Ingredient.objects.create(**data)
                created_count += 1
                
        except Exception as e:
            errors.append(f"{data['brand']} {data['name']}: {str(e)}")
    
    return {
        'created': created_count,
        'updated': updated_count,
        'skipped': skipped_count,
        'errors': errors
    }