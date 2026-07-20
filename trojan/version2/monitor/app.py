import asyncio
import json
import logging
import subprocess
import time
from collections.abc import Collection
from datetime import datetime, timezone
from typing import Any, override

from async_lru import alru_cache
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# In this project, using uvicorn.error is a pragmatic choice
# because Uvicorn has already configured its handler
logger = logging.getLogger("uvicorn.error")


COMMAND_TIMEOUT_SECONDS = 1.0


class IpAddressCountItem(BaseModel):
    ip: str
    count: int


class ConnectionStateCountItem(BaseModel):
    state: str
    count: int


class IncomingConnectionCountItem(BaseModel):
    port: int
    count: int


class StatusOverview(BaseModel):
    server_port: int
    current_client_ip: str
    total_connections: int
    connection_state_counts: list[ConnectionStateCountItem]
    client_ip_counts: list[IpAddressCountItem]
    incoming_connection_counts: list[IncomingConnectionCountItem]
    generated_at: datetime


class PrettyJSONResponse(JSONResponse):
    @override
    def render(self, content: Any) -> bytes:
        return json.dumps(
            content,
            ensure_ascii=False,
            allow_nan=False,
            indent=2,
        ).encode("utf-8")


app = FastAPI()


async def capture_shell_output(
    command: str,
    *,
    allowed_return_codes: Collection[int] = (0,),
) -> str:
    process = await asyncio.create_subprocess_shell(
        command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    try:
        stdout, stderr = await asyncio.wait_for(
            process.communicate(),
            timeout=COMMAND_TIMEOUT_SECONDS,
        )
    except TimeoutError:
        process.kill()
        await process.wait()
        raise

    if process.returncode not in allowed_return_codes:
        raise RuntimeError(
            f"Command failed with code {process.returncode}: {stderr.decode().strip()}"
        )

    return stdout.decode()


async def get_client_ip_counts(
    server_port: int, limit: int = 10
) -> list[IpAddressCountItem]:
    if limit <= 0:
        raise ValueError(f"Invalid limit: {limit}. It must be a positive integer")

    command = (
        f"netstat -4 -ant | grep ':{server_port} ' | grep ESTABLISHED | "
        "awk '{print $5}' | cut -d : -f 1 | sort | uniq -c | "
        f"sort -nrk 1 | head -n {limit}"
    )

    stdout = await capture_shell_output(command, allowed_return_codes=(0, 1))

    def line_to_ip_count(line: str) -> IpAddressCountItem:
        match line.strip().split(" "):
            case [count_s, client_ip]:
                return IpAddressCountItem(count=int(count_s), ip=client_ip)
            case _:
                raise ValueError(
                    f"Unable to parse IpAddressCountItem from string: {line.strip()}"
                )

    return [line_to_ip_count(line) for line in stdout.splitlines() if line.strip()]


async def get_incoming_connection_counts(
    limit: int = 10,
) -> list[IncomingConnectionCountItem]:
    if limit <= 0:
        raise ValueError(f"Invalid limit: {limit}. It must be a positive integer")

    command = (
        "netstat -4 -ant | grep ^tcp | grep -v LISTEN | awk '{print $4}' | "
        f"cut -d : -f 2 | sort | uniq -c | sort -nrk 1 | head -n {limit}"
    )

    stdout = await capture_shell_output(command, allowed_return_codes=(0, 1))

    def line_to_incoming_conn_count(line: str) -> IncomingConnectionCountItem:
        match line.strip().split(" "):
            case [count_s, server_port]:
                return IncomingConnectionCountItem(
                    count=int(count_s), port=int(server_port)
                )
            case _:
                raise ValueError(
                    "Unable to parse IncomingConnectionCountItem from string: "
                    f"{line.strip()}"
                )

    return [
        line_to_incoming_conn_count(line) for line in stdout.splitlines() if line.strip()
    ]


async def get_total_connections(server_port: int) -> int:
    command = f"netstat -4 -ant | grep -c ':{server_port} '"
    stdout = await capture_shell_output(command, allowed_return_codes=(0, 1))
    return int(stdout)


async def get_connection_state_counts(server_port: int) -> list[ConnectionStateCountItem]:
    stdout = await capture_shell_output(
        f"netstat -4 -ant | grep ':{server_port} ' | "
        "awk '{print $6}' | sort | uniq -c | sort -nrk 1",
        allowed_return_codes=(0, 1),
    )

    def line_to_connection_state(line: str) -> ConnectionStateCountItem:
        match line.strip().split(" "):
            case [count_s, connection_state]:
                return ConnectionStateCountItem(
                    count=int(count_s), state=connection_state
                )
            case _:
                raise ValueError(
                    "Unable to parse ConnectionStateCountItem from string: "
                    f"{line.strip()}"
                )

    return [
        line_to_connection_state(line) for line in stdout.splitlines() if line.strip()
    ]


@alru_cache(maxsize=1, ttl=10)
async def get_server_status_overview(server_port: int) -> StatusOverview:
    total_connections = await get_total_connections(server_port)
    connection_state_counts = await get_connection_state_counts(server_port)
    client_ip_counts = await get_client_ip_counts(server_port, limit=10)
    incoming_connection_counts = await get_incoming_connection_counts(limit=10)
    return StatusOverview(
        server_port=server_port,
        current_client_ip="",
        total_connections=total_connections,
        connection_state_counts=connection_state_counts,
        client_ip_counts=client_ip_counts,
        incoming_connection_counts=incoming_connection_counts,
        generated_at=datetime.fromtimestamp(time.time(), tz=timezone.utc),
    )


def get_client_ip(request: Request) -> str:
    ip = request.headers.get("x-real-ip", None)
    if ip is None:
        ip = request.client.host if request.client else "***"
    return ip


@app.get("/overview", response_class=PrettyJSONResponse)
async def status_overview(request: Request, port: int = 443) -> StatusOverview:
    try:
        overview = await get_server_status_overview(port)
        current_client_ip = get_client_ip(request)
        overview.current_client_ip = current_client_ip
        return overview
    except subprocess.TimeoutExpired as exc:
        raise HTTPException(
            status_code=504,
            detail=f"Command timed out after {exc.timeout} seconds",
        ) from exc
    except subprocess.CalledProcessError as exc:
        stderr = exc.stderr.strip() if exc.stderr else ""

        raise HTTPException(
            status_code=500,
            detail={
                "message": "Command execution failed",
                "return_code": exc.returncode,
                "stderr": stderr,
            },
        ) from exc
    except OSError as exc:
        # Includes cases such as a missing command or insufficient permissions.
        raise HTTPException(
            status_code=500,
            detail=f"Unable to execute command: {exc}",
        ) from exc
