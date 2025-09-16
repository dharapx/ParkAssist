from fastapi import Depends, HTTPException, APIRouter
from baseConfig.dependencies import require_roles, get_current_user
from baseConfig.db import fetch_all, update
from baseConfig.models import UserFilter, UserListResponse, ApprovalUpdateRequest, RoleModificationRequest, userModResponse

admin_role_required = require_roles(["admin"])

router = APIRouter(tags=["Admin - User Management"])

@router.get("/approval_requests", dependencies=[Depends(admin_role_required)])
def get_approval_requests(current_user=Depends(get_current_user)):
    response = fetch_all(table="user_onboard", filters={"approval_status": "pending"})

    if response.get("error"):
        raise HTTPException(status_code=500, detail=response["error"])

    return {"approval_requests": response.get("data", [])}

@router.post("/users", dependencies=[Depends(admin_role_required)], response_model=UserListResponse)
def get_users(filters: UserFilter, current_user=Depends(get_current_user)):
    # Convert Pydantic model to dict and remove None values
    sanitized_filters = {k: v for k, v in filters.model_dump().items() if v is not None}

    response = fetch_all(table="user_profile", filters=sanitized_filters)

    if response.get("error"):
        raise HTTPException(status_code=500, detail=response["error"])
    
    if response.get("error"):
        raise HTTPException(status_code=500, detail="Failed to fetch users")

    return UserListResponse(users=response.get("data", []))

@router.post("/approval_requests/update", dependencies=[Depends(admin_role_required)])
def update_approval_status(req: ApprovalUpdateRequest, current_user=Depends(get_current_user)):
    # Update the approval_status field in user_onboard table
    response = update(
        table="user_onboard",
        data={"approval_status": req.approval_status},
        filters={"request_id": req.request_id}
    )
    
    if response.get("error"):
        raise HTTPException(status_code=500, detail=response["error"])

    data_set = response.get("data")[0]
    
    data_set.update({"message": "Approval status updated successfully"})

    # return userModResponse(**data_set)
    return data_set

@router.post("/user_role/update", dependencies=[Depends(admin_role_required)])
def update_role(req: RoleModificationRequest, current_user=Depends(get_current_user)):
    
    # Update the roles field in user_profile table
    response = update(
        table="user_profile",
        data={"roles": req.user_role},
        filters={"employee_id": req.employee_id}
    )

    if response.get("error"):
        raise HTTPException(status_code=500, detail=response["error"])
    
    data_set = response.get("data")[0]
    if not data_set:
        raise HTTPException(status_code=404, detail="No matching user found for role update")
    
    data_set.update({"message": "User role updated successfully"})
    return userModResponse(**data_set)