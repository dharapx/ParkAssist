from fastapi import APIRouter, HTTPException
from baseConfig.db import fetch_one, insert
from baseConfig.auth import hash_password, verify_password, create_access_token
from baseConfig.models import SignupRequest, LoginRequest


router = APIRouter(tags=["General"])

@router.post("/signup")
def signup(req: SignupRequest):
    existing = fetch_one(table="user_profile", filters={"employee_id": req.employee_id})
    if existing.get("error"):
        raise HTTPException(status_code=500, detail=existing["error"])
    
    if existing.get("data"):
        raise HTTPException(status_code=400, detail="Employee already exists")
    
    insert("user_profile", {
        "employee_id": req.employee_id,
        "company_email": req.company_email,
        "password": hash_password(req.password),
        "roles": [req.user_role],
        "user_status": "pending"
    })
    return {"status": "signup_requested"}

@router.post("/login")
def login(req: LoginRequest):
    response = fetch_one(table="user_profile", filters={"company_email": req.company_email})
    if response.get("error"):
        raise HTTPException(status_code=500, detail=response["error"])

    user = response.get("data")

    if not user or user["user_status"] != "active":
        raise HTTPException(status_code=403, detail="Invalid credentials or not approved")
    
    if not verify_password(req.password, user["password"]):
        raise HTTPException(status_code=403, detail="Invalid credentials")
    
    token = create_access_token(user_id=user["id"], roles=user["roles"])
    return {"access_token": token, "roles": user["roles"]}
