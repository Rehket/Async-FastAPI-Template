from fastapi import APIRouter


router = APIRouter()


@router.get("/")
def get_health():
    """
    Retrieve items.
    """
    return {"health": "ok"}
