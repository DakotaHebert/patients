from enum import StrEnum

from aws_lambda_powertools.utilities.parser import BaseModel


class HealthStatus(StrEnum):
    ThumbsUp = ":thumbsup:"
    ThumbsDown = ":thumbsdown:"


class Health(BaseModel):
    region: Optional[str] = os.getenv("AWS_REGION", "unknown")
    version: Optional[str] = os.getenv("VERSION", "unknown")
    status: Optional[str] = HealthStatus.ThumbsUp
    downstreams: Optional[Dict] = {}
    last_updated: Optional[int] = 0
