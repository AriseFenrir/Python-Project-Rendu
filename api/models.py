from dataclasses import dataclass, field
from uuid import uuid4

from pydantic import BaseModel, Field


@dataclass
class Server:
    name: str
    host: str
    port: int
    id: str = field(default_factory=lambda: str(uuid4()))
    status: str = "UNKNOWN"

    def base_url(self) -> str:
        return f"http://{self.host}:{self.port}"


class ServerIn(BaseModel):
    name: str
    host: str
    port: int = Field(ge=1, le=65535)


class ServerOut(BaseModel):
    id: str
    name: str
    host: str
    port: int
    status: str

    @classmethod
    def from_server(cls, server: Server) -> "ServerOut":
        return cls(
            id=server.id,
            name=server.name,
            host=server.host,
            port=server.port,
            status=server.status,
        )
