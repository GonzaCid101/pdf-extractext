from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def health_check():
    return {"message": "API Conversor PDF funcionando"}
