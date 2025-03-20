# define tools
from mcp.server.fastmcp import FastMCP
from langchain_core.tools import tool
from langchain_experimental.utilities import PythonREPL
from langchain_community.tools.tavily_search import TavilySearchResults
import io
import base64
import matplotlib.pyplot as plt
from openai import OpenAI
from pydantic import BaseModel, Field
import os
from dotenv import load_dotenv
from langchain_core.tools import tool
import asyncio
load_dotenv()


mcp = FastMCP("Server")

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class GenImageSchema(BaseModel):
    prompt: str = Field(description="The prompt for image generation")

# @tool(args_schema=GenImageSchema)
@mcp.tool()
async def generate_image(prompt: str) -> str:
    """
    Generate an image using DALL-E based on the given prompt.
    """
    if not isinstance(prompt, str) or not prompt.strip():
        raise ValueError("Invalid prompt")
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    response = await loop.run_in_executor (None, lambda : client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size="1024x1024",
        quality="standard",
        n=1
    ))
    return f"Successfuly generated the image!,{response.data[0].url}"

repl = PythonREPL()

@mcp.tool()
def data_visualization(code: str):
    """Execute Python code. Use matplotlib for visualization."""
    try:
        repl.run(code)
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        img_str = base64.b64encode(buf.getvalue()).decode()
        return f"data:image/png;base64,{img_str}"
    except Exception as e:
        return f"Error creating chart: {str(e)}"
        
@mcp.tool()
def python_repl(code: str):
    """Execute Python code."""
    return repl.run(code)

search = TavilySearchResults(max_results=2)

def get_tools(retriever_tool=None):
    base_tools = [generate_image, search, python_repl, data_visualization]
    if retriever_tool:
        base_tools.append(retriever_tool)
    return base_tools

if __name__ == "__main__":
    mcp.run(transport="sse")
