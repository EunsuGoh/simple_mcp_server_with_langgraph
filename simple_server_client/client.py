# asyncio 임포트 추가
import asyncio
import os   
import dotenv
dotenv.load_dotenv()
API_KEY = os.getenv('OPENAI_API_KEY')

# 기존 코드를 async 함수로 감싸기
async def main():
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
    from langchain_mcp_adapters.tools import load_mcp_tools
    from langgraph.prebuilt import create_react_agent
    from langchain_openai import ChatOpenAI
    
    model = ChatOpenAI(model="gpt-4o", api_key=API_KEY)
    
    server_params = StdioServerParameters(
        command="python",
        args=["./math_server.py"],
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await load_mcp_tools(session)
            agent = create_react_agent(model, tools)
            agent_response = await agent.ainvoke({"messages": "what's (3 + 5) x 12?"})
            print(agent_response)  # 결과 출력 추가

# async 메인 함수 실행
asyncio.run(main())
