import uvicorn
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route

from pait.app.starlette import pait
from pait.field import Json


def sync_heavy_task(data: str) -> str:
    """Simulate a slow synchronous task, such as a database query or file processing."""
    import time

    time.sleep(0.1)  # Simulate slow work.
    return f"Processed: {data}"


@pait(sync_to_thread=True)
def sync_route(data: str = Json.i(description="Data to process")) -> JSONResponse:
    """Synchronous route function using sync_to_thread."""
    result = sync_heavy_task(data)
    return JSONResponse({"result": result, "message": "Synchronous function executed in the thread pool"})


# Comparison: an async version without sync_to_thread.
async def async_route(data: str = Json.i(description="Data to process")) -> JSONResponse:
    """Regular async route function."""
    # In an async environment, synchronous work blocks the event loop.
    result = sync_heavy_task(data)
    return JSONResponse({"result": result, "message": "Async function executed synchronous work directly"})


app = Starlette(
    routes=[Route("/api/sync", sync_route, methods=["POST"]), Route("/api/async", async_route, methods=["POST"])]
)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
