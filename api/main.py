import asyncio
from contextlib import asynccontextmanager

import httpx
from fastapi import Depends, FastAPI, HTTPException, WebSocket, WebSocketDisconnect

from api.auth import verify_api_key
from api.metrics import get_system_metrics
from api.models import Server, ServerIn, ServerOut
from api.poller import poll_server, run_poll_loop

servers: dict[str, Server] = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(run_poll_loop(servers))
    yield
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass


app = FastAPI(title="DevOps Monitor API", lifespan=lifespan)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/metrics")
async def metrics():
    return get_system_metrics()


@app.websocket("/ws/metrics")
async def ws_metrics(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = get_system_metrics()
            await websocket.send_json(data)
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        pass


@app.post("/servers", status_code=201)
async def create_server(
    server_in: ServerIn,
    _: str = Depends(verify_api_key),
):
    server = Server(
        name=server_in.name,
        host=server_in.host,
        port=server_in.port,
    )
    servers[server.id] = server
    return ServerOut.from_server(server)


@app.get("/servers")
async def list_servers():
    return [ServerOut.from_server(s) for s in servers.values()]


@app.delete("/servers/{server_id}", status_code=204)
async def delete_server(
    server_id: str,
    _: str = Depends(verify_api_key),
):
    if server_id not in servers:
        raise HTTPException(status_code=404, detail="Server not found")
    del servers[server_id]


@app.post("/servers/{server_id}/check")
async def check_server(server_id: str):
    if server_id not in servers:
        raise HTTPException(status_code=404, detail="Server not found")
    server = servers[server_id]
    async with httpx.AsyncClient() as client:
        await poll_server(server, client)
    return ServerOut.from_server(server)
