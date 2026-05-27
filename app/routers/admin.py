from fastapi import APIRouter, Depends, HTTPException, status
from app.dependencies import require_admin, User
from app.storage import get_storage, TaskStorage

router = APIRouter(prefix="/admin", tags=["admin"])

@router.get("/stats")
def get_stats(
    admin: User = Depends(require_admin),
    storage: TaskStorage = Depends(get_storage)
):
    return storage.get_stats()

@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task_admin(
    task_id: int,
    admin: User = Depends(require_admin),
    storage: TaskStorage = Depends(get_storage)
):
    if not storage.delete_task_admin(task_id):
        raise HTTPException(status_code=404, detail="Task not found")
