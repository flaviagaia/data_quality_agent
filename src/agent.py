from __future__ import annotations

import os
from typing import Any

from .tools import (
    build_data_quality_summary,
    build_fallback_report,
    get_record_context,
    suggest_record_corrections,
    validate_record_fields,
)

try:
    from haystack.components.generators.chat import OpenAIChatGenerator
    from haystack.dataclasses import ChatMessage
    from haystack.tools.tool import Tool
    from haystack_experimental.components.agents import Agent
except Exception:  # pragma: no cover - optional runtime dependency
    OpenAIChatGenerator = None
    ChatMessage = None
    Tool = None
    Agent = None


SYSTEM_PROMPT = """
You are a data quality agent.

Your responsibilities:
- inspect a customer record;
- identify quality issues in format and consistency;
- recommend safe corrections or remediation steps;
- keep the response grounded in tool outputs only.
"""


def _build_haystack_agent(model_name: str = "gpt-4.1-mini"):
    if not (OpenAIChatGenerator and ChatMessage and Tool and Agent and os.getenv("OPENAI_API_KEY")):
        return None

    generator = OpenAIChatGenerator(model=model_name, api_key=os.getenv("OPENAI_API_KEY"))
    tools = [
        Tool(
            name="get_record_context",
            description="Retrieve the full customer record by record_id.",
            parameters={"type": "object", "properties": {"record_id": {"type": "string"}}, "required": ["record_id"]},
            function=get_record_context,
        ),
        Tool(
            name="validate_record_fields",
            description="Validate customer record fields and list quality issues.",
            parameters={"type": "object", "properties": {"record_id": {"type": "string"}}, "required": ["record_id"]},
            function=validate_record_fields,
        ),
        Tool(
            name="suggest_record_corrections",
            description="Suggest remediation steps for the record.",
            parameters={"type": "object", "properties": {"record_id": {"type": "string"}}, "required": ["record_id"]},
            function=suggest_record_corrections,
        ),
        Tool(
            name="build_data_quality_summary",
            description="Generate an executive summary of the record quality.",
            parameters={"type": "object", "properties": {"record_id": {"type": "string"}}, "required": ["record_id"]},
            function=build_data_quality_summary,
        ),
    ]
    return Agent(chat_generator=generator, tools=tools, system_prompt=SYSTEM_PROMPT)


def ask_data_quality_agent(
    record_id: str,
    user_question: str,
    model_name: str = "gpt-4.1-mini",
) -> dict[str, Any]:
    agent = _build_haystack_agent(model_name=model_name)
    if agent is None:
        report = build_fallback_report(record_id=record_id, user_question=user_question)
        return {"runtime_mode": "deterministic_fallback", **report}

    report = build_fallback_report(record_id=record_id, user_question=user_question)
    try:
        messages = [
            ChatMessage.from_system(SYSTEM_PROMPT),
            ChatMessage.from_user(
                f"record_id={record_id}\nuser_question={user_question}\n"
                "Inspect the record, identify quality issues and recommend corrections."
            ),
        ]
        response = agent.run(messages=messages)
        if isinstance(response, dict):
            reply = response.get("messages", [])[-1].text if response.get("messages") else report["final_message"]
        else:
            reply = report["final_message"]
        report["final_message"] = reply
        return {"runtime_mode": "haystack_agent", **report}
    except Exception:
        return {"runtime_mode": "deterministic_fallback", **report}
