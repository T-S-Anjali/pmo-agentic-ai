"""Auth router stub — JWT validation via Azure AD / OIDC."""
from fastapi import APIRouter

router = APIRouter()


@router.get("/me")
async def get_current_user():
    """Return the current authenticated user identity (stub)."""
    return {"user_id": "demo-user", "role": "pm", "name": "Demo User"}
