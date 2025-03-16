from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends
from sqlmodel import Session

from crud import create_task, get_tasks, get_top_tasks, search_tasks, update_task, delete_task, task_by_id
from database import get_session, init_db
from schemas import TaskCreate, TaskUpdate, TaskRead


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(lifespan=lifespan)


@app.post("/tasks/", response_model=TaskRead)
def add_task(task: TaskCreate, session: Session = Depends(get_session)):
    return create_task(session, task)


@app.get("/tasks/", response_model=list[TaskRead])
def list_tasks(sort_by: str = None, session: Session = Depends(get_session)):
    return get_tasks(session, sort_by)


@app.get("/tasks/top/", response_model=list[TaskRead])
def top_tasks(top_n: int, session: Session = Depends(get_session)):
    return get_top_tasks(session, top_n)


@app.get("/tasks/search/", response_model=list[TaskRead])
def search_task(query: str, session: Session = Depends(get_session)):
    return search_tasks(session, query)


@app.get("/tasks/{task_id}/", response_model=TaskRead)
def get_task(task_id: str, session: Session = Depends(get_session)):
    return task_by_id(session, task_id)


@app.put("/tasks/{task_id}/", response_model=TaskRead)
def edit_task(task_id: int, task_update: TaskUpdate, session: Session = Depends(get_session)):
    return update_task(session, task_id, task_update)


@app.delete("/tasks/{task_id}/")
def remove_task(task_id: int, session: Session = Depends(get_session)):
    delete_task(session, task_id)
    return {"message": "Task deleted"}
