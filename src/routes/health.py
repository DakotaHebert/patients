import os

from fastapi import APIRouter

from models.health import Health

router = APIRouter()


sfn_client = boto3.client("stepfunctions", region_name=AWS_REGION)


@router.get("/health", response_model=Health)
def get_health():
    # Empty dynamo table to tell me if AWS Dynamo is up or not
    dynamo_health = dynamodb_client.scan(
        TableName="health_checks"
    )

    # List executions of the sfn 
    sfn_health = client.list_executions(
        stateMachineArn="arn:aws:states:us-east-1:123456789012:stateMachine:appointment_request",
        maxResults=10 
    )

    return health
