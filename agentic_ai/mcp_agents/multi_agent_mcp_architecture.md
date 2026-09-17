# Multi-Agent AI System with MCP

## Architecture

```text
                         User Question
                              │
                              ▼
                       Supervisor Agent
                              │
                  ┌───────────┼───────────┐
                  │           │           │
                  ▼           ▼           ▼
              Weather      Finance       User
                Agent        Agent       Agent
                  │           │           │
                  └───────────┼───────────┘
                              │
                              ▼
                         MCP Manager
                              │
             ┌────────────────┼────────────────┐
             │                │                │
             ▼                ▼                ▼
        Weather MCP      Finance MCP        User MCP
             │                │                │
             ▼                ▼                ▼
          Weather          Finance         PostgreSQL
            API             Tools            Database
```

## Components

### 1. User

The user sends a natural-language question.

Examples:

```text
What is the weather in Jabalpur?
What is USD to INR?
What are the details of user 101?
```

The question is sent to the Supervisor Agent.

---

### 2. Supervisor Agent

The Supervisor Agent decides which specialized agent should handle the question.

It returns one of:

```text
weather
finance
user
```

Example:

```text
User:
Weather of Jabalpur?

Supervisor:
weather
```

The Supervisor does not execute the actual business operation. It only performs routing.

---

### 3. Specialized Agents

There are three specialized agents.

#### Weather Agent

Handles weather-related questions.

```text
Weather Agent
      │
      ▼
Weather MCP
      │
      ▼
Weather API
```

Example tool:

```text
get_weather(city)
```

#### Finance Agent

Handles finance-related questions such as currency exchange.

```text
Finance Agent
      │
      ▼
Finance MCP
      │
      ▼
Finance Tool / API
```

Example tool:

```text
get_exchange_rate(from_currency, to_currency)
```

#### User Agent

Handles questions about users.

```text
User Agent
      │
      ▼
User MCP
      │
      ▼
PostgreSQL
```

Example tool:

```text
get_user_from_db(user_id)
```

---

## 4. Central MCP Manager

The MCP Manager is shared by all specialized agents.

Its responsibilities are:

1. Load MCP server configuration.
2. Discover tools from MCP servers.
3. Convert MCP tool definitions into the format expected by the LLM.
4. Maintain the tool registry.
5. Route tool calls to the correct MCP server.

The manager discovers tools once:

```python
mcp_manager = MCPManager()

await mcp_manager.discover_tools()
```

Then the same manager is passed to the agents:

```python
await weather_agent(question, mcp_manager)

await finance_agent(question, mcp_manager)

await user_agent(question, mcp_manager)
```

---

## 5. MCP Server Configuration

MCP servers are configured in `mcp_servers.yaml`.

Example:

```yaml
servers:
  finance:
    url: http://localhost:8001/mcp

  user:
    url: http://localhost:8002/mcp

  weather:
    url: http://localhost:8003/mcp
```

The server name must match the name used by the agents:

```python
mcp_manager.get_tools_for_server("weather")
mcp_manager.get_tools_for_server("finance")
mcp_manager.get_tools_for_server("user")
```

The mapping must point to the correct MCP server:

```text
finance → server containing get_exchange_rate
user    → server containing get_user_from_db
weather → server containing get_weather
```

---

# Complete Request Flow

## Example: Weather Question

User asks:

```text
What is the weather in Jabalpur?
```

### Step 1 — Supervisor

```text
User
 │
 ▼
Supervisor Agent
 │
 ▼
weather
```

### Step 2 — Weather Agent

The orchestrator calls:

```python
await weather_agent(
    question,
    mcp_manager
)
```

The Weather Agent gets only weather tools:

```python
tools = mcp_manager.get_tools_for_server(
    "weather"
)
```

The LLM sees:

```text
get_weather
```

and decides to call it.

### Step 3 — MCP Manager

The Weather Agent calls:

```python
result = await mcp_manager.call_mcp_tool(
    tool_name,
    arguments
)
```

The MCP Manager looks up the tool in its registry:

```text
get_weather
     │
     ▼
weather
     │
     ▼
http://localhost:8003/mcp
```

### Step 4 — Weather MCP

The MCP server executes:

```text
get_weather("Jabalpur")
```

and returns the weather data.

### Step 5 — LLM

The result is sent back to the Weather Agent's LLM:

```text
Weather MCP
     │
     ▼
Tool Result
     │
     ▼
Weather Agent
     │
     ▼
LLM
     │
     ▼
Natural Language Answer
```

---

# Complete Architecture Flow

