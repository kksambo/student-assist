from fastapi import APIRouter

router = APIRouter()

@router.get("/resources")
def get_resources():
    return [
        {"id": 1, "title": "Math Notes", "link": "https://tut.ac.za/math.pdf"},
        {"id": 2, "title": "Physics Slides", "link": "https://tut.ac.za/physics.pdf"}
    ]
