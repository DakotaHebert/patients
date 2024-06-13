import os
from datetime import datetime

import boto3
from fastapi import APIRouter
from fastapi import Depends
from fastapi import Request
from fastapi.security import HTTPBearer
from loguru import logger

from src.lib.dynamo import appointment_table

STEP_FUNCTION_ARN = "arn:aws:states:us-east-1:YOUR_ACCOUNT_ID:stateMachine:appointment_request"

router = APIRouter()

# Initialize Step Functions client
sfn_client = boto3.client("stepfunctions", region_name=AWS_REGION)

"""
Call would look like:
    POST /providers/provider123/reserve
    {
        "slot_id": "2023-07-12T15:00:00",
        "patient_id": "patient456",
        "task_token": "abcdef123456"
    }
"""


@router.post(
    "/providers/{provider_id}/reserve",
    status_code=200,
    tags=["providers"],
    dependencies=[Depends(HTTPBearer())],
)
@request_context(logger=logger)
def post_reserve_appointment(request: Request, provider_id: str, reserve_request: str):
    # Parse the slot_id to a datetime object
    try:
        slot_time = datetime.fromisoformat(reserve_request.slot_id)
    except ValueError as e:
        raise HTTPException(
            status_code=400, detail="Invalid slot_id format. Expected ISO 8601 format."
        )

    # Ensure the reservation is at least 24 hours in advance
    if slot_time < datetime.now() + timedelta(hours=24):
        raise HTTPException(
            status_code=400,
            detail="Reservations must be made at least 24 hours in advance.",
        )

    # Check if the slot is available
    availability_date = slot_time.strftime("%Y-%m-%d")
    start_time = slot_time.strftime("%H:%M")
    response = appointment_table.get_item(
        Key={"provider_id": provider_id, "availability_date": availability_date}
    )
    if (
        "Item" not in response
        or response["Item"]["start_time"] > start_time
        or response["Item"]["end_time"] <= start_time
    ):
        raise HTTPException(status_code=404, detail="Slot not available.")

    # Initiate the Step Function state machine
    sfn_client.start_execution(
        stateMachineArn=STEP_FUNCTION_ARN,
        input=json.dumps(
            {
                "provider_id": provider_id,
                "slot_id": reserve_request.slot_id,
                "patient_id": reserve_request.patient_id,
                "task_token": reserve_request.task_token,
            }
        ),
    )

    """
    Would need a script that 
    sfn_response = sfn_client.send_task_success(
        taskToken=task_token,
        output=json.dumps(sfn_return_info),
    )
    that tells the sfn to continue
    """

    # Store the reservation in DynamoDB
    table.put_item(
        Item={
            "provider_id": provider_id,
            "availability_date": availability_date,
            "slot_id": reserve_request.slot_id,
            "patient_id": reserve_request.patient_id,
            "status": "PENDING",
            "created_at": datetime.now().isoformat(),
        }
    )

    return {
        "message": "Reservation request initiated successfully, awaiting confirmation."
    }
