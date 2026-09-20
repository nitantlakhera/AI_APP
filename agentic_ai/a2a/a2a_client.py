import asyncio
import httpx

from a2a.client import (
    A2ACardResolver,
    ClientConfig,
    create_client
)

from a2a.helpers import (
    new_text_message
)

from a2a.types import (
    Role,
    SendMessageRequest
)

RECOMMENDATION_URL = "http://127.0.0.1:9000"


async def send_to_recommendation_agent(message_text):
    print("\n========================================")
    print("A2A CLIENT")
    print("========================================")

    # --------------------------------------------------
    # HTTP timeout
    #
    # Ollama may take some time to generate the answer.
    # Give the server enough time.
    # --------------------------------------------------

    timeout = httpx.Timeout(
        connect=10.0,
        read=180.0,
        write=30.0,
        pool=30.0
    )

    async with httpx.AsyncClient(
            timeout=timeout
    ) as httpx_client:

        # --------------------------------------------------
        # 1. Get Agent Card
        # --------------------------------------------------

        print("\nGetting Agent Card...")

        resolver = A2ACardResolver(
            httpx_client=httpx_client,
            base_url=RECOMMENDATION_URL
        )

        agent_card = await resolver.get_agent_card()

        print("\nAgent Card received:")
        print("Name:", agent_card.name)
        print("Description:", agent_card.description)

        # --------------------------------------------------
        # 2. Create A2A Client
        # --------------------------------------------------

        print("\nCreating A2A client...")

        config = ClientConfig(
            streaming=False,
            polling=False,
            httpx_client=httpx_client
        )

        client = await create_client(
            agent=agent_card,
            client_config=config
        )

        print("A2A client created successfully")

        # --------------------------------------------------
        # 3. Create A2A Message
        # --------------------------------------------------

        print("\nCreating A2A message...")

        message = new_text_message(
            message_text,
            role=Role.ROLE_USER
        )

        request = SendMessageRequest(
            message=message
        )

        # --------------------------------------------------
        # 4. Send request
        # --------------------------------------------------

        print("\nSending message to Recommendation Agent...")

        try:

            response_stream = client.send_message(
                request
            )

            print("\nWaiting for Recommendation Agent...")

            # --------------------------------------------------
            # 5. Read A2A response
            # --------------------------------------------------

            async for response in response_stream:

                print("\n========================================")
                print("A2A RESPONSE RECEIVED")
                print("========================================")

                print(response)

                # --------------------------------------------------
                # Response is normally a Task for this flow
                # --------------------------------------------------

                if hasattr(response, "task"):

                    task = response.task

                    print("\nTask ID:")
                    print(task.id)

                    print("\nTask status:")

                    if task.status:
                        print(task.status.state)

                    # --------------------------------------------------
                    # Read artifacts
                    # --------------------------------------------------

                    if task.artifacts:

                        print("\n========================================")
                        print("RECOMMENDATION")
                        print("========================================")

                        for artifact in task.artifacts:

                            for part in artifact.parts:

                                if hasattr(part, "text"):
                                    print(part.text)

                                    return part.text

                # --------------------------------------------------
                # Sometimes the response can be a Message
                # --------------------------------------------------

                elif hasattr(response, "message"):

                    print("\nMessage response received:")

                    message_response = response.message

                    for part in message_response.parts:

                        if hasattr(part, "text"):
                            print(part.text)

                            return part.text

            print("\nNo recommendation received.")

            return None

        except Exception as e:

            print("\n========================================")
            print("A2A CLIENT ERROR")
            print("========================================")

            print("Exception type:")
            print(type(e).__name__)

            print("Exception:")
            print(e)

            raise

        finally:

            await client.close()


async def main():
    print("\n========================================")
    print("STARTING A2A REQUEST")
    print("========================================")

    message = """
USER INFORMATION:
Name: Rahul
City: Bangalore
Role: Software Engineer

WEATHER INFORMATION:
Temperature: 29°C
Condition: Light rain
Humidity: 70%

FINANCE INFORMATION:
Daily budget: ₹800

Based on this information,
provide a useful recommendation.
"""

    result = await send_to_recommendation_agent(message)

    print("#----------------------------")

    if result:
        print(result)
    else:
        print("Not delivered")

if __name__ == "__main__":
    asyncio.run(main())
