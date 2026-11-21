# GAECHWI - AI 기반 구인구직 및 취업 준비 통합 플랫폼 (백엔드 상세 문서)

**발표자:** 박영서, 김경환

**프로젝트 페이지:**[https://park-yeongseo.github.io/frontend/](https://park-yeongseo.github.io/frontend/)  (로그인 화면의 **게스트로 체험하기**로 가입 없이 사용해 볼 수 있습니다)

**백엔드 API:**`https://gaechwi.duckdns.org` (AWS Lightsail, Docker Compose)

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

GAECHWI는 AI 기반 이력서 첨삭과 채용 공고별 맞춤 피드백을 제공하는 취업 준비 플랫폼입니다. 구직자가 이력서를 관리하고, 공고에 맞춰 개선할 수 있도록 지원합니다.

### 핵심 가치

* **자동화된 피드백**: OpenAI API를 활용한 고급 자연어 처리로 이력서 분석 및 개선 제안
* **채용 공고 연동**: 각 채용 공고별 맞춤형 피드백 제공

### 주요 기능

* 이력서 작성 및 관리 (CRUD)
* AI 기반 이력서 첨삭 및 매칭률 평가
* 채용 공고별 맞춤형 피드백
* 피드백을 반영한 개선 이력서 자동 생성
* 게스트 체험 (가입 없이 샘플 데이터로 사용, 24시간 후 자동 삭제)

**개발 예정:** AI 모의 면접, 직무별 학습 가이드

---

## 2. 백엔드 팀 구성


| 이름       | 역할             | 담당 영역                                             |
| ---------- | ---------------- | ----------------------------------------------------- |
| **박영서** | 아키텍트, 개발자 | DB 설계/구현, AI 통합, 이력서/피드백 로직, OAuth 인증 |
| **김경환** | 개발자           | 채용 공고 관리, DB 설계/구현, 유저 관리               |

---

## 3. 시스템 아키텍처

### 전체 시스템 흐름도

[아키텍처 구조도](https://claude.ai/chat/image/%EC%95%84%ED%82%A4%ED%85%8D%EC%B3%90%20%EA%B5%AC%EC%A1%B0%EB%8F%84.png)

### 레이어별 구성

```
┌─────────────────────────────────────────────┐
│  Router Layer (app/routers/)                │
│  - auth.py (Google OAuth, JWT, 게스트 로그인)│
│  - resumes.py (이력서 CRUD)                 │
│  - resume_feedback.py (AI 피드백)           │
│  - job_postings.py (공고 관리)              │
│  - users.py (사용자 정보)                   │
│  - dashboard.py (대시보드)                  │
└─────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────┐
│  Business Logic Layer (app/service/)        │
│  - resume_service.py (이력서 조회/생성)     │
│  - resume_feedback_service.py (AI 분석)     │
│  - posting_service.py (공고 로직)           │
│  - login_service.py (사용자 조회/생성)      │
│  - guest_service.py (게스트 계정/샘플 데이터)│
│  - storage_util/storage_util.py (S3 파일)   │
│  - security.py (JWT 생성/검증)              │
└─────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────┐
│  Data Access Layer                          │
│  - models/models.py (SQLAlchemy ORM 모델)   │
│  - database.py (async/sync 엔진 관리)       │
│  - schema/schemas.py (Pydantic 검증 스키마) │
└─────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────┐
│  External Services                          │
│  - OpenAI API (LangChain 기반 피드백)       │
│  - AWS Lightsail 버킷 (S3 호환 파일 저장소) │
│  - Google OAuth (인증)                      │
│  - PostgreSQL (데이터 저장)                 │
└─────────────────────────────────────────────┘
```

**아키텍처 특징:**

* **비동기 처리**: FastAPI + Uvicorn으로 높은 동시성 지원
* **이중 DB 엔진**: Alembic 마이그레이션용 동기 엔진, API용 비동기 엔진
* **계층 분리**: Router / Service / Data 계층 분리로 유지보수성 향상
* **외부 서비스 통합**: OAuth, AI, 클라우드 스토리지 통합

---

## 4. 기술 스택


| 분류              | 기술                 | 용도                      | 버전               |
| ----------------- | -------------------- | ------------------------- | ------------------ |
| **Framework**     | FastAPI              | 비동기 API 서버           | 최신               |
| **ASGI Server**   | Uvicorn              | 고성능 ASGI 서버          | 최신               |
| **Database**      | PostgreSQL           | 관계형 DB                 | 14+                |
| **ORM**           | SQLAlchemy           | 비동기 ORM                | 2.0+               |
| **Migration**     | Alembic              | 스키마 버전 관리          | 최신               |
| **AI/ML**         | LangChain            | 자연어 처리 프레임워크    | 최신               |
| **LLM**           | OpenAI (gpt-4o-mini) | 텍스트 생성 및 분석       | 설정으로 변경 가능 |
| **Auth**          | Python-jose          | JWT 토큰 생성/검증        | 최신               |
| **OAuth**         | Google Auth          | 소셜 로그인               | OAuth 2.0          |
| **File Storage**  | Boto3 (Lightsail)    | 클라우드 파일 저장소      | 최신               |
| **Validation**    | Pydantic             | 데이터 검증 및 직렬화     | 2.0+               |
| **Reverse Proxy** | Nginx + Certbot      | HTTPS(Let's Encrypt) 적용 | 최신               |
| **Container**     | Docker               | 컨테이너 이미지           | 최신               |
| **Orchestration** | Docker Compose       | 개발/운영 환경 구성       | 최신               |

---

## 5. 프로젝트 구조

```
Backend/
├── app/
│   ├── routers/              # API 엔드포인트 (라우트 정의)
│   │   ├── auth.py           # 인증 (Google OAuth, 회원가입, 게스트 로그인)
│   │   ├── resumes.py        # 이력서 CRUD
│   │   ├── resume_feedback.py# AI 피드백 생성/조회
│   │   ├── job_postings.py   # 채용 공고 관리
│   │   ├── users.py          # 사용자 정보
│   │   └── dashboard.py      # 대시보드
│   │
│   ├── service/              # 비즈니스 로직
│   │   ├── resume_service.py
│   │   ├── resume_feedback_service.py  # AI 분석 및 피드백 생성
│   │   ├── posting_service.py
│   │   ├── login_service.py
│   │   └── guest_service.py  # 게스트 계정, 샘플 데이터, 만료 계정 정리
│   │
│   ├── models/models.py      # SQLAlchemy ORM 정의
│   ├── schema/schemas.py     # Pydantic 검증 스키마 (요청/응답)
│   ├── storage_util/         # S3 파일 관리 및 검증
│   ├── security.py           # JWT 생성/검증
│   ├── ai.py                 # LLM 클라이언트 설정
│   ├── database.py           # 비동기/동기 DB 엔진 관리
│   └── config/
│       ├── settings.py       # 환경별 설정 로더
│       ├── base.py           # 공통 설정
│       ├── development.py    # 개발 환경 설정
│       └── production.py     # 운영 환경 설정
│
├── alembic/                  # 데이터베이스 마이그레이션
├── nginx_config/             # Nginx 설정
├── certbot/                  # HTTPS 인증서
├── main.py                   # FastAPI 앱 진입점
├── requirements.txt          # Python 의존성 목록
├── docker-compose.dev.yml    # 로컬 개발 환경 설정
├── docker-compose.yml        # 운영 환경 설정
├── Dockerfile                # 컨테이너 이미지 정의
├── erd.mmd                   # ERD (Mermaid 형식)
├── .env.example              # 환경변수 템플릿
└── README.md                 # 이 문서
```

---

## 6. 데이터베이스 설계

### 테이블 구조

```
Users (사용자 정보)
├─ Resumes (이력서)
│  ├─ ResumeFeedbacks (AI 피드백)
│  │  └─ FeedbackContents (피드백 세부 항목)
│  ├─ Experiences (경력 정보)
│  ├─ Educations (학력 정보)
│  ├─ Projects (프로젝트 경험)
│  ├─ Activities (대외활동)
│  ├─ Qualifications (자격증)
│  ├─ TechnologyStacks (기술 스택)
│  └─ Files (프로필 이미지)
├─ JobPostings (채용 공고)
├─ Interviews (모의 면접 세션, 개발 예정)
│  ├─ Conversations (대화 기록)
│  └─ InterviewFeedbacks (면접 피드백)
├─ StudyGuides (학습 가이드, 개발 예정)
├─ UserBlacklists (사용자 차단 목록)
└─ UserActivityLogs (활동 로그)

공통 테이블
├─ Codes (코드값 매핑 - 성별, 직급, 학위 등)
└─ Files (S3 메타데이터)
```

### ERD (Entity-Relationship Diagram)

[Database ERD](https://claude.ai/chat/image/erd.png)

### Code 테이블 (코드 매핑 패턴)

```python
class Code(Base):
    __tablename__ = "codes"

    code_id: int = Column(Integer, primary_key=True)
    division: str = Column(String(50))  # 분류 (gender, user_type, degree, feedback_division, military)
    detail_id: str = Column(String(50)) # 코드값 (1, 2, 3...)
    code_detail: str = Column(String(50)) # 설명 (남성, 여성...)
    order: int = Column(Integer)
```

**활용 예시:**

```python
# 피드백 분류 코드 조회
codes = await db.execute(
    select(Code).where(
        Code.division == "feedback_division",
        Code.detail_id.in_(["1", "2", "3"])
    )
)
code_map = {code.detail_id: code.code_detail for code in codes.scalars().all()}

# 결과: {"1": "잘된 부분", "2": "개선 제안", "3": "추가 권장사항"}
```

**특징:**

* 열거형 데이터를 테이블로 관리하여 확장성 확보
* 프론트엔드와 백엔드 간 공통 코드 참조
* 런타임에 코드 값을 변경 가능 (DB 수정만으로 UI 변경)

---

## 7. 핵심 기능

### 7.1 AI 기반 이력서 피드백 시스템

**데이터 흐름:**

```
1. 사용자가 이력서 작성 및 제출
   ↓
2. [resume_feedback.py] POST /resume_feedbacks/stantard/{resume_id}
   ↓
3. [resume_feedback_service.py] 이력서 데이터 조회 및 전처리
   ↓
4. LangChain + OpenAI API로 분석
   ├─ Pydantic 구조화된 출력으로 JSON 형식 강제
   ├─ matching_rate (0-100) 계산
   └─ 피드백 내용 자동 분류 (잘된 부분, 개선 제안, 추가 권장사항)
   ↓
5. [resume_feedback.py] ResumeFeedback 객체 생성
   ├─ DB에 피드백 저장 (ResumeFeedback 테이블)
   ├─ 세부 내용 저장 (FeedbackContent 테이블)
   └─ Code 테이블 JOIN으로 분류명 매핑
   ↓
6. [resume_feedback_service.py] 피드백 조회 및 변환
   ├─ contains_eager로 관계 데이터 한 번에 로드
   ├─ Code 매핑으로 코드값을 사람이 읽을 수 있는 형식으로 변환
   └─ ResumeFeedbackResponse로 변환
   ↓
7. 클라이언트에 JSON 응답 반환
```

**성능 최적화:**

* `contains_eager` + `outerjoin` 사용으로 N+1 쿼리 문제 해결
* Code 테이블 매핑으로 중복 조회 방지
* 비동기 처리로 동시 요청 최적화

### 7.2 채용 공고 관리 시스템

**주요 API:**


| Method  | Path                         | 기능          | 설명                               |
| ------- | ---------------------------- | ------------- | ---------------------------------- |
| `POST`  | `/job-postings/`             | 공고 생성     | 채용담당자가 채용 공고 등록        |
| `GET`   | `/job-postings/`             | 목록 조회     | 페이징 및 제목 검색 지원 |
| `GET`   | `/job-postings/{posting_id}` | 상세 조회     | 공고 상세 정보 및 요구사항 확인    |
| `PUT`   | `/job-postings/{posting_id}` | 수정          | 공고 정보 수정                     |
| `PATCH` | `/job-postings/{posting_id}` | 삭제 (소프트) | 공고 숨김 처리 (is\_active=False)  |

**특징:**

* 소프트 삭제: 데이터 완전 삭제 없이 is\_active 플래그로 상태 관리
* 페이징: page=1, page\_size=6 형식으로 효율적인 데이터 로드
* 제목 검색: 제목에 검색어가 포함된 공고 조회

---

## 8. API 엔드포인트

### 인증 API


| Method | Path                     | 설명                                              | 요청 예시                           |
| ------ | ------------------------ | ------------------------------------------------- | ----------------------------------- |
| `POST` | `/auth/google`           | Google OAuth 로그인                               | `{"code": "auth_code_from_google"}` |
| `POST` | `/auth/google/localhost` | Google OAuth 로그인 (로컬 개발용)                 | `{"code": "auth_code_from_google"}` |
| `POST` | `/auth/signup`           | 이메일 회원가입                                   | 사용자 정보                         |
| `POST` | `/auth/activate`         | 탈퇴 사용자 복구                                  | 사용자 식별 정보                    |
| `POST` | `/auth/guest`            | 게스트 로그인 (샘플 데이터가 담긴 임시 계정 발급) | 없음                                |

### 이력서 API


| Method  | Path                   | 설명                 | 상태   |
| ------- | ---------------------- | -------------------- | ------ |
| `POST`  | `/resumes`             | 이력서 생성          | 구현됨 |
| `GET`   | `/resumes/`            | 이력서 목록          | 구현됨 |
| `GET`   | `/resumes/{resume_id}` | 이력서 상세          | 구현됨 |
| `PUT`   | `/resumes/{resume_id}` | 이력서 수정          | 구현됨 |
| `PATCH` | `/resumes/{resume_id}` | 이력서 삭제 (소프트) | 구현됨 |

**이력서 생성 요청 예시:**

```json
{
  "title": "2024 상반기 취업용 이력서",
  "name": "박영서",
  "email": "example@example.com",
  "phone": "010-xxxx-xxxx",
  "birth_date": "1999-01-15",
  "address": "서울시 강남구",
  "resume_type": "1",
  "experiences": [
    {
      "company_name": "ABC 회사",
      "position": "인턴 개발자",
      "start_date": "2023-01-01",
      "end_date": "2023-06-30",
      "description": "백엔드 개발 담당"
    }
  ],
  "educations": [
    {
      "school_name": "OO 대학교",
      "major": "컴퓨터공학",
      "degree_level": "1",
      "start_date": "2019-03-01"
    }
  ],
  "technology_stacks": ["Python", "FastAPI", "PostgreSQL"]
}
```

### 피드백 API


| Method   | Path                                                 | 설명                       | 기능                                    |
| -------- | ---------------------------------------------------- | -------------------------- | --------------------------------------- |
| `POST`   | `/resume_feedbacks/stantard/{resume_id}`             | 일반 피드백 생성           | 이력서 일반 분석 (공고 무관)            |
| `POST`   | `/resume_feedbacks/posting/{resume_id}/{posting_id}` | 공고별 피드백 생성         | 특정 공고에 맞춘 맞춤형 분석            |
| `POST`   | `/resume_feedbacks/standard_resume/{feedback_id}`    | 개선 이력서 생성           | 일반 피드백을 반영한 이력서 자동 생성   |
| `POST`   | `/resume_feedbacks/posting_resume/{feedback_id}`     | 공고 맞춤 개선 이력서 생성 | 공고별 피드백을 반영한 이력서 자동 생성 |
| `GET`    | `/resume_feedbacks/`                                 | 피드백 목록 조회           | 생성한 피드백 목록                      |
| `GET`    | `/resume_feedbacks/content/{feedback_id}`            | 피드백 상세 조회           | 이전에 생성한 피드백 조회               |
| `DELETE` | `/resume_feedbacks/{feedback_id}`                    | 피드백 삭제                | 피드백 삭제                             |

---

## 9. 인증 및 보안

### Google OAuth 2.0 플로우

```
1. 프론트엔드에서 Google 로그인 버튼 클릭
   ↓
2. Google에서 인증 코드 발급 (프론트엔드 /googleCallback 으로 리다이렉트)
   ↓
3. 프론트엔드가 코드를 백엔드 /auth/google 에 전송
   ↓
4. Google 토큰 엔드포인트에서 액세스 토큰으로 교환
   └─ 요청: code + client_id + client_secret + redirect_uri
   ↓
5. Google UserInfo API에서 사용자 정보 조회
   └─ 응답: email, name, picture, provider_id
   ↓
6. [login_service.py] 기존 사용자 조회
   ├─ OAuth 제공자 + ID로 기존 사용자 검색
   ├─ 없으면 이메일로 다시 검색
   └─ 여전히 없으면 신규 사용자
   ↓
7. [security.py] JWT 액세스 토큰 생성
   ↓
8. 클라이언트에 토큰 반환
   ├─ 신규 사용자: is_new_user=true
   ├─ 비활성 사용자: is_active=false
   └─ 활성 사용자: access_token 포함
```

### 게스트 로그인

```
1. 로그인 화면에서 "게스트로 체험하기" 클릭
   ↓
2. POST /auth/guest
   ├─ 24시간이 지난 게스트 계정과 S3 파일 정리
   ├─ 게스트 계정 수 제한 확인 (최대 100개)
   └─ 방문마다 새 게스트 계정 생성
   ↓
3. [guest_service.py] 샘플 데이터 생성
   └─ 공고, 이력서(프로필 사진 포함), 피드백 등
   ↓
4. JWT 액세스 토큰 발급
```

* 계정을 방문자마다 따로 만들어서 다른 방문자의 데이터와 섞이지 않습니다.
* 게스트 계정은 `guest` 제공자로 구분하며, DB의 `ON DELETE CASCADE`로 관련 데이터가 함께 삭제됩니다.

### JWT 토큰 구조

```python
# 토큰 페이로드
{
  "sub": "abc123xyz...",   # 사용자 고유 ID (unique_id)
  "exp": 1700200000        # 만료 시간 (Unix timestamp)
}

# HTTP 헤더에 전송
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### 의존성 주입으로 인증 처리

```python
async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    """
    JWT 토큰을 검증하고 현재 사용자 반환
    - 토큰이 유효하지 않으면 401 Unauthorized 반환
    - 토큰이 유효하면 sub(unique_id)로 User 조회
    """
    payload = verify_token(token)
    ...

# 라우터에서 사용
@router.get("/resumes/")
async def list_resumes(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),  # 자동 인증 확인
):
    ...
```

**보안 기능:**

* HTTPS: Nginx + Let's Encrypt 인증서 적용
* JWT 기반 인증, 만료 시간 설정
* 소프트 삭제: 탈퇴·삭제 시 `is_active` 플래그로 관리

**개선 예정:** 로그아웃 시 토큰 블랙리스트(Redis), CORS 허용 도메인 제한

---

## 10. 개발 가이드

### 로컬 환경 설정

```bash
# 1단계: 환경변수 파일 생성
cp .env.example .env

# 2단계: .env 파일에 .env.example 의 항목을 채웁니다
# ENVIRONMENT, DATABASE_URL, DB_*, REDIS_*, JWT_SECRET, JWT_ALGORITHM,
# ACCESS_TOKEN_EXPIRE_MINUTES, OPENAI_API_KEY, AWS_*, GOOGLE_CLIENT_ID/SECRET,
# FRONT_END_DOMAIN 등

# 3단계: 가상환경 생성 및 의존성 설치
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 4단계: 데이터베이스 마이그레이션
alembic upgrade head

# 5단계: 개발 서버 실행
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# 6단계: API 문서 확인
# Swagger UI: http://localhost:8000/docs
# ReDoc: http://localhost:8000/redoc
```

### 마이그레이션 관리

```bash
# 마이그레이션 파일 생성 (자동 감지)
alembic revision --autogenerate -m "add favorite_field to resumes"

# 생성된 마이그레이션 파일 검토 후 수정
# 파일: alembic/versions/xxxx_add_favorite_field_to_resumes.py

# 최신 버전으로 업그레이드
alembic upgrade head

# 특정 버전으로 업그레이드
alembic upgrade 72361d77de7e

# 이전 버전으로 롤백
alembic downgrade -1

# 마이그레이션 히스토리 확인
alembic history

# 현재 DB 버전 확인
alembic current
```

**마이그레이션 팁:**

* 스키마 변경 전에 항상 마이그레이션 생성
* `alembic upgrade head` 후 테스트 데이터로 검증
* 롤백 테스트: `downgrade -1` → `upgrade head` 반복 확인
* 팀 협업 시 마이그레이션 충돌 주의 (merge 커밋 권장)

---

## 11. 배포 및 운영

### Docker Compose 기반 로컬 개발

```bash
# 개발 환경 (자동 리로드, 디버그 모드)
docker-compose -f docker-compose.dev.yml up --build

# 운영 환경 시뮬레이션
docker-compose up --build

# 백그라운드 실행
docker-compose up -d

# 로그 확인
docker-compose logs -f backend

# 특정 서비스 로그만 확인
docker-compose logs -f db

# 컨테이너 중지
docker-compose down

# 볼륨까지 제거 (완전 초기화)
docker-compose down -v
```

### AWS Lightsail 배포 절차

1. **사전 준비**
   ```bash
   git clone https://github.com/moduFinalProject/Backend.git
   cd Backend
   ```
2. **환경 설정**
   ```bash
   # .env 파일 생성 (프로덕션 환경변수 설정)
   cp .env.example .env
   nano .env  # 프로덕션 값 입력
   ```
3. **Docker로 배포**
   ```bash
   docker-compose up -d
   ```
4. **Nginx 설정**
   * SSL/TLS 인증서 설정 (Let's Encrypt)
   * 리버스 프록시 설정
   * HSTS 헤더 추가
5. **자동 갱신**
   * Certbot으로 인증서 자동 갱신 (12시간마다)
   * Nginx 자동 리로드 (6시간마다)

**배포 모니터링:**

```bash
# 운영 서버 로그 확인
docker-compose logs -f backend

# 컨테이너 상태 확인
docker ps

# 데이터베이스 상태 확인
docker-compose exec db psql -U <DB_USER> -d <DB_NAME> -c "SELECT version();"
```

---

## 12. 트러블슈팅 및 해결 사항

### 12.1 N+1 쿼리 문제 - contains\_eager 성능 개선

**문제:** 이력서 상세 조회 시 관련 테이블 6개(경험, 교육, 프로젝트, 활동, 기술스택, 자격증) 조회로 1 + N × 6 형태의 쿼리 발생.

**증상:**

* 이력서 1개 조회: 7개 쿼리 (1 + 6)
* 이력서 10개 조회: 61개 쿼리 (1 + 60)

**원인:** ORM의 기본 동작인 Lazy Loading으로 인해 관계 데이터가 필요한 시점에 별도 쿼리 실행.

```python
# ❌ 나쁜 예: N+1 쿼리 발생
resume = await db.get(Resume, resume_id)
for experience in resume.experiences:  # 추가 쿼리 발생!
    print(experience.company_name)
```

**해결책:**`contains_eager` + `outerjoin`으로 한 번에 로드

```python
stmt = (
    select(Resume)
    .outerjoin(Resume.experiences)
    .outerjoin(Resume.educations)
    .outerjoin(Resume.projects)
    .outerjoin(Resume.activities)
    .outerjoin(Resume.technology_stacks)
    .outerjoin(Resume.qualifications)
    .options(
        contains_eager(Resume.experiences),
        contains_eager(Resume.educations),
        contains_eager(Resume.projects),
        contains_eager(Resume.activities),
        contains_eager(Resume.technology_stacks),
        contains_eager(Resume.qualifications),
    )
    .where(Resume.resume_id == resume_id)
)
result = await db.execute(stmt)
row = result.unique().first()  # 중복 행 제거 필수!
resume = row[0]
```

**핵심 포인트:**

* `outerjoin` + `contains_eager` 함께 사용 필수 (selectinload는 별도 쿼리 사용)
* `result.unique()`로 JOIN 결과의 중복 행 제거 (다대다 관계에서 중복 발생)
* 여러 관계를 한 번에 로드하면 네트워크 왕복 횟수 급감
* **개선 결과: 관계 데이터를 JOIN으로 한 번에 불러와 N+1 쿼리 문제를 해결** (학위 코드 매핑은 별도 조회)

---

### 12.2 AI 응답 데이터 구조 불일치 - LangChain 파싱 실패

**문제:** OpenAI API 응답이 Pydantic 스키마와 맞지 않아 필드 누락이나 타입 오류 발생.

**증상:**

```
ValidationError: 1 validation error for ResumeFeedbackAI
feedback_contents
  Field required (type=value_error.missing)
```

**원인:** 프롬프트에 JSON 구조가 명확하게 명시되지 않아 LLM이 형식을 자유롭게 해석.

```python
# ❌ 문제 있는 코드
chain = prompt | llm  # 구조 강제 없음
result = await chain.ainvoke({"resume": data})
# LLM이 자유로운 형식으로 응답 → 파싱 실패
```

**해결책:** LangChain의 `with_structured_output()`으로 JSON 구조 강제

```python
class ResumeFeedbackAI(BaseModel):
    """이력서 피드백 데이터 모델"""
    matching_rate: int = Field(
        ge=0, le=100,
        description="매칭률 (0~100 사이의 정수)"
    )
    feedback_contents: List[dict] = Field(
        min_items=1,
        description="피드백 내용 리스트 (최소 1개 이상)"
    )

# ✅ 올바른 코드
chain = prompt | llm.with_structured_output(ResumeFeedbackAI)
result = await chain.ainvoke({"resume": data})
# LLM이 반드시 ResumeFeedbackAI 스키마 형식으로 응답
```

**동작 원리:**

1. Pydantic 스키마의 필드 정의 추출
2. JSON Schema로 변환
3. 프롬프트에 자동으로 JSON 형식 지시 추가
4. LLM이 반드시 해당 형식으로 응답하도록 강제
5. 응답 자동 검증 및 파싱

**핵심 포인트:**

* `with_structured_output()`은 LLM API의 기본 기능 활용 (OpenAI, Claude 등)
* Field의 description이 LLM이 실제로 따르는 지시사항
* `ge=0, le=100` 같은 제약 조건이 프롬프트에 자동 반영
* ValidationError 제거로 안정적인 파이프라인 구성
* **개선 결과: 응답 형식 오류로 인한 ValidationError 해소**

---

## 추가 자료

### 아키텍처 구조도

![아키텍처 구조도](./image/아키텍쳐%20구조도.png)[

### 데이터베이스 ERD

![Database ERD](./image/erd.png)

---
