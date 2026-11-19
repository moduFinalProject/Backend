from app.config.settings import settings
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import RedisChatMessageHistory
from langchain_core.messages import AIMessage, HumanMessage
from ai import llm

redis_url = f"redis://{settings.redis_host}:{settings.redis_port}"


async def get_redis_session_history(session_id: int):
    """대화 히스토리 저장 조회"""

    return RedisChatMessageHistory(
        session_id=session_id, url=redis_url, ttl=settings.history_ttl
    )


async def create_chain_with_history():
    """인터뷰 체인 생성"""

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """당신은 {company} 회사의 면접관 입니다. 이력서와 공고를 기반으로 면접을 진행해 주세요
                
        - 한 번에 한 가지 질문만 하세요
        - 구체적이고 명확한 질문을 하세요
        - 필요시 지원자의 답변을 바탕으로 심화 질문(꼬리 질문)을 하세요 
        
        구인 공고 : {posting}
        이력서 : {resume}
        """,
            ),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{input}"),
        ]
    )

    chain = prompt | llm

    with_message_history = RunnableWithMessageHistory(
        chain,
        get_redis_session_history,
        input_messages_key="input",
        history_messages_key="history",
    )

    return with_message_history


async def generate_feedback(question: str, answer: str):
    """답변 피드백"""

    prompt = f"""다음은 면접 질문과 지원자의 답변입니다.

질문: {question}
답변: {answer}

위 답변에 대한 구체적인 피드백을 작성해주세요:
1. 좋았던 점
2. 개선이 필요한 점
3. 추천하는 답변 방향

피드백은 건설적이고 구체적으로 작성해주세요.
"""
    response = await llm.ainvoke(prompt)

    return response.content

