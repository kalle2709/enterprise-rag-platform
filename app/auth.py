from fastapi import Header, HTTPException, status

API_KEYS = {
    "admin-key-123": "admin",
    "user-key-456": "user",
}


def get_current_role(x_api_key: str = Header(...)) -> str:
    role = API_KEYS.get(x_api_key)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key"
        )
    return role


def require_admin(role: str = Header(default=None, alias="x-api-key")) -> str:
    resolved_role = get_current_role(role)
    if resolved_role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return resolved_role