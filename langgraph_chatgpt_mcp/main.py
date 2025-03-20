from langchain_core.messages import AIMessage
import streamlit as st
import requests
from io import BytesIO
from PIL import Image
import base64
from agent import create_agent
import asyncio



# async def invoke_our_graph(state, graph):
#     final_text = ""
#     async for event in graph.astream_events(state):
        

async def main():
    agent = await create_agent()
    # print(agent)
    result = agent.invoke({"messages":"can you make a image about a snow white?"})
    print(result)


asyncio.run(main())