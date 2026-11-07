import asyncio
import httpx
from api.index import app

async def test():
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        # Test 1: Clean root
        r1 = await client.get("/")
        print("GET / ->", r1.status_code, r1.text)

        # Test 2: If Vercel passes /api/index
        r2 = await client.get("/api/index")
        print("GET /api/index ->", r2.status_code, r2.text)

        # Test 3: If Vercel passes /api/index/api/v1/health
        r3 = await client.get("/api/index/api/v1/health")
        print("GET /api/index/api/v1/health ->", r3.status_code, r3.text)

asyncio.run(test())

