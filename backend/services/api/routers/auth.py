from fastapi import APIRouter

from backend.services.api.dependencies import CurrentUserDep

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
    responses={404: {"description": "Not found"}},
)


@router.get("/me")
async def read_users_me(current_user: CurrentUserDep):
    """
    Get current user identity.
    """
    return current_user
