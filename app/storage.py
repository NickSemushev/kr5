from typing import Dict, List, Optional
from app.schemas import Task, TaskStatus

class TaskStorage:
    def __init__(self):
        self._tasks: Dict[int, Task] = {}
        self._next_id: int = 1

    def create(self, task_data: dict, owner_id: int) -> Task:
        task = Task(
            id=self._next_id,
            **task_data,
            owner_id=owner_id
        )
        self._tasks[task.id] = task
        self._next_id += 1
        return task

    def get_user_tasks(self, owner_id: int, status: Optional[str] = None, min_priority: Optional[int] = None) -> List[Task]:
        tasks = [t for t in self._tasks.values() if t.owner_id == owner_id]
        if status:
            tasks = [t for t in tasks if t.status == status]
        if min_priority:
            tasks = [t for t in tasks if t.priority >= min_priority]
        return tasks

    def get_task(self, task_id: int) -> Optional[Task]:
        return self._tasks.get(task_id)

    def update_status(self, task_id: int, status: TaskStatus) -> Optional[Task]:
        if task_id in self._tasks:
            task = self._tasks[task_id]
            updated_task = task.model_copy(update={"status": status})
            self._tasks[task_id] = updated_task
            return updated_task
        return None

    def delete_task(self, task_id: int) -> bool:
        if task_id in self._tasks:
            del self._tasks[task_id]
            return True
        return False

    def delete_task_admin(self, task_id: int) -> bool:
        return self.delete_task(task_id)

    def get_stats(self) -> dict:
        tasks = list(self._tasks.values())
        by_status = {
            "todo": len([t for t in tasks if t.status == "todo"]),
            "in_progress": len([t for t in tasks if t.status == "in_progress"]),
            "done": len([t for t in tasks if t.status == "done"])
        }
        return {
            "total_tasks": len(tasks),
            "by_status": by_status
        }

    def clear(self):
        self._tasks.clear()
        self._next_id = 1

_storage = TaskStorage()

def get_storage():
    return _storage
