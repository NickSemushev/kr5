from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Optional
from app.schemas import TaskCreate, Task, TaskStatusUpdate, TaskStatus
from app.storage import get_storage, TaskStorage
from app.dependencies import get_current_user, User

router = APIRouter(prefix="/tasks", tags=["tasks"])

@router.post("/", response_model=Task, status_code=status.HTTP_201_CREATED)
def create_task(
    task_data: TaskCreate,
    current_user: User = Depends(get_current_user),
    storage: TaskStorage = Depends(get_storage)
):
    return storage.create(task_data.model_dump(), current_user.id)

@router.get("/", response_model=list[Task])
def get_tasks(
    status_filter: Optional[str] = Query(None, alias="status"),
    min_priority: Optional[int] = Query(None, ge=1, le=5),
    current_user: User = Depends(get_current_user),
    storage: TaskStorage = Depends(get_storage)
):
    return storage.get_user_tasks(current_user.id, status_filter, min_priority)

@router.get("/{task_id}", response_model=Task)
def get_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    storage: TaskStorage = Depends(get_storage)
):
    task = storage.get_task(task_id)
    if not task or task.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.patch("/{task_id}/status", response_model=Task)
def update_task_status(
    task_id: int,
    status_update: TaskStatusUpdate,
    current_user: User = Depends(get_current_user),
    storage: TaskStorage = Depends(get_storage)
):
    task = storage.get_task(task_id)
    if not task or task.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Task not found")
    
    updated = storage.update_status(task_id, status_update.status)
    if not updated:
        raise HTTPException(status_code=404, detail="Task not found")
    return updated

@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    storage: TaskStorage = Depends(get_storage)
):
    task = storage.get_task(task_id)
    if not task or task.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if not storage.delete_task(task_id):
        raise HTTPException(status_code=404, detail="Task not found")
