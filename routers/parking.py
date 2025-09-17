from datetime import datetime
from fastapi import Depends, HTTPException, APIRouter
from typing import List
from baseConfig.dependencies import require_roles, get_current_user
from baseConfig.db import fetch_one, fetch_all, update, insert
from baseConfig.models import ParkingLotDetails, FullParkingLotResponse, ParkingLotUpdateRequest, ParkingAvailabilityResponse, UpdateAvailabilityRequest, UpdateAvailabilityResponse, BulkUpdateRequest

admin_role_required = require_roles(["admin"])
guard_role_required = require_roles(["guard"])
common_role_required = require_roles(["employee", "guard"])

router_admin = APIRouter(tags=["Admin - Parking Lot Management"], dependencies=[Depends(admin_role_required)])
router_guard = APIRouter(tags=["Parking - Guard"], dependencies=[Depends(guard_role_required)])
router = APIRouter(tags=["Parking"], dependencies=[Depends(common_role_required)])


def get_parking_lot_by_code(code: str) -> FullParkingLotResponse:
    response = fetch_one(table="parking_lot", filters={"code": code})
    if response.get("error"):
        raise HTTPException(status_code=500, detail=response["error"])
    lot = response.get("data")
    if not lot:
        raise HTTPException(status_code=404, detail="Parking lot not found")
    return FullParkingLotResponse(**lot)

@router_admin.get("/parking_lots", response_model=List[FullParkingLotResponse])
def get_parking_lots(current_user=Depends(get_current_user)):
    response = fetch_all(table="parking_lot")
    if response.get("error"):
        raise HTTPException(status_code=500, detail=response["error"])

    return response.get("data", [])

@router_admin.post("/add_parking_lot", dependencies=[Depends(admin_role_required)])
def add_parking_lot(parking_lot: ParkingLotDetails, current_user=Depends(get_current_user)):
    existing = fetch_one(table="parking_lot", filters={"code": parking_lot.code})
    if existing.get("error"):
        raise HTTPException(status_code=500, detail=existing["error"])
    
    if existing.get("data"):
        raise HTTPException(status_code=400, detail="Parking lot already exists")
    
    response = insert(
        table="parking_lot", 
        data={
            "code": parking_lot.code,
            "name": parking_lot.name,
            "type": parking_lot.type.lower(),
            "capacity": parking_lot.capacity,
            "availability": parking_lot.capacity,
            "created_at": datetime.now().isoformat()
        }
    )

    if response.get("error"):
        raise HTTPException(status_code=500, detail=response.get("error"))
    return {"message": "Parking lot added successfully"}

@router_admin.post("/update_parking_lot", dependencies=[Depends(admin_role_required)])
def update_parking_lot(parking_lot: ParkingLotUpdateRequest, current_user=Depends(get_current_user)):
    existing = fetch_one(table="parking_lot", filters={"code": parking_lot.code})
    if existing.get("error"):
        raise HTTPException(status_code=500, detail=existing["error"])
    
    if not existing.get("data"):
        raise HTTPException(status_code=404, detail="Parking lot not found")
    
    sanitized_data = {k: v for k, v in parking_lot.model_dump().items() if v is not None and k != "code"}
    if not sanitized_data:
        return {"message": "Nothing to Update"}
    response = update(
        table="parking_lot", 
        data=sanitized_data,
        filters={"code": parking_lot.code}
    )

    if response.get("error"):
        raise HTTPException(status_code=500, detail=response.get("error"))
    return {"message": f"Parking lot: {parking_lot.code} successfully updated with {sanitized_data}"}

@router.get("/availability", response_model=List[ParkingAvailabilityResponse])
def check_availability(current_user=Depends(get_current_user)):
    response = fetch_all(table="parking_lot")
    if response.get("error"):
        raise HTTPException(status_code=500, detail=response["error"])

    data_set = []
    for lot in response.get("data", []):
        data_set.append(ParkingAvailabilityResponse(**lot))
    return data_set

@router_guard.post("/update_availability", response_model=UpdateAvailabilityResponse)
def update_availability(req: UpdateAvailabilityRequest, current_user=Depends(get_current_user)):
    # Fetch current parking lot details
    lot = get_parking_lot_by_code(req.parking_lot_code)
    current_availability = lot.availability
    capacity = lot.capacity
    final_response = {
        "code": lot.code,
        "name": lot.name,
        "type": lot.type,
        "availability": current_availability,
        "updated_at": lot.updated_at,
        "message": None
    }

    # Compute new availability
    if req.event_type.lower() == "in":
        if current_availability <= 0:
            final_response.update({"availability": 0, "message": "Parking lot is full"})
            return UpdateAvailabilityResponse(**final_response)
        new_availability = current_availability - 1
    elif req.event_type.lower() == "out":
        if current_availability >= capacity:
            final_response.update({"availability": capacity, "message": "Parking lot is empty"})
            return UpdateAvailabilityResponse(**final_response)
        new_availability = current_availability + 1
    else:
        raise HTTPException(status_code=400, detail="Invalid event type. Must be 'in' or 'out'")

    # Update the parking lot availability
    update_info = {"availability": new_availability, "updated_at": datetime.now().isoformat()}
    update_response = update(
        table="parking_lot",
        data=update_info,
        filters={"code": req.parking_lot_code}
    )

    if update_response.get("error"):
        raise HTTPException(status_code=500, detail=update_response["error"])

    final_response.update({
        "availability": new_availability,
        "updated_at": update_info["updated_at"],
        "message": "Availability updated successfully"
    })
    return UpdateAvailabilityResponse(**final_response)

@router_guard.post("/bulk_update", response_model=UpdateAvailabilityResponse)
def bulk_update_availability(req: BulkUpdateRequest, current_user=Depends(get_current_user)):
    # Fetch current parking lot details
    lot = get_parking_lot_by_code(req.parking_lot_code)
    if req.new_availability < 0 or req.new_availability > lot.capacity:
        raise HTTPException(status_code=400, detail="New availability must be between 0 and the parking lot capacity")
    
    final_response = {
        "code": lot.code,
        "name": lot.name,
        "type": lot.type,
        "availability": lot.availability,
        "updated_at": lot.updated_at,
        "message": None
    }

    # Update the parking lot availability
    update_info = {"availability": req.new_availability, "updated_at": datetime.now().isoformat()}

    # Perform the update
    response = update(
        table="parking_lot",
        data=update_info,
        filters={"code": req.parking_lot_code}
    )
    
    if response.get("error"):
        raise HTTPException(status_code=500, detail=response["error"])
    
    final_response.update({
        "availability": req.new_availability,
        "updated_at": update_info["updated_at"],
        "message": "Bulk Availability updated successfully"
    })

    return UpdateAvailabilityResponse(**final_response)

