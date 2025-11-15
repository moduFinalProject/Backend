from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from app.config.settings import settings
from app.schemas import ResumeFeedbackAI


llm = ChatOpenAI(api_key=settings.openai_api_key, model=settings.ai_model, temperature=settings.temperature)


async def resume_standard_feedback(resume: dict)-> ResumeFeedbackAI:
    '''일반 이력서 첨삭'''
    
    prompt = ChatPromptTemplate([
        ("system","당신은 전직 한 회사의 인사과 팀장이자 이력서 첨삭 전문가 입니다. 이력서 정보를 받고 회사에 취업할 수 있도록 이력서를 피드백 해주세요, 단 사실에 근거해야 합니다. 매칭률은 0으로 출력하시오.parent_content는 이력서의 내용을 md 형식의 text로 정리하세요"),
        ("user","{resume}")
    ])
    
    chain = prompt | llm.with_structured_output(ResumeFeedbackAI)
    
    result = chain.invoke({"resume":resume})
    
    
    return result
    


async def resume_feedback_with_posting(resume: dict, posting: dict)-> ResumeFeedbackAI:
    '''공고별 이력서 첨삭'''
    
    prompt = ChatPromptTemplate([
        ("system",'''당신은 전직 {company} 회사의 인사과 팀장이자 이력서 첨삭 전문가 입니다. 이력서와 공고 정보를 받고 해당 회사에 취업할 수 있도록 이력서를 피드백 해주세요,
         단 사실에 근거해야 합니다. parent_content는 이력서의 내용을 md 형식의 text로 정리하세요. 피드백 내용은 구체적으로 적어주세요'''),
        ("user","{resume}, {posting}")
    ])
    
    chain = prompt | llm.with_structured_output(ResumeFeedbackAI)
    
    result = chain.invoke({"company":posting.get("company"),"resume":resume, "posting":posting})
    
    
    return result



