"""Personal Productivity Assistant - Multi-Agent AI System.

This module defines the root agent and sub-agents for managing tasks,
calendar events, and notes using Google ADK.
"""

import os
import logging

from dotenv import load_dotenv
from google.adk import Agent
from google.adk.agents import SequentialAgent
from google.adk.tools.tool_context import ToolContext
from google.cloud import logging as cloud_logging

from productivity_assistant.tools.task_tools import (
    create_task,
    list_tasks,
    update_task_status,
    delete_task,
)
from productivity_assistant.tools.calendar_tools import (
    create_event,
    list_events,
    delete_event,
)
from productivity_assistant.tools.notes_tools import (
    create_note,
    list_notes,
    search_notes,
)

load_dotenv()

# Initialize cloud logging (lazy - only when credentials available)
try:
    cloud_logging.Client().setup_logging()
except Exception:
    logging.basicConfig(level=logging.INFO)

model_name = os.getenv("MODEL", "gemini-2.0-flash")


def add_prompt_to_state(tool_context: ToolContext, prompt: str) -> dict:
    """Save the user's prompt to the tool context state.

    Args:
        tool_context: The tool context for state management.
        prompt: The user's prompt to save.

    Returns:
        dict: A dictionary with status indicating success.
    """
    tool_context.state["PROMPT"] = prompt
    logging.info(f"Saved prompt to state: {prompt}")
    return {"status": "success"}


task_agent = Agent(
    name="task_agent",
    model=model_name,
    tools=[create_task, list_tasks, update_task_status, delete_task],
    instruction="""
    You manage the user's tasks. Read the PROMPT from state.
    If the user wants to create, list, update, or delete a task,
    use the appropriate tool. Always return a clear confirmation.
    PROMPT: { PROMPT }
    """,
)

calendar_agent = Agent(
    name="calendar_agent",
    model=model_name,
    tools=[create_event, list_events, delete_event],
    instruction="""
    You manage the user's calendar. Read the PROMPT from state.
    If the user wants to create, list, or delete an event,
    use the appropriate tool. Always return a clear confirmation.
    PROMPT: { PROMPT }
    """,
)

notes_agent = Agent(
    name="notes_agent",
    model=model_name,
    tools=[create_note, list_notes, search_notes],
    instruction="""
    You manage the user's notes. Read the PROMPT from state.
    If the user wants to create, list, or search notes,
    use the appropriate tool. Always return a clear confirmation.
    PROMPT: { PROMPT }
    """,
)

formatter_agent = Agent(
    name="formatter_agent",
    model=model_name,
    tools=[],
    instruction="""
    You are the final voice of the assistant. Read all outputs
    from state and synthesize them into one clean, conversational,
    friendly response for the user. Be concise. Be helpful.
    """,
    output_key="final_response",
)

productivity_workflow = SequentialAgent(
    name="productivity_workflow",
    sub_agents=[task_agent, calendar_agent, notes_agent, formatter_agent],
)

root_agent = Agent(
    name="greeter",
    model=model_name,
    tools=[add_prompt_to_state],
    sub_agents=[productivity_workflow],
    instruction="""
    You are a friendly personal productivity assistant.
    Greet the user warmly. When they tell you what they need,
    use add_prompt_to_state to save their request, then
    transfer control to productivity_workflow.
    """,
)
