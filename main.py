from fastapi import FastAPI
from app.config.settings import settings
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth
from app.routers import job_postings
from app.routers import auth, job_postings, resumes


app = FastAPI(title="AI 구인구직 플랫폼")

@app.get("/healthy")
def health_check():
    return {"hello": "world"}



app = FastAPI(
    title=settings.app_name,
    description=settings.description if settings.debug else None,
    debug=settings.debug,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://gaechwi.duckdns.org",
        "http://localhost:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)




app.include_router(auth.router)
app.include_router(job_postings.router)
app.include_router(resumes.router)