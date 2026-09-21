from agentic_ai.agents.llm_provider import chat_llm

from agentic_ai.rag.retriever import retrieve_documents


# ============================================================
# RAG AGENT
# ============================================================

def rag_agent(question):
    print("\n========================================")
    print("RAG AGENT")
    print("========================================")

    print("\nQuestion:")
    print(question)

    # ========================================================
    # RETRIEVE DOCUMENTS
    # ========================================================

    documents = retrieve_documents(
        question,
        top_k=4
    )

    print("\n========================================")
    print("RETRIEVED DOCUMENTS")
    print("========================================")

    for index, item in enumerate(documents):
        print(
            f"\nDocument {index + 1}:"
        )

        print(
            item["document"]
        )

        print(
            "Metadata:",
            item["metadata"]
        )

    # ========================================================
    # CHECK IF DOCUMENTS WERE FOUND
    # ========================================================

    if not documents:
        return (
            "I could not find relevant information "
            "in the knowledge base."
        )

    # ========================================================
    # BUILD CONTEXT
    # ========================================================

    context = ""

    for index, item in enumerate(documents):
        context += f"""

--- DOCUMENT {index + 1} ---

{item["document"]}

SOURCE:
{item["metadata"]}
"""

    # ========================================================
    # ASK LLM
    # ========================================================

    messages = [
        {
            "role": "system",
            "content": """
You are a Knowledge/RAG Agent.

Answer the user's question using ONLY
the information provided in the retrieved
knowledge.

Do not invent information.

If the retrieved knowledge does not contain
the answer, say:

"I could not find this information
in the knowledge base."

Keep the answer clear and concise.

Mention the source when possible.
"""
        },
        {
            "role": "user",
            "content": f"""
USER QUESTION:

{question}


RETRIEVED KNOWLEDGE:

{context}


Answer the user's question using the
retrieved knowledge.
"""
        }
    ]

    # ========================================================
    # CALL LLM
    # ========================================================

    response = chat_llm(
        messages
    )

    answer = response.choices[0].message.content

    # ========================================================
    # RETURN RESULT
    # ========================================================

    result = {
        "answer": answer,
        "sources": [
            item["metadata"]
            for item in documents
        ]
    }

    print("\n========================================")
    print("RAG ANSWER")
    print("========================================")

    print(answer)

    print("\nSources:")
    print(result["sources"])

    return result
