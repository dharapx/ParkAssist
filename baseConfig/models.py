from pydantic import BaseModel
from typing import List, Optional
from enum import Enum
from typing_extensions import Literal

# ----------------------------------------
# User Management Schemas
# ----------------------------------------

# Allowed user types at signup
class SignupUserRoleName(str, Enum):
    employee = "employee"
    guard = "guard"

class SignupRequest(BaseModel):
    employee_id: str
    company_email: str
    password: str
    user_role: SignupUserRoleName

class LoginRequest(BaseModel):
    company_email: str
    password: str

class ParkingLot(BaseModel):
    id: int
    code: str
    name: str
    type: str
    capacity: int
    available: int

class EventRequest(BaseModel):
    event_type: str  # "in" or "out"

class BulkUpdateRequest(BaseModel):
    available: int

class UserFilter(BaseModel):
    employee_id: Optional[str] = None
    company_email: Optional[str] = None
    user_status: Optional[str] = None

class UserResponse(BaseModel):
    employee_id: str
    company_email: str
    roles: List[str]
    user_status: str
    signup_time: str

class UserListResponse(BaseModel):
    users: List[UserResponse]

class ApprovalUpdateRequest(BaseModel):
    request_id: int
    approval_status: Literal["accepted", "rejected"]

class RoleModificationRequest(BaseModel):
    employee_id: str
    user_role: list[Literal["employee", "guard", "admin"]]

class userModResponse(BaseModel):
    employee_id: str
    company_email: str
    roles: List[str]
    user_status: str
    message: Optional[str] = None



# ----------------------------------------
# Parking Lot Management Schemas
# ----------------------------------------
class BaseParkingLot(BaseModel):
    code: str
    name: str
    type: str

class ParkingLotDetails(BaseParkingLot):
    capacity: int

class ParkingLotResponse(ParkingLotDetails):
    created_at: str
    updated_at: Optional[str] = None

class FullParkingLotResponse(ParkingLotResponse):
    availability: int
    
class ParkingLotUpdateRequest(BaseModel):
    code: str
    name: Optional[str] = None
    type: Optional[str] = None
    capacity: Optional[int] = None

class ParkingAvailabilityResponse(BaseParkingLot):
    availability: int
    updated_at: str

class UpdateAvailabilityRequest(BaseModel):
    parking_lot_code: str
    event_type: Literal["in", "out"]

class UpdateAvailabilityResponse(ParkingAvailabilityResponse):
    message: Optional[str] = None

# Request model
class BulkUpdateRequest(BaseModel):
    parking_lot_code: str
    new_availability: int
