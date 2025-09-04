import os
from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters, types
from mcp.client.stdio import stdio_client
import asyncio
import google.generativeai as genai
from concurrent.futures import TimeoutError
from functools import partial

from fastapi import FastAPI, WebSocket, WebSocketDisconnect

from pydantic import BaseModel
#from gmail_utils import fetch_emails_from_query
from gemini_agent import get_details_from_email_body,build_gmail_search_query, summarize_emails_with_query,get_total_expenses_from_emails_with_query,Replace_total_expenses_from_emails_with_query

import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from datetime import datetime, timedelta

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

# Load environment variables from .env file
load_dotenv()

# Access your API key and initialize Gemini client correctly
api_key = os.getenv("GEMINI_API_KEY")
#client = genai.Client(api_key=api_key)
genai.configure(api_key=api_key)
client = genai.GenerativeModel("gemini-2.0-flash")

max_iterations = 6
last_response = None
iteration = 0
iteration_response = []

async def generate_with_timeout(client, prompt, timeout=10):
    """Generate content with a timeout"""
    print("Starting LLM generation...")
    try:
        # Convert the synchronous generate_content call to run in a thread
        loop = asyncio.get_event_loop()
        response = await asyncio.wait_for(
            loop.run_in_executor(
                None, 
                lambda: client.generate_content(prompt)
            ),
            timeout=timeout
        )
        print("LLM generation completed")
        return response
    except TimeoutError:
        print("LLM generation timed out!")
        raise
    except Exception as e:
        print(f"Error in LLM generation: {e}")
        raise

def reset_state():
    """Reset all global variables to their initial state"""
    global last_response, iteration, iteration_response
    last_response = None
    iteration = 0
    iteration_response = []

app = FastAPI()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            # Receive a message from client
            query = await websocket.receive_text()
            print(f"Client says: {query}")
            gmail_query = build_gmail_search_query(query)

            # Respond back to client
            await websocket.send_text(gmail_query)
            collected_snippets = []
            while True:
                date = await websocket.receive_text()
                if date == "Done":
                    break
                subject = await websocket.receive_text()
                body = await websocket.receive_text()
                details = get_details_from_email_body(body, query)
                full_snippet = (
                        f"Date: {date}\n"
                        f"Subject: {subject}\n"
                        f"Details: {details}\n"
                    )
                collected_snippets.append(full_snippet)
            print(f"Received snippets: {collected_snippets}")
            summarized_email = summarize_emails_with_query(query, collected_snippets)
            #list_of_numbers = get_total_expenses_from_emails_with_query(summarized_email)
            #reset_state()  # Reset at the start of main
            #print("Starting main execution...")
            #try:
                # Create a single MCP server connection
                #print("Establishing connection to MCP server...")
                #server_params = StdioServerParameters(
                #    command="python",
                #    args=["example2.py"]
                #)

                #async with stdio_client(server_params) as (read, write):
                #    print("Connection established, creating session...")
                #    async with ClientSession(read, write) as session:
                #        print("Session created, initializing...")
                #        await session.initialize()
                        
                        # Get available tools
                #        print("Requesting tool list...")
                #        tools_result = await session.list_tools()
                #        tools = tools_result.tools
                #        print(f"Successfully retrieved {len(tools)} tools")

                        # Create system prompt with available tools
                        #print("Creating system prompt...")
                        #print(f"Number of tools: {len(tools)}")
                        
                        #try:
                            # First, let's inspect what a tool object looks like
                            # if tools:
                            #     print(f"First tool properties: {dir(tools[0])}")
                            #     print(f"First tool example: {tools[0]}")
                            
                            #tools_description = []
                            #for i, tool in enumerate(tools):
                            #    try:
                            #        # Get tool properties
                            #        params = tool.inputSchema
                             #       desc = getattr(tool, 'description', 'No description available')
                              #      name = getattr(tool, 'name', f'tool_{i}')
                                    
                                    # Format the input schema in a more readable way
                            #        if 'properties' in params:
                            #            param_details = []
                            #            for param_name, param_info in params['properties'].items():
                            #                param_type = param_info.get('type', 'unknown')
                            #                param_details.append(f"{param_name}: {param_type}")
                            #            params_str = ', '.join(param_details)
                            #        else:
                            #            params_str = 'no parameters'

                            #        tool_desc = f"{i+1}. {name}({params_str}) - {desc}"
                            #        tools_description.append(tool_desc)
                            #        print(f"Added description for tool: {tool_desc}")
                            #    except Exception as e:
                            #        print(f"Error processing tool {i}: {e}")
                            #        tools_description.append(f"{i+1}. Error processing tool")
                            
                            #tools_description = "\n".join(tools_description)
                            #print("Successfully created tools description")
                        #except Exception as e:
                        #    print(f"Error creating tools description: {e}")
                        #    tools_description = "Error loading tools"
                        
                        #print("Created system prompt... ")
                        #print(list_of_numbers)

                        #_, function_info = list_of_numbers.split(":", 1)
                        #parts = [p.strip() for p in function_info.split("|")]
                       # func_name, params = parts[0], parts[1:]

            summarized_email = Replace_total_expenses_from_emails_with_query(summarized_email,1000)
            await websocket.send_text(summarized_email)

    except WebSocketDisconnect:
        print("Client disconnected")

    
    return {"answer": summarized_email}

def main():
    """Main function to run the FastAPI app"""
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8765)
if __name__ == "__main__":
    main()
    
    
