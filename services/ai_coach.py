from core.config import settings

SYSTEM_PROMPT = """
You are Pace, a factual, data-grounded HYROX coach for two Mixed Doubles athletes.
Praise only when supported by evidence, and keep praise restrained. Do not use hype.
Identify uncertainty, incomplete data, workload risk, pain patterns, and the highest-value
next action. Do not diagnose injuries. Recommend medical assessment when symptoms are
persistent, worsening, severe, or affecting normal movement.
"""

def answer_question(question: str, context: str) -> str:
    if not settings.ai_ready:
        return (
            "Demo response: Based on the available training record, the priority is to "
            "maintain consistent running volume without adding another high-intensity "
            "session. The knee-pain entries should be monitored after the next two sessions."
        )

    from openai import OpenAI
    client = OpenAI(api_key=settings.openai_api_key)
    response = client.responses.create(
        model=settings.openai_model,
        instructions=SYSTEM_PROMPT,
        input=f"Training context:\n{context}\n\nQuestion:\n{question}",
    )
    return response.output_text
