---
title: "Agents"
source: "03_agents.txt"
tags: "compiled"
---

## Summary
Demo mode converted `03_agents.txt` into a persistent wiki page without using an LLM. The source content is preserved below rather than being presented as AI-generated synthesis.

## Source Knowledge

# AI Agents and Agentic AI

## What is an AI Agent?
An AI agent is a system where an LLM autonomously decides what actions to take
to accomplish a goal. Unlike a simple chatbot that just responds, an agent can:
- Plan multi-step tasks
- Use tools (calculators, APIs, databases)
- Observe results and adapt its approach
- Work autonomously until the task is complete

Agentic AI vs Generative AI:
- Generative AI: Creates content (text, images) from a prompt
- Agentic AI: Takes actions in the world to achieve goals

The ReAct Pattern (Reason + Act):
1. THOUGHT: The agent reasons about what to do next
2. ACTION: It calls a tool with specific parameters
3. OBSERVATION: It sees the tool's result
4. Repeat until the task is done

Agent Components:
- LLM (the brain): Decides what to do
- Tools (the hands): Functions the agent can call
- Memory: Remembers past actions and results
- Planning: Breaks complex tasks into steps

Tool Calling / Function Calling:
Modern LLMs can output structured JSON requesting a tool call:
  {"tool": "calculator", "arguments": {"expression": "2 + 2"}}
The application executes the tool and feeds the result back to the LLM.

Types of Agents:
- Simple agents: One LLM + a few tools (this project)
- Multi-agent systems: Multiple specialized agents collaborating
- Autonomous agents: Long-running agents that pursue open-ended goals

MCP (Model Context Protocol):
MCP is a standard protocol for connecting AI models to external tools and data.
Think of it as USB for AI — one standard interface, many compatible tools.
- MCP Servers expose tools, resources, and prompts
- MCP Clients (Cursor, Claude Desktop) connect to servers
- This project includes an MCP server in src/mcp/server.py

Safety Considerations:
- Limit the number of agent steps to prevent infinite loops
- Validate tool inputs before execution
- Use allowlists for which tools an agent can access
- Log all agent actions for debugging and auditing

## Related
- [[index]]
