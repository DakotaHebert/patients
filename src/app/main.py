import os

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from mangum import Mangum

from src.routes import health

app = FastAPI(
    title="Patients",
    version="1.0.0",
    root_path=os.environ.get("STAGE_NAME", "/v1"),
    servers=[
        {
            "url": "http://localhost:8000",
            "description": "local",
        },
    ],
)

app.include_router(health.router)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
def exception_handler(request, ex):
    logger.exception(
        f"failed with exception",
        exc_info=ex,
        canonical=True,
    )
    return fastapi_gateway_response(
        httpStatusCode=500, body={"message": "Internal server error"}
    )


@app.exception_handler(RequestValidationError)
def validation_exception_handler(request, ex):
    logger.warning(f"Validation Exception occurred: {ex.errors()}")
    return fastapi_gateway_response(httpStatusCode=422, body={"detail": ex.errors()})


@logger.inject_lambda_context(
    log_event=True,
    clear_state=True,
)
def main(event, context):
    handler = Mangum(app, api_gateway_base_path="/v1")
    return handler(event, context)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
