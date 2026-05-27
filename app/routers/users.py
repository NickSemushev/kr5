from fastapi import APIRouter, Depends, HTTPException
from app.dependencies import get_current_user, User
from app.storage import get_storage, TaskStorage

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/me", response_model=User)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    return current_user

@router.get("/{user_id}", response_model=dict)
def get_user_by_id(
    user_id: int,
    current_user: User = Depends(get_current_user),
    storage: TaskStorage = Depends(get_storage)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admin can view other users")
    
    tasks = storage.get_user_tasks(user_id)
    return {"user_id": user_id, "task_count": len(tasks)}
