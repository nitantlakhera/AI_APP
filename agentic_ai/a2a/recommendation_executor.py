from a2a.server.agent_execution import (
    AgentExecutor,
    RequestContext
)

from a2a.server.events import EventQueue

from a2a.helpers import (
    get_message_text,
    new_task_from_user_message,
    new_text_message,
    new_text_part
)

from a2a.server.tasks import TaskUpdater

from a2a.types.a2a_pb2 import TaskState

from agentic_ai.agents.llm_provider import chat_llm


class RecommendationAgentExecutor(AgentExecutor):

    async def execute(
            self,
            context: RequestContext,
            event_queue: EventQueue
    ):

        print("\n========================================")
        print("RECOMMENDATION A2A AGENT")
        print("========================================")

        # -----------------------------------------
        # 1. Get or create task
        # -----------------------------------------

        if context.current_task:
            task = context.current_task

        else:
            task = new_task_from_user_message(
                context.message
            )

            await event_queue.enqueue_event(
                task
            )

        print("\nTask ID:")
        print(task.id)

        # -----------------------------------------
        # 2. Create TaskUpdater
        # -----------------------------------------

        task_updater = TaskUpdater(
            event_queue=event_queue,
            task_id=task.id,
            context_id=task.context_id
        )

        # -----------------------------------------
        # 3. Mark task as WORKING
        # -----------------------------------------

        await task_updater.update_status(
            state=TaskState.TASK_STATE_WORKING,
            message=new_text_message(
                "Generating recommendation..."
            )
        )

        # -----------------------------------------
        # 4. Read incoming A2A message
        # -----------------------------------------

        message = get_message_text(
            context.message
        )

        print("\nReceived A2A message:")
        print(message)

        # -----------------------------------------
        # 5. Call Recommendation LLM
        # -----------------------------------------

        messages = [
            {
                "role": "system",
                "content": """
You are a Recommendation Agent.

You receive information from other agents.

The information may come from:

- User Agent
- Weather Agent
- Finance Agent

Combine the information and provide a useful
natural-language recommendation.

Do not mention:

- A2A
- MCP
- JSON
- internal agent communication
"""
            },
            {
                "role": "user",
                "content": message
            }
        ]

        print("\nCalling LLM...")

        response = chat_llm(messages)

        result = response.choices[0].message.content

        print("\n========================================")
        print("Recommendation Result:")
        print("========================================")
        print(result)

        # -----------------------------------------
        # 6. Add recommendation as artifact
        # -----------------------------------------

        print("\nSending result through A2A...")

        await task_updater.add_artifact(
            parts=[
                new_text_part(
                    text=result,
                    media_type="text/plain"
                )
            ]
        )

        # -----------------------------------------
        # 7. Mark task COMPLETED
        # -----------------------------------------

        await task_updater.update_status(
            state=TaskState.TASK_STATE_COMPLETED,
            message=new_text_message(
                "Recommendation generated successfully."
            )
        )

        print("\nA2A result sent successfully")

    async def cancel(
            self,
            context: RequestContext,
            event_queue: EventQueue
    ):

        raise NotImplementedError(
            "Cancel is not supported."
        )