# GAECHWI - AI 기반 구인구직 및 취업 준비 통합 플랫폼 (백엔드 상세 문서)

**발표자:** 박영서, 김경환

---

## 목차

1. [프로젝트 소개](#1-프로젝트-소개)
2. [백엔드 팀 구성](#2-백엔드-팀-구성)
3. [시스템 아키텍처](#3-시스템-아키텍처)
4. [기술 스택](#4-기술-스택)
5. [프로젝트 구조](#5-프로젝트-구조)
6. [데이터베이스 설계](#6-데이터베이스-설계)
7. [핵심 기능](#7-핵심-기능)
8. [API 엔드포인트](#8-api-엔드포인트)
9. [인증 및 보안](#9-인증-및-보안)
10. [개발 가이드](#10-개발-가이드)
11. [배포 및 운영](#11-배포-및-운영)
12. [트러블슈팅 및 해결 사항](#12-트러블슈팅-및-해결-사항)

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
| **김경환** | 개발자 | 채용 공고 관리, DB 설계/구현, 유저 관리 |

---

## 3. 시스템 아키텍처

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

## 4. 기술 스택

| 분류 | 기술 | 용도 |
| --- | --- | --- |
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
| **File Storage** | Boto3 (Lightsail) | 파일 저장소 |
| **Validation** | Pydantic | 데이터 검증 |
| **Container** | Docker + Docker Compose | 컨테이너화 및 개발 환경 |

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
│   ├── versions/             # 마이그레이션 파일
│   └── script.py.mako
│
├── main.py                   # FastAPI 앱 진입점
├── requirements.txt          # Python 의존성
├── docker-compose.dev.yml    # 로컬 개발 환경
├── docker-compose.yml        # 운영 환경
├── Dockerfile               # 컨테이너 이미지
├── erd.mmd                  # ERD (Mermaid 형식)
├── .env.example             # 환경변수 템플릿
└── README.md                # 이 문서
```

---

## 6. 데이터베이스 설계

### 테이블 구조 (17개)

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
├─ Interviews (모의 면접)
│  ├─ Conversations (대화)
│  └─ InterviewFeedbacks (피드백)
├─ StudyGuides (학습 가이드)
├─ UserBlacklists (차단 목록)
└─ UserActivityLogs (활동 로그)

공통 테이블
├─ Codes (코드값 매핑)
└─ Files (S3 메타데이터)
```

### Code 테이블 (코드 매핑)

```python
class Code(Base):
    division: String(50)  # 분류 (gender, user_type, degree, etc.)
    detail_id: String(50) # 코드값
    code_detail: String(50) # 설명
```

**활용:**
```python
codes = await db.execute(
    select(Code).where(
        Code.division == "feedback_division",
        Code.detail_id.in_(feedback_divisions)
    )
)
code_map = {code.detail_id: code.code_detail for code in codes}
```

---

## 7. 핵심 기능

### 7.1 AI 기반 이력서 피드백 시스템

**데이터 흐름:**
```
사용자 이력서 입력
    ↓
[resume_feedback.py] POST /resume_feedbacks/standard/{resume_id}
    ↓
[resume_feedback_util.py] LangChain + OpenAI로 분석
    ↓
[resume_feedback.py] ResumeFeedback 객체 생성 및 DB 저장
    ↓
클라이언트에 JSON 반환
```

**성능 최적화:**
- `contains_eager` 사용으로 N+1 쿼리 방지
- Code 테이블 매핑으로 코드값 → 설명 변환
- 비동기 처리로 동시 처리 최적화

### 7.2 채용 공고 관리 시스템

| Method | Path | 기능 |
| --- | --- | --- |
| `POST` | `/job-postings/` | 공고 생성 |
| `GET` | `/job-postings/` | 목록 조회 (페이징, 검색) |
| `GET` | `/job-postings/{posting_id}` | 상세 조회 |
| `PUT` | `/job-postings/{posting_id}` | 수정 |
| `PATCH` | `/job-postings/{posting_id}` | 삭제 (소프트) |

---

## 8. API 엔드포인트

### 인증 API

| Method | Path | 설명 |
| --- | --- | --- |
| `POST` | `/auth/google/callback` | Google OAuth 콜백 |
| `POST` | `/auth/refresh` | JWT 토큰 갱신 |
| `POST` | `/auth/logout` | 로그아웃 |

### 이력서 API

| Method | Path | 설명 |
| --- | --- | --- |
| `POST` | `/resumes/` | 이력서 생성 |
| `GET` | `/resumes/` | 이력서 목록 (페이징) |
| `GET` | `/resumes/{resume_id}` | 이력서 상세 |
| `PUT` | `/resumes/{resume_id}` | 이력서 수정 |
| `DELETE` | `/resumes/{resume_id}` | 이력서 삭제 |

### 피드백 API

| Method | Path | 설명 |
| --- | --- | --- |
| `POST` | `/resume_feedbacks/standard/{resume_id}` | 일반 피드백 생성 |
| `POST` | `/resume_feedbacks/posting/{resume_id}/{posting_id}` | 공고별 피드백 생성 |
| `GET` | `/resume_feedbacks/{feedback_id}` | 피드백 조회 |
| `POST` | `/resume_feedbacks/standard_resume/{feedback_id}` | 개선 이력서 생성 |

---

## 9. 인증 및 보안

### Google OAuth 2.0 플로우

```
1. 프론트엔드에서 Google 로그인
   ↓
2. Google OAuth 인증 코드 발급
   ↓
3. 백엔드 /auth/google/callback에 code 전송
   ↓
4. Google API에서 액세스 토큰 교환
   ↓
5. Google API에서 사용자 정보 조회
   ↓
6. 기존 사용자 조회, 없으면 신규 생성
   ↓
7. JWT 토큰 생성 (access_token 15분, refresh_token 7일)
   ↓
8. 토큰 반환
```

### JWT 토큰 구조

```python
{
  "user_id": "abc123xyz...",
  "email": "user@example.com",
  "name": "박영서",
  "exp": 1700200000
}
```

### 의존성 주입으로 인증 처리

```python
@router.post("/resume_feedbacks/standard/{resume_id}")
async def resume_feedback(
    resume_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # current_user는 JWT에서 인증된 사용자
    ...
```

---

## 10. 개발 가이드

### 로컬 환경 설정

```bash
# 환경변수 파일 생성
cp .env.example .env

# 가상환경 및 의존성 설치
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 데이터베이스 마이그레이션
alembic upgrade head

# 개발 서버 실행
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 마이그레이션 관리

```bash
# 마이그레이션 파일 생성
alembic revision --autogenerate -m "설명"

# 최신 버전으로 업그레이드
alembic upgrade head

# 이전 버전으로 롤백
alembic downgrade -1

# 마이그레이션 히스토리 확인
alembic history
```

---

## 11. 배포 및 운영

### Docker Compose 기반 개발

```bash
# 개발 환경
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

### AWS Lightsail 배포

- Git repository clone
- `.env` 파일 설정
- Docker Compose로 배포
- Nginx 리버스 프록시 설정
- Let's Encrypt SSL/TLS 인증서 자동 갱신

---

## 12. 트러블슈팅 및 해결 사항

### 12.1 N+1 쿼리 문제 - contains_eager 성능 개선

**문제:** 이력서 상세 조회 시 관련 테이블 6개(경험, 교육, 프로젝트, 활동, 기술스택, 자격증) 조회로 1 + N × 6 형태의 쿼리 발생.

**원인:** ORM의 기본 동작인 Lazy Loading으로 인해 관계 데이터가 필요한 시점에 별도 쿼리 실행.

**해결책:**
```python
stmt = (
    select(Resume)
    .outerjoin(Resume.experiences)
    .outerjoin(Resume.educations)
    .options(
        contains_eager(Resume.experiences),
        contains_eager(Resume.educations),
    )
    .where(Resume.resume_id == resume_id)
)
result = await db.execute(stmt)
row = result.unique().first()  # 중복 제거
```

**핵심 포인트:**
- `outerjoin` + `contains_eager` 함께 사용 필수
- `result.unique()`로 JOIN 결과의 중복 행 제거
- 성능 개선: 1 + 60 쿼리 → 1 쿼리로 개선

---

### 12.2 AI 응답 데이터 구조 불일치 - LangChain 파싱 실패

**문제:** OpenAI API 응답이 Pydantic 스키마와 맞지 않아 필드 누락이나 타입 오류 발생.

**원인:** 프롬프트에 JSON 구조가 명확하게 명시되지 않아 LLM이 형식을 자유롭게 해석.

**해결책:**
```python
class ResumeFeedbackAI(BaseModel):
    matching_rate: int = Field(ge=0, le=100, description="매칭률")
    feedback_contents: List[dict] = Field(min_items=1, description="피드백 리스트")

chain = prompt | llm.with_structured_output(ResumeFeedbackAI)
result = await chain.ainvoke({"resume": data})
```

**핵심 포인트:**
- `with_structured_output()`으로 LLM 응답 자동 검증
- Field의 description과 제약 조건이 프롬프트에 자동 반영
- ValidationError 제거로 안정적인 파이프라인 구성

---
