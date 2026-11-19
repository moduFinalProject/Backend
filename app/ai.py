from langchain_openai import ChatOpenAI
from app.config.settings import settings


llm = ChatOpenAI(
    api_key=settings.openai_api_key,
    model=settings.ai_model,
    temperature=settings.temperature,
)