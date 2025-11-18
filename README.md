# GAECHWI - AI 기반 구인구직 및 취업 준비 통합 플랫폼 (백엔드 상세 문서)

**발표자:** 박영서, 김경환

---

## 목차

1. [프로젝트 소개](#1-프로젝트-소개)
2. [백엔드 팀 구성](#2-백엔드-팀-구성)
3. [시스템 아키텍처](#3-시스템-아키텍처)
4. [기술 스택 (백엔드)](#4-기술-스택-백엔드)
5. [프로젝트 구조](#5-프로젝트-구조)
6. [핵심 기능 분석](#6-핵심-기능-분석)
7. [데이터베이스 설계](#7-데이터베이스-설계)
8. [API 엔드포인트](#8-api-엔드포인트)
9. [인증 및 보안](#9-인증-및-보안)
10. [성능 최적화 및 캐싱](#10-성능-최적화-및-캐싱)
11. [개발 가이드](#11-개발-가이드)
12. [배포 및 운영](#12-배포-및-운영)
13. [트러블슈팅 및 해결 사항](#13-트러블슈팅-및-해결-사항)

---

## 1. 프로젝트 소개

GAECHWI는 AI 기반 이력서 첨삭, 모의 면접, 맞춤형 학습 가이드를 제공하는 취업 준비 통합 플랫폼입니다.

### 핵심 가치

- **자동화된 피드백**: OpenAI API를 활용한 고급 자연어 처리로 이력서 분석
- **채용 공고 연동**: 각 채용 공고별 맞춤형 피드백 및 학습 가이드
- **실시간 상호작용**: 모의 면접을 통한 실전 경험 제공

---

## 2. 백엔드 팀 구성

| 이름 | 역할 | 담당 영역 |
| --- | --- | --- |
| **박영서** | 아키텍트, 개발자 | DB 설계/구현, AI 통합, 이력서/피드백 로직, OAuth 인증 |
| **김경환** | 개발자 | 채용 공고 관리 , DB 설계/구현 , 유저 관리|

---

## 3. 시스템 아키텍처

### 전체 흐름도

```
아키텍처 구조도 사진
```

### 레이어별 구성

```
┌─────────────────────────────────────────────┐
│  Router Layer (app/routers/)                │
│  - auth.py (Google OAuth, JWT)              │
│  - resumes.py (이력서 CRUD)                 │
│  - resume_feedback.py (AI 피드백)           │
│  - job_postings.py (공고 관리)              │
│  - users.py (사용자 정보)                   │
└─────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────┐
│  Business Logic Layer (app/util/)           │
│  - resume_util.py (이력서 조회/생성)        │
│  - resume_feedback_util.py (AI 분석)        │
│  - posting_util.py (공고 CRUD)              │
│  - login_logic.py (사용자 조회)             │
│  - storage_util.py (S3 파일 관리)           │
│  - security.py (JWT, OAuth)                 │
└─────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────┐
│  Data Access Layer                          │
│  - models.py (17개 SQLAlchemy ORM 모델)    │
│  - database.py (async/sync 엔진 관리)       │
│  - schemas.py (Pydantic 검증 스키마)        │
└─────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────┐
│  External Services                          │
│  - OpenAI API (LangChain 기반 피드백)       │
│  - AWS S3 (파일 저장소)                     │
│  - Google OAuth (인증)                      │
│  - PostgreSQL + Redis (데이터 저장)         │
└─────────────────────────────────────────────┘
```

---

## 4. 기술 스택 (백엔드)

| 분류 | 기술 | 버전 | 용도 |
| --- | --- | --- | --- |
| **Framework** | FastAPI | 비동기 API 서버 |
| **ASGI Server** | Uvicorn | 고성능 ASGI 서버 |
| **Database** | PostgreSQL | 관계형 DB |
| **ORM** | SQLAlchemy | 비동기 ORM |
| **Migration** | Alembic | 스키마 버전 관리 |
| **AI/ML** | LangChain | 자연어 처리 |
| **LLM** | OpenAI | 텍스트 생성 |
| **Cache** | Redis | 세션/캐시 |
| **Auth** | Python-jose | JWT 토큰 |
| **OAuth** | Google Auth | 사용자 인증 |
| **File Storage** | Boto3 (Lightsail bucket) | 파일 저장소 |
| **Validation** | Pydantic | 데이터 검증 |
| **Container** | Docker | 컨테이너화 |
| **Container Compose** | Docker Compose | 로컬 개발 환경 |

---

## 5. 프로젝트 구조

```
/Users/yeongseo/Desktop/final_project/
├── app/
│   ├── routers/              # API 엔드포인트
│   │   ├── auth.py           # 인증 (Google OAuth, JWT)
│   │   ├── resumes.py        # 이력서 CRUD
│   │   ├── resume_feedback.py# AI 피드백 생성/조회
│   │   ├── job_postings.py   # 채용 공고 관리
│   │   └── users.py          # 사용자 정보
│   │
│   ├── util/                 # 비즈니스 로직
│   │   ├── resume_util.py    # 이력서 조회/생성 로직
│   │   ├── resume_feedback_util.py  # AI 분석 로직
│   │   ├── posting_util.py   # 공고 CRUD 로직
│   │   ├── login_logic.py    # 사용자 조회 로직
│   │   ├── storage_util.py   # S3 파일 관리
│   │   └── security.py       # JWT, OAuth 처리
│   │
│   ├── models.py             # SQLAlchemy ORM (17개 테이블)
│   ├── schemas.py            # Pydantic 검증 스키마
│   ├── database.py           # 비동기/동기 DB 엔진
│   └── config/
│       ├── settings.py       # 환경별 설정
│       ├── base.py           # 공통 설정
│       ├── development.py    # 개발 환경
│       └── production.py     # 운영 환경
│
├── alembic/                  # 데이터베이스 마이그레이션
│   ├── env.py
│   ├── versions/             # 마이그레이션 파일 (21개)
│   └── script.py.mako
│
├── main.py                   # FastAPI 앱 진입점
├── requirements.txt          # Python 의존성
├── docker-compose.dev.yml    # 로컬 개발 환경
├── docker-compose.yml        # 운영 환경
├── Dockerfile               # 컨테이너 이미지
├── .env.example             # 환경변수 템플릿
└── README.md                # 이 문서
```

---

## 6. 핵심 기능 분석

### 6.1 AI 기반 이력서 피드백 시스템

#### 데이터 흐름

```
사용자 이력서 입력
    ↓
[resume_feedback.py] POST /resume_feedbacks/standard/{resume_id}
    ↓
[resume_feedback_util.py] resume_standard_feedback()
    ├─ LangChain + OpenAI로 분석
    ├─ ResumeFeedbackAI 구조화
    └─ 매칭률, 피드백 분류 생성
    ↓
[resume_feedback.py] ResumeFeedback 객체 생성
    ├─ DB 저장 (ResumeFeedback 테이블)
    ├─ 피드백 내용 저장 (FeedbackContent 테이블)
    └─ Code 테이블과 JOIN
    ↓
[resume_feedback_util.py] get_resume_feedback()
    ├─ joinedload로 관계 로드
    ├─ Code 매핑으로 코드값 → 설명 변환
    └─ ResumeFeedbackResponse로 변환
    ↓
클라이언트에 JSON 반환
```

#### 핵심 코드 구조

```python
# 1. 피드백 생성 (router)
async def resume_feedback():
    result = await resume_standard_feedback(resume)  # AI 분석
    new_feedback = ResumeFeedback(...)               # ORM 객체
    db.add(new_feedback)
    await db.commit()

# 2. 피드백 조회 (util)
async def get_resume_feedback(feedback_id, db):
    feedback = await db.execute(
        select(ResumeFeedback)
        .options(joinedload(...))  # N+1 방지
        .where(...)
    )
    # Code 테이블 JOIN으로 코드값 매핑
    return ResumeFeedbackResponse.from_orm(feedback)

# 3. 스키마 검증 (schemas.py)
class ResumeFeedbackResponse(BaseModel):
    feedback_id: int
    matching_rate: int
    parent_content: str
    feedback_contents: List[FeedbackContentResponse]
```

#### 성능 최적화

- **N+1 쿼리 방지**: `joinedload` 사용으로 관계 한 번에 로드
- **Code 매핑 캐싱**: Redis에 캐싱하여 조회 성능 향상
- **비동기 처리**: 논블로킹 I/O로 동시 처리 최적화

---

### 6.2 채용 공고 관리 시스템

#### API 엔드포인트

| Method | Path | 기능 |
| --- | --- | --- |
| `POST` | `/job-postings/` | 공고 생성 |
| `GET` | `/job-postings/` | 목록 조회 (페이징, 검색) |
| `GET` | `/job-postings/{posting_id}` | 상세 조회 |
| `PUT` | `/job-postings/{posting_id}` | 수정 |
| `PATCH` | `/job-postings/{posting_id}` | 삭제 (소프트) |

#### 구현 위치

- **라우터**: app/routers/job_postings.py
- **로직**: app/util/posting_util.py

#### 페이징 처리

```python
async def get_job_postings(db, user_id, page=1, page_size=6, title=None):
    offset = (page - 1) * page_size

    search_condition = [
        DBJobPosting.user_id == user_id,
        DBJobPosting.is_active == True,
    ]
    if title:
        search_condition.append(DBJobPosting.title.ilike(f"%{title}%"))

    result = await db.execute(
        select(DBJobPosting)
        .where(*search_condition)
        .order_by(desc(DBJobPosting.created_at))
        .offset(offset)
        .limit(page_size)
    )
    return result.scalars().all()
```

---

## 7. 데이터베이스 설계

### 7.1 테이블 구조 (17개)

```
Users (사용자)
├─ Resumes (이력서)
│  ├─ ResumeFeedbacks (피드백)
│  │  └─ FeedbackContents (피드백 세부)
│  ├─ Experiences (경력)
│  ├─ Educations (학력)
│  ├─ Projects (프로젝트)
│  ├─ Activities (활동)
│  ├─ Qualifications (자격증)
│  ├─ TechnologyStacks (기술스택)
│  └─ Files (이미지)
├─ JobPostings (채용 공고)
│  └─ ResumeFeedbacks (공고별 피드백)
├─ Interviews (모의 면접)
│  ├─ Conversations (대화)
│  └─ InterviewFeedbacks (피드백)
├─ StudyGuides (학습 가이드)
│  ├─ StudyItems (학습항목)
│  └─ StudyKeywords (키워드)
└─ UserBlacklists (차단 목록)

코드 관리
├─ Codes (코드값 매핑)
└─ Files (S3 메타데이터)
```

### 7.2 핵심 모델 (ORM)

#### User 모델

```pythone
erd
```

### 7.3 Code 테이블 (코드 매핑)

```python
class Code(Base):
    __tablename__ = "codes"

    code_id: Integer = Column(primary_key=True)
    division: String(50)  # 분류 (gender, user_type, feedback_division)
    detail_id: String(50)  # 코드값
    code_detail: String(50)  # 설명
    order: Integer
```

**활용 예시:**

```python
# Code 테이블 데이터
division='feedback_division', detail_id='1', code_detail='잘된 부분'
division='feedback_division', detail_id='2', code_detail='개선 제안'
division='feedback_division', detail_id='3', code_detail='추가 권장사항'

# 쿼리
codes = await db.execute(
    select(Code).where(
        Code.division == "feedback_division",
        Code.detail_id.in_(feedback_divisions)
    )
)
code_map = {code.detail_id: code.code_detail for code in codes}
```

---

## 8. API 엔드포인트

### 8.1 인증 API

| Method | Path | 설명 |
| --- | --- | --- |
| `POST` | `/auth/google/callback` | Google OAuth 콜백 |
| `POST` | `/auth/refresh` | JWT 토큰 갱신 |
| `POST` | `/auth/logout` | 로그아웃 (토큰 블랙리스트) |

### 8.2 이력서 API

| Method | Path | 설명 |
| --- | --- | --- |
| `POST` | `/resumes/` | 이력서 생성 |
| `GET` | `/resumes/` | 이력서 목록 (페이징) |
| `GET` | `/resumes/{resume_id}` | 이력서 상세 |
| `PUT` | `/resumes/{resume_id}` | 이력서 수정 |
| `DELETE` | `/resumes/{resume_id}` | 이력서 삭제 |

**요청/응답 예시:**

```bash
# 이력서 생성
POST /resumes/
Content-Type: application/json

{
  "title": "2024 상반기 취업용 이력서",
  "name": "박영서",
  "email": "example@example.com",
  "resume_type": "1",
  "experiences": [...],
  "educations": [...],
  "technology_stacks": ["Python", "FastAPI", "PostgreSQL"]
}

# 응답
{
  "resume_id": 1,
  "user_id": "abc123xyz...",
  "title": "2024 상반기 취업용 이력서",
  "resume_type": "1",
  "created_at": "2024-11-17T12:00:00Z",
  ...
}
```

### 8.3 피드백 API

| Method | Path | 설명 |
| --- | --- | --- |
| `POST` | `/resume_feedbacks/standard/{resume_id}` | 일반 피드백 생성 |
| `POST` | `/resume_feedbacks/posting/{resume_id}/{posting_id}` | 공고별 피드백 생성 |
| `GET` | `/resume_feedbacks/{feedback_id}` | 피드백 조회 |
| `POST` | `/resume_feedbacks/standard_resume/{feedback_id}` | 개선 이력서 생성 |

### 8.4 공고 API

| Method | Path | 설명 |
| --- | --- | --- |
| `POST` | `/job-postings/` | 공고 생성 |
| `GET` | `/job-postings/?title=검색어&page=1&page_size=6` | 목록 조회 |
| `GET` | `/job-postings/{posting_id}` | 상세 조회 |
| `PUT` | `/job-postings/{posting_id}` | 공고 수정 |
| `PATCH` | `/job-postings/{posting_id}` | 공고 삭제 (소프트) |

---

## 9. 인증 및 보안

### 9.1 Google OAuth 2.0 플로우

```
1. 프론트엔드에서 Google 로그인
   ↓
2. Google OAuth 인증 코드 발급
   ↓
3. 백엔드 /auth/google/callback에 code 전송
   ↓
4. [security.py] Google API에서 액세스 토큰 교환
   ↓
5. Google API에서 사용자 정보 조회
   ↓
6. 기존 사용자 조회, 없으면 신규 생성
   ↓
7. [JWT 토큰 생성]
   ├─ access_token (15분 유효)
   └─ refresh_token (7일 유효)
   ↓
8. 토큰 반환
```

### 9.2 JWT 토큰 구조

```python
# 토큰 페이로드
{
  "user_id": "abc123xyz...",
  "email": "user@example.com",
  "name": "박영서",
  "exp": 1700200000,  # 만료 시간
}

# 토큰 저장
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### 9.3 의존성 주입으로 인증 처리

```python
async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    return user

# 라우터에서 사용
@router.post("/resume_feedbacks/standard/{resume_id}")
async def resume_feedback(
    resume_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    ...
```

---

## 10. 성능 최적화 및 캐싱


#### N+1 쿼리 방지

```python
# 나쁜 예: N+1 쿼리
for feedback in feedbacks:
    codes = await db.execute(...)  # 각각 쿼리 실행

# 좋은 예: joinedload
feedbacks = await db.execute(
    select(ResumeFeedback)
    .options(joinedload(ResumeFeedback.feedback_contents))
    .where(...)
)
```


### 10.3 비동기 처리

```python
async def create_feedback():
    resume_task = get_resume_response(...)
    posting_task = db.get(JobPosting, ...)

    resume, posting = await asyncio.gather(resume_task, posting_task)
    result = await resume_feedback_with_posting(resume, posting)
```

---

## 11. 개발 가이드

### 11.1 로컬 환경 설정

```bash
cp .env.example .env

# .env 파일 편집
DATABASE_URL=
REDIS_URL=
JWT_SECRET_KEY=
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
OPENAI_API_KEY=
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_S3_BUCKET_NAME=
AWS_REGION=
```

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

alembic upgrade head

uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 11.2 마이그레이션 관리

```bash
# 마이그레이션 파일 생성
alembic revision --autogenerate -m "설명"

# 최신 버전으로 업그레이드
alembic upgrade head

# 이전 버전으로 롤백
alembic downgrade -1

# 마이그레이션 히스토리 확인
alembic current  # 현재 버전
alembic history  # 히스토리
```


---

## 12. 배포 및 운영

### 12.1 Docker 기반 로컬 개발

```bash
# 개발 환경 (자동 리로드 활성화)
docker-compose -f docker-compose.dev.yml up --build

# 운영 환경
docker-compose up --build

# 백그라운드 실행
docker-compose up -d

# 로그 확인
docker-compose logs -f backend

# 컨테이너 중지
docker-compose down
```

### 12.2 AWS 배포

```bash
# Lightsail
git clone [repo]


# 추가 파일 생성
alembic.ini
.env

# 이미지 빌드 및 푸시
docker-compose up -d



## 13. 트러블슈팅 및 해결 사항

### 13.1 데이터 타입 불일치 문제

**문제:**
```python
feedback = await get_resume_feedback(...)  
resume = await get_resume_response(feedback.resume_id) 
# vs
resume = await get_resume_response(feedback['resume_id'])  
```

**해결:**
- Pydantic 모델은 ORM 객체처럼 `.속성` 접근
- 명확한 타입 힌트로 실수 방지

### 13.2 N+1 쿼리 문제

**문제:**
```python
feedbacks = await db.execute(select(ResumeFeedback))
for feedback in feedbacks:
    contents = await db.execute(...) 
```

**해결:**
```python
feedbacks = await db.execute(
    select(ResumeFeedback)
    .options(joinedload(ResumeFeedback.feedback_contents))  # ✅ 1번에 로드
)
```

### 13.3 소프트 삭제 처리

**문제:**
```python
# 기존 항목도 반환됨
items = await db.execute(select(Item))
```

**해결:**
```python
items = await db.execute(
    select(Item)
    .where(Item.is_active == True)
)
```

### 13.4 마이그레이션 충돌

**문제:**
```python
is_activate = Column(Boolean)  # 모델에는 is_active
# 마이그레이션 불일치
```

**해결:**
```bash
alembic revision --autogenerate -m "rename is_activate to is_active"
alembic upgrade head
```

---

