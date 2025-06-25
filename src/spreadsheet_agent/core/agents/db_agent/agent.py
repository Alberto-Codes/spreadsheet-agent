"""Defines the db agent."""

from google.adk.agents import Agent

from spreadsheet_agent.core.tools.db_interrogator import (
    get_object_columns,
    get_object_summary,
    get_view_definition,
    list_tables_and_views,
)

from .prompts import DB_AGENT_INSTRUCTION

root_agent = Agent(
    model="gemini-2.0-flash",
    name="db_agent",
    description="An agent that can answer questions about the database.",
    instruction=DB_AGENT_INSTRUCTION,
    tools=[
        list_tables_and_views,
        get_object_columns,
        get_object_summary,
        get_view_definition,
    ],
)
