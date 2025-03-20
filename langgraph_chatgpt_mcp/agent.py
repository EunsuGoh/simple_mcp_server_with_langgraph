from langgraph.graph import StateGraph, START, MessagesState
from nodes import create_chatbot
from langgraph.prebuilt import tools_condition
from langgraph.prebuilt import ToolNode
from langgraph.graph import MessagesState
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from datetime import datetime
import os
import dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient
import asyncio

dotenv.load_dotenv()


llm = ChatOpenAI(
    model="gpt-4o", 
    api_key=os.getenv("OPENAI_API_KEY"))

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


def create_chatbot(docs_info=None, retriever_tool=None):
    prompt = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(get_system_prompt(docs_info)),
        HumanMessagePromptTemplate.from_template("{input}")
    ])
    
    # retriever_tool이 있을 경우 tools에 추가
    llm_with_tools = llm.bind_tools(retriever_tool)
    chain = prompt | llm_with_tools
    
    def chatbot(state: MessagesState):
        response = chain.invoke(state["messages"])
        return {"messages": response}
    
    return chatbot

async def create_agent(docs_info=None):
    async with MultiServerMCPClient(
        {
            "server":{
                "url":"http://localhost:8000/sse",
                "transport":"sse"
            }
        }
    ) as client:
        graph_builder = StateGraph(MessagesState)
        
        # chatbot 노드 생성시 docs_info와 retriever_tool 전달
        chatbot_node = create_chatbot(docs_info, client.get_tools())
        graph_builder.add_node("chatbot", chatbot_node)
        
        # tool_node도 여기서 생성
        tool_node = ToolNode(tools=client.get_tools())
        graph_builder.add_node("tools", tool_node)
        
        graph_builder.add_conditional_edges(
            "chatbot",
            tools_condition,
        )
        graph_builder.add_edge("tools", "chatbot")
        graph_builder.add_edge(START, "chatbot")
        graph = graph_builder.compile()
        return graph