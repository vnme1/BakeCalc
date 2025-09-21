# BakeCalc 🥐
**제과제빵 영양성분·손실률·라벨 생성 웹앱 (Django + DRF)**  
재료 영양성분을 입력하면 레시피 단위로 총중량, 1회 제공량, 손실률 보정된 영양성분 라벨을 자동 생성합니다.  
판매자/제조자가 실제 판매용 라벨이나 영양표를 쉽게 만들 수 있도록 돕는 도구입니다.

---

## ✨ 주요 기능
### 📌 Ingredient (재료)
- 브랜드/제품명 + 100g 당 영양성분 입력
- 선택적으로 밀도(g/mL) 입력 → **mL 단위 입력 지원**
- 추후 단가(가격/100g) 입력 → 원가 계산 준비

### 📌 Recipe (레시피)
- 재료 조합으로 **총 영양성분 자동 계산**
- `piece_weight_g`(조각/1회 제공 중량) → 제공량(servings) 자동 계산
- `yield_rate`(손실률/증발률 %) → 굽기/식힘 후 실제 중량·영양 보정
- 레시피 노트 작성 가능

### 📌 Recipe Item (레시피 재료항목)
- g 또는 mL 단위로 입력 가능
- 밀도 입력된 재료는 mL → g 자동 환산

### 📌 라벨 & API
- `/recipes/<id>/label` → 영양성분표 HTML 라벨
- `/api/recipes/<id>/nutrition` → JSON 응답
- 총합, 1회 제공량, 손실률 적용 결과 모두 포함

### 📌 손실률 프리셋 API
- `/api/yield-presets/`
- 카테고리별 권장 손실률 기본값 제공 (예: 스폰지케이크 94%, 쿠키 85%)

---

## 🛠 기술 스택
- **Backend**: Python 3.12, Django 5.0, Django REST Framework
- **DB**: SQLite (개발용) → PostgreSQL 대응 가능
- **Frontend**: Django Template (영양라벨 페이지)
- **Others**:
  - dj-database-url (환경변수 기반 DB 설정)
  - python-dotenv (로컬 개발 환경)
  - psycopg2-binary (PostgreSQL 드라이버)

---

2. 가상환경 생성 및 활성화
python -m venv .venv
# Windows PowerShell
.\.venv\Scripts\Activate.ps1

---

3. 의존성 설치
pip install -r requirements.txt

---

4. DB 마이그레이션
python manage.py makemigrations
python manage.py migrate

---

5. 관리자 계정 생성
python manage.py createsuperuser

---

6. 개발 서버 실행
python manage.py runserver


→ 접속: http://127.0.0.1:8000/

---

📚 사용 예시
Ingredient 등록 (예: 서울우유 생크림)
kcal_per100g: 335
carbs_per100g: 3
protein_per100g: 2
fat_per100g: 35
sugar_per100g: 3
sodium_per100g: 27
density_g_per_ml: 1.0

Recipe 등록
title: 생크림케이크
piece_weight_g: 75
yield_rate: 92

API 호출

GET /api/recipes/1/nutrition

응답(JSON 예시)
{
  "recipe_id": 1,
  "title": "생크림케이크",
  "servings": 8,
  "piece_weight_g": 75,
  "total_weight_g": 540,
  "yield_rate": 92,
  "totals": {
    "kcal": 1620,
    "carbs": 144,
    "protein": 96,
    "fat": 240,
    "sugar": 72,
    "sodium": 432
  },
  "per_serving": {
    "kcal": 203,
    "carbs": 18,
    "protein": 12,
    "fat": 30,
    "sugar": 9,
    "sodium": 54
  }
}

---

📦 향후 계획 (Todo)

 원가 계산 (재료 단가 → 총원가/1회 원가/권장가 계산)

 PDF 라벨 다운로드 기능

 QR 코드 공유 페이지

 팀 계정/권한 관리

 공공 식품 DB 연동 (자동완성 지원)

---

git remote add origin https://github.com/vnme1/BakeCalc.git
git branch -M main
git push -u origin main