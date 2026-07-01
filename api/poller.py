import asyncio

import httpx

from api.models import Server


async def poll_server(server: Server, client: httpx.AsyncClient) -> None:
    try:
        response = await client.get(
            f"{server.base_url()}/health", timeout=5.0
        )
        if response.status_code == 200:
            server.status = "UP"
        else:
            server.status = "DEGRADED"
    except Exception:
        server.status = "DOWN"


async def run_poll_loop(servers: dict[str, Server]) -> None:
    async with httpx.AsyncClient() as client:
        while True:
            if servers:
                tasks = [
                    poll_server(server, client)
                    for server in servers.values()
                ]
                await asyncio.gather(*tasks)
            await asyncio.sleep(10)
