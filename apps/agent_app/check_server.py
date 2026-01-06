import httpx
import asyncio

async def check():
    url = "http://127.0.0.1:8000/form-schema"
    print(f"Checking {url}...")
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(url)
            print(f"Status: {resp.status_code}")
            print(f"Content: {resp.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(check())
