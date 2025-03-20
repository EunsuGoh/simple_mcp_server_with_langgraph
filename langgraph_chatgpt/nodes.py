# tool로써 tavily 웹검색 기능과 코드실행 기능을 가진 chatGPT 클라이언트 생성
# asyncio 임포트 추가
import asyncio
import os   
import dotenv

from server import get_tools
from langgraph.graph import MessagesState
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from datetime import datetime

dotenv.load_dotenv()

API_KEY = os.getenv('OPENAI_API_KEY')

# TODO : PART4 CH02 파이썬 파일 node.py / agent.py 검토 후 코드 작성
# llm모델 선언
llm = ChatOpenAI(
    model = "gpt-4o-mini",
    api_key=os.getenv("OPENAI_API_KEY")
)

# 시스템 프롬프트 함수
def get_system_prompt(docs_info=None):
    system_prompt = f"""
    Today is {datetime.now().strftime("%Y-%m-%d")}
    You are a helpful AI Assistant that can use web search tool(tavily ai api), 
    image generation tool(DallE API) and code execution tool(Python REPL).
    When you call image generation or data visualization tool, only answer the fact that you generated, not base64 code or url.
    Once you generated image by a tool, then do not call it again in one answer.
    """
    if docs_info:
        docs_context = "\n\nYou have access to these documents:\n"
        for doc in docs_info:
            docs_context += f"- {doc['name']}: {doc['type']}\n"
        system_prompt += docs_context
        
    system_prompt += "\nYou should always answer in same language as user's ask."
    return system_prompt

#챗봇생성 함수
def create_chatbot(docs_info=None, retriever_tool=None):
    prompt = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(get_system_prompt(docs_info)),
        HumanMessagePromptTemplate.from_template("{input}")
    ])
    
    # retriever_tool이 있을 경우 tools에 추가
    tools = get_tools(retriever_tool)
    llm_with_tools = llm.bind_tools(tools)
    chain = prompt | llm_with_tools
    
    def chatbot(state: MessagesState):
        response = chain.invoke(state["messages"])
        return {"messages": response}
    
    return chatbot