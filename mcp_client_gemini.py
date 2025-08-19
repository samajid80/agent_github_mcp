import asyncio
import os
from dotenv import load_dotenv
from openai import AsyncOpenAI
from agents import (
    Agent,
    Runner,
    set_default_openai_api,
    set_default_openai_client,
    set_tracing_disabled,
    set_tracing_export_api_key
)
from agents.mcp import MCPServerStreamableHttp, MCPServerStreamableHttpParams, ToolFilter,  ToolFilterStatic

load_dotenv()
BASE_URL = os.getenv("BASE_URL")
API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = "gemini-2.5-pro"
GITHUB_PAT = os.getenv("GITHUB_PAT")
GITHUB_MCP_URL = os.getenv("GITHUB_MCP_URL")
TRACING_KEY = os.getenv("OPENAI_API_KEY")

client = AsyncOpenAI(
    base_url=BASE_URL,
    api_key=API_KEY,
)
set_default_openai_client(client=client, use_for_tracing=False)
set_default_openai_api("chat_completions")
# set_tracing_disabled(disabled=True)
set_tracing_export_api_key(TRACING_KEY)


async def main():
   # Define parameters for the GitHub MCP server (assumed to be remotely hosted)
    github_mcp_params = MCPServerStreamableHttpParams(
        url=GITHUB_MCP_URL,  # Replace with actual GitHub MCP server URL
        headers={"Authorization": GITHUB_PAT},  # Replace with actual token
        timeout=10,  # HTTP request timeout in seconds
        sse_read_timeout=300,  # Streamable HTTP connection timeout (5 minutes)
        terminate_on_close=True
    )
    github_mcp_server = MCPServerStreamableHttp(
        name="Github MCP Server",
        params=github_mcp_params,
        cache_tools_list=True,  # Cache tools list to reduce latency
        client_session_timeout_seconds=5,
        use_structured_content=False,
          # Use structured content if server supports it
        tool_filter=ToolFilterStatic(
        allowed_tool_names=["get_me", "search_repositories"],
        )
    )
    # Create an agent

    async with github_mcp_server:   
        agent = Agent(
        name="Github MCP Agent With Gemini",
        instructions="Handle user queries related to GitHub by using tools from the GitHub MCP server.",
        mcp_servers=[github_mcp_server],
        model=MODEL_NAME,
        )
        result = await Runner.run(
            agent,
            "First get my github username and then list my owned 1 repos related to python only names using search_repositories tool?",
        )
        print(result.final_output)
    
    await asyncio.sleep(2)
    
    

asyncio.run(main())