```text
                         ┌─────────────────┐
                         │      USER       │
                         └────────┬────────┘
                                  │
                                  │ Question
                                  ▼
                         ┌─────────────────┐
                         │   SUPERVISOR    │
                         │      AGENT      │
                         └────────┬────────┘
                                  │
                    ┌─────────────┼─────────────┐
                    │             │             │
                 weather       finance         user
                    │             │             │
                    ▼             ▼             ▼
             ┌──────────┐  ┌──────────┐  ┌──────────┐
             │ Weather  │  │ Finance  │  │   User   │
             │  Agent   │  │  Agent   │  │  Agent   │
             └────┬─────┘  └────┬─────┘  └────┬─────┘
                  │             │             │
                  └─────────────┼─────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   MCP MANAGER   │
                       └────────┬────────┘
                                │
                 ┌──────────────┼──────────────┐
                 │              │              │
                 ▼              ▼              ▼
          ┌────────────┐ ┌────────────┐ ┌────────────┐
          │  Weather   │ │  Finance   │ │    User    │
          │    MCP     │ │    MCP     │ │    MCP     │
          └─────┬──────┘ └─────┬──────┘ └─────┬──────┘
                │              │              │
                ▼              ▼              ▼
           Weather API    Finance API/Tool  PostgreSQL
```

---

# Python Application Flow

The main application is responsible for orchestration:

```python
async def main():

    # Create one central MCP manager
    mcp_manager = MCPManager()

    # Discover all MCP tools once
    await mcp_manager.discover_tools()

    # Supervisor decides the agent
    agent_name = run_supervisor_agent(question)

    # Call the selected agent
    if agent_name == "weather":
        result = await weather_agent(
            question,
            mcp_manager
        )

    elif agent_name == "finance":
        result = await finance_agent(
            question,
            mcp_manager
        )

    elif agent_name == "user":
        result = await user_agent(
            question,
            mcp_manager
        )
```

---

# Important Design Rules

## Rule 1 — Discover MCP tools once

Do this centrally:

```python
await mcp_manager.discover_tools()
```

Do not call discovery separately inside every agent.

---

## Rule 2 — Use one central MCP Manager

Create:

```python
mcp_manager = MCPManager()
```

in the main orchestrator and pass it to the agents.

```text
Main
 │
 └── MCPManager
       │
       ├── Weather Agent
       ├── Finance Agent
       └── User Agent
```

---

## Rule 3 — Agents should not know MCP URLs

The Weather Agent should not contain:

```text
http://localhost:8003/mcp
```

The MCP Manager owns that information.

The agent only knows:

```python
mcp_manager.get_tools_for_server("weather")
```

---

## Rule 4 — Agents should not directly access databases

The User Agent should not contain:

```python
psycopg2.connect(...)
```

The database access belongs to the User MCP server.

```text
User Agent
    │
    ▼
User MCP
    │
    ▼
PostgreSQL
```

---

## Rule 5 — MCP provides tool definitions dynamically

The agent does not need to manually create:

```python
tools = [
    {
        "type": "function",
        ...
    }
]
```

Instead:

```python
tools = mcp_manager.get_tools_for_server(
    "weather"
)
```

The MCP Manager obtains the tool definition from:

```python
await mcp_client.list_tools()
```

---

# Final Architecture

The system has four major layers:

```text
┌───────────────────────────────────────────┐
│              USER INTERFACE               │
│          CLI / Streamlit / API            │
└─────────────────────┬─────────────────────┘
                      │
                      ▼
┌───────────────────────────────────────────┐
│             SUPERVISOR AGENT              │
│              Agent Selection               │
└─────────────────────┬─────────────────────┘
                      │
          ┌───────────┼───────────┐
          ▼           ▼           ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│Weather Agent │ │Finance Agent │ │  User Agent  │
└──────┬───────┘ └──────┬───────┘ └──────┬───────┘
       │                │                │
       └────────────────┼────────────────┘
                        ▼
               ┌─────────────────┐
               │   MCP MANAGER   │
               │ Discovery +     │
               │ Tool Routing    │
               └────────┬────────┘
                        │
          ┌─────────────┼─────────────┐
          ▼             ▼             ▼
   ┌────────────┐ ┌────────────┐ ┌────────────┐
   │ Weather MCP│ │ Finance MCP│ │  User MCP  │
   └─────┬──────┘ └─────┬──────┘ └─────┬──────┘
         │              │              │
         ▼              ▼              ▼
      Weather        Finance       PostgreSQL
        API          Service        Database
```

This gives you a clean progression from a simple tool-calling agent to a **multi-agent + MCP architecture**.
