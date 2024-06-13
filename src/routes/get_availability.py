import os
from datetime import datetime
from datetime import timedelta
from typing import Optional

from boto3.dynamodb.conditions import Key
from cloud_apigw_middleware.lib import request_context
from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer
from loguru import logger

from src.lib.dynamo import availibility_table

AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
router = APIRouter()

# Call would look like GET /providers/provider123/availability?start_date=2023-09-07&end_date=2023-11-18
@router.get(
    "/providers/{provider_id}/availability",
    status_code=200,
    tags=["providers"],
    dependencies=[Depends(HTTPBearer())],
)
@request_context(logger=logger)
def get_availability(
    request: Request,
    provider_id: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
):
    # Validate and parse date parameters
    if start_date:
        start_date = datetime.strptime(start_date, "%Y-%m-%d")
    if end_date:
        end_date = datetime.strptime(end_date, "%Y-%m-%d")
    if start_date and end_date and start_date >= end_date:
        raise HTTPException(status_code=400, detail="End date must be after start date")

    # Default to the next 7 days if dates are not provided
    if not start_date:
        start_date = datetime.now()
    if not end_date:
        end_date = start_date + timedelta(days=7)

    # Query DynamoDB for availability within the date range
    response = availibility_table.query(
        KeyConditionExpression=Key("provider_id").eq(provider_id)
        & Key("availability_date").between(
            start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")
        )
    )

    # Process the query results into a list of available slots
    available_slots = []
    for item in response["Items"]:
        availability_date = datetime.strptime(item["availability_date"], "%Y-%m-%d")
        available_times = item.get("available_slots", {})

        for start, end in available_times.items():
            start_time = datetime.strptime(start, "%H:%M")
            end_time = datetime.strptime(end, "%H:%M")
            current_time = availability_date.replace(
                hour=start_time.hour, minute=start_time.minute
            )
            end_time = availability_date.replace(
                hour=end_time.hour, minute=end_time.minute
            )

            while current_time < end_time:
                if start_date <= current_time <= end_date:
                    available_slots.append(current_time.isoformat())
                current_time += timedelta(minutes=15)

    return JSONResponse(content={"available_slots": available_slots})
