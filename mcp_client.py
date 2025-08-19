from agents import Agent, Runner, SQLiteSession
from agents.mcp import MCPServerStreamableHttp, MCPServerStreamableHttpParams, ToolFilterStatic
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

GITHUB_PAT = os.getenv("GITHUB_PAT")
GITHUB_MCP_URL = os.getenv("GITHUB_MCP_URL")



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
    
    async with github_mcp_server:   
        try:

            agent = Agent(
            name="Github MCP Agent",
            instructions="Handle user queries related to GitHub by using tools from the GitHub MCP server.",
            mcp_servers=[github_mcp_server],
            model="gpt-4o"
            )
            while True:
                user_input = input("Enter Your query or type 'exit' or 'quit' to quit.\n> ")
                if user_input.lower() in ['exit', 'quit']:
                    break

                result = await Runner.run(
                    agent,
                    user_input,
                    # session=session,
                )
                print(result.final_output, "\n\n")
        except Exception as e:
            print(f"Error occurred: {e}")
            
        print("Exiting Program...")
        await asyncio.sleep(2)
    
    

asyncio.run(main())