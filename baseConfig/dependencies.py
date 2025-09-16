from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from baseConfig.auth import decode_access_token
from baseConfig.db import fetch_one
# from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
# from fastapi.security import OAuth2


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/user/login")


def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = decode_access_token(token)
    user_id = payload.get("sub")
    user_data = fetch_one("user_profile", {"id": user_id})
    user = user_data.get("data")
    if not user or not user["user_status"] == "active":
        raise HTTPException(status_code=403, detail="User not approved")
    user["roles"] = payload.get("roles", [])
    return user

def require_roles(allowed_roles: list[str]):
    def wrapper(current_user = Depends(get_current_user)):        
        if not any(role in current_user["roles"] for role in allowed_roles):
            raise HTTPException(status_code=403, detail="Insufficient privileges")
        return current_user
    return wrapper
