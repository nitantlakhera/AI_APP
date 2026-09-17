┌──────────────────────────────────────────────┐
│ USER                                         │
│                                              │
│ "What is the name and role of user 101?"    │
└──────────────────────┬───────────────────────┘
                       │
                       ▼
              ┌─────────────────┐
              │   run_agent()   │
              └────────┬────────┘
                       │
                       │ messages
                       ▼
              ┌─────────────────┐
              │      LLM        │
              │   qwen2.5:3b    │
              │    via Ollama   │
              └────────┬────────┘
                       │
                       │ Understands:
                       │ "This is about
                       │  user ID 101"
                       ▼
              ┌─────────────────────┐
              │ TOOL SELECTION      │
              │                     │
              │ get_user_info       │
              │ user_id = 101       │
              └─────────┬───────────┘
                        │
                        │ tool_call
                        ▼
              ┌─────────────────────┐
              │ available_tools     │
              │                     │
              │ "get_user_info" ────┼──► get_user_info()
              └─────────────────────┘
                        │
                        ▼
              ┌─────────────────────┐
              │ Python Function     │
              │                     │
              │ get_user_info(101)  │
              └─────────┬───────────┘
                        │
                        ▼
              ┌─────────────────────┐
              │ TOOL RESULT         │
              │                     │
              │ name: Rahul         │
              │ city: Bangalore     │
              │ role: Software Eng. │
              └─────────┬───────────┘
                        │
                        │ send result
                        ▼
              ┌─────────────────────┐
              │      LLM            │
              │                     │
              │ Processes result    │
              └─────────┬───────────┘
                        │
                        ▼
              ┌─────────────────────┐
              │ FINAL ANSWER        │
              │                     │
              │ "User 101 is Rahul, │
              │ a Software Engineer │
              │ based in Bangalore."│
              └─────────────────────┘

mcp dev AI_AGENTS\weather_server.py