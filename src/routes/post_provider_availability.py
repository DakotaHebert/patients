from typing import List

from fastapi import Depends
from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer
from loguru import logger

from src.lib.dynamo import availibility_table


@router.post(
    "/providers/{provider_id}/availability/{date}",
    status_code=200,
    tags=["providers"],
    dependencies=[Depends(HTTPBearer())],
)
@request_context(logger=logger)
def post_provider_availability(
    request: Request,
    provider_id: str,
    date: str,
    availability: List[ProviderAvailability],
):
    provider_item = availibility_table.get_item(Key={"provider_id": provider_id})
    if "Item" not in provider_item:
        # Check if the provider exists
        return JSONResponse(status_code=404, content={"message": "Provider not found"})

    # Fetch current availability
    current_availability = provider_item.get("Item", {}).get("available_slots", {})

    # Update availability dictionary with new slots
    for slot in availability:
        current_availability[slot.start_time] = slot.end_time

    # Save the updated availability in DynamoDB
    availibility_table.put_item(
        Item={
            "provider_id": provider_id,
            "availability_date": date,
            "available_slots": current_availability,
        }
    )

    return JSONResponse(
        status_code=200, content={"message": "Availability posted successfully"}
    )
