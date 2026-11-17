import asyncio
from agent_bridge import bridge

async def test():
    q = "Can a zero-vehicle caregiver reach the evaluation hub by public bus?"
    print("Testing bridge with query:", q)
    ans = await bridge.ask(q, "MS")
    print("\n--- RESPONSE FROM ADK BRIDGE ---")
    print(ans)

if __name__ == "__main__":
    asyncio.run(test())
