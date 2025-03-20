from langgraph.graph import StateGraph, START, MessagesState
from nodes import create_chatbot
from server import get_tools
from langgraph.prebuilt import tools_condition
from langgraph.prebuilt import ToolNode
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_mcp_adapters.tools import load_mcp_tools
from langchain_mcp_adapters.client import MultiServerMCPClient


# stdio 윈도우 지원 이슈
# async def create_agent(docs_info=None, retriever_tool=None):
    
#     server_params = StdioServerParameters(
#         command="python",
#         args=["./server.py"]
#     )

#     async with stdio_client(server_params) as (read, write):
#         async with ClientSession(read,write) as session:
#             await session.initialize()
#             tools = await load_mcp_tools(session)
#             agent_builder = StateGraph(MessagesState)
    
#             # chatbot 노드 생성시 docs_info와 retriever_tool 전달
#             chatbot_node = create_chatbot(docs_info, retriever_tool)
#             agent_builder.add_node("chatbot", chatbot_node)
            
#             # tool_node도 여기서 생성
#             tool_node = ToolNode(tools=get_tools(retriever_tool))
#             agent_builder.add_node("tools", tool_node)
            
#             agent_builder.add_conditional_edges(
#                 "chatbot",
#                 tools_condition,
#             )
#             agent_builder.add_edge("tools", "chatbot")
#             agent_builder.add_edge(START, "chatbot")
#             agent = agent_builder.compile()
#             return agent

async def create_agent(docs_info=None, retriever_tool=None):
    async with MultiServerMCPClient(
        {
            "server":{
                "url":["http://localhost:8000/sse"],
                "transport":"sse"
            }
        }
    ) as client : 
        tools =client.get_tools()
        agent_builder = StateGraph(MessagesState)

        # chatbot 노드 생성시 docs_info와 retriever_tool 전달
        chatbot_node = create_chatbot(docs_info, retriever_tool)
        agent_builder.add_node("chatbot", chatbot_node)
        
        # tool_node도 여기서 생성
        tool_node = ToolNode(tools=tools(retriever_tool))
        agent_builder.add_node("tools", tool_node)
        
        agent_builder.add_conditional_edges(
            "chatbot",
            tools_condition,
        )
        agent_builder.add_edge("tools", "chatbot")
        agent_builder.add_edge(START, "chatbot")
        agent = agent_builder.compile()
        return agent
