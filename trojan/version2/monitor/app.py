# app.py

import asyncio
import subprocess
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel


CACHE_TTL_SECONDS = 10.0
COMMAND_TIMEOUT_SECONDS = 1.0


class ConnectionStat(BaseModel):
    client_ip: str
    count: int


class CommandResult(BaseModel):
    items: list[ConnectionStat]
    generated_at: datetime
    cached: bool


@dataclass
class CacheEntry:
    data: dict[str, Any]
    created_at: float


app = FastAPI()

# This state belongs only to the current Python process.
_cache: CacheEntry | None = None

# Prevent multiple coroutines from refreshing the cache simultaneously.
_refresh_lock = asyncio.Lock()


async def run_command_async() -> dict[str, Any]:
    process = await asyncio.create_subprocess_shell(
        "netstat -4 -ant | grep :443 | grep ESTABLISHED | awk '{print $5}' | cut -d : -f 1 | sort | uniq -c | sort -nrk 1 | head",
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

    if process.returncode != 0:
        raise RuntimeError(
            f"Command failed with code {process.returncode}: "
            f"{stderr.decode().strip()}"
        )

    def line_to_connection_stat(line: str) -> ConnectionStat:
        match line.strip().split(' '):
            case [count_s, client_ip]:
                return ConnectionStat(count=int(count_s), client_ip=client_ip)
            case _:
                raise ValueError(f"Unable to parse ConnectionStat from string: {line.strip()}")

    items = [
        line_to_connection_stat(line)
        for line in stdout.decode().splitlines()
        if line.strip()
    ]

    return {
        "items": items,
        "generated_at": datetime.fromtimestamp(time.time(), tz=timezone.utc)
    }


def cache_is_valid(now: float) -> bool:
    return (
        _cache is not None
        and now - _cache.created_at < CACHE_TTL_SECONDS
    )


async def get_command_result() -> tuple[dict[str, Any], bool]:
    """
    Return:
        (result data, whether it came from the cache)
    """

    global _cache

    now = time.monotonic()

    # First check: no lock is needed when the cache is valid.
    if cache_is_valid(now):
        assert _cache is not None
        return _cache.data, True

    async with _refresh_lock:
        # Second check:
        # Another request may have completed the refresh while we waited for the lock.
        now = time.monotonic()

        if cache_is_valid(now):
            assert _cache is not None
            return _cache.data, True

        # Run the synchronous blocking command in a thread.
        # data = await asyncio.to_thread(run_command_and_process_output)
        data = await run_command_async()

        _cache = CacheEntry(
            data=data,
            created_at=time.monotonic(),
        )

        return data, False


@app.get("/connection-count", response_model=CommandResult)
async def connection_count() -> CommandResult:
    try:
        data, cached = await get_command_result()
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

    return CommandResult(
        **data,
        cached=cached,
    )


@app.get("/request-info")
async def request_info(request: Request) -> dict[str, dict[str, str]]:
    return {"headers": dict(request.headers)}
