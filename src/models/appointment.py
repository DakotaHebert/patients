from pydantic import BaseModel


class ReserveAppointmentRequest(BaseModel):
    slot_id: str  # ISO format datetime string for the slot being reserved
    patient_id: str
    task_token: str


class ProviderAvailability(BaseModel):
    start_time: str
    end_time: str


class AppointmentStatus(str, Enum):
    DENIED = "DENIED"
    EXPIRED = "EXPIRED"
    CONFIRMED = "CONFIRMED"
