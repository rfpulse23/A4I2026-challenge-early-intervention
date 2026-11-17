import asyncio
import os
from google.genai import types
from agent.agent import root_agent
from google.adk.runners import InMemoryRunner

os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "True"
os.environ["GOOGLE_CLOUD_PROJECT"] = os.environ.get("GOOGLE_CLOUD_PROJECT", "qwiklabs-gcp-04-5956a6cfcbdf")
os.environ["GOOGLE_CLOUD_LOCATION"] = os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")

async def main():
    runner = InMemoryRunner(agent=root_agent)
    session = await runner.session_service.create_session(user_id="coordinator", app_name=runner.app_name)
    print("Created session:", session.id)
    
    msg = types.Content(role="user", parts=[types.Part.from_text(text="Can a zero-vehicle caregiver reach the evaluation hub by public bus?")])
    
    answer_text = ""
    async for event in runner.run_async(user_id="coordinator", session_id=session.id, new_message=msg):
        # Event might have content or be an ADK event object
        if hasattr(event, "content") and event.content:
            for part in event.content.parts:
                if hasattr(part, "text") and part.text:
                    answer_text += part.text
        if hasattr(event, "actions"):
            print("Actions executed:", event.actions)

    print("\n--- FINAL AGENT ANSWER ---")
    print(answer_text)

if __name__ == "__main__":
    asyncio.run(main())
