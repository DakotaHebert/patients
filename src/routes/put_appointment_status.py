import boto3
from uuid import uuid4

from fastapi import APIRouter
from fastapi import Depends
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer
from loguru import logger

from src.lib.dynamo import appointment_table

router = APIRouter()

@router.put(
    "/providers/{provider_id}/reserve/{status}",
    status_code=200,
    tags=["providers"],
    dependencies=[Depends(HTTPBearer())],
)
@request_context(logger=logger)
def put_appointment_status(provider_id: str, status: AppointmentStatus):
    # Validate the status
    if status not in [
        AppointmentStatus.DENIED,
        AppointmentStatus.EXPIRED,
        AppointmentStatus.CONFIRMED,
    ]:
        return JSONResponse(status_code=400, content={"message": "Invalid status"})

    if status == "CONFIRMED":
        sfn_client = boto3.client('stepfunctions')
        sfn_client.send_task_success(
            taskToken=task_token,
            output=json.dumps({'status': 'CONFIRMED'})  # Example output, can be modified as needed
        )
    appointment_table.update_item(
        Key={
            "provider_id": provider_id,
            "appointment_id":  str(uuid4())
        },
        UpdateExpression="SET appointment_status = :status",
        ExpressionAttributeValues={":status": status.value},
    )

    return JSONResponse(
        status_code=200,
        content={"message": "Appointment status updated successfully"},
    )