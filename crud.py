from typing import Sequence

from sqlmodel import select, Session

from models import Task
from schemas import TaskCreate, TaskUpdate


def create_task(session: Session, task_create: TaskCreate) -> Task:
    task = Task(**task_create.dict())
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


def task_by_id(session: Session, task_id: str) -> Task:
    return session.get(Task, task_id)


def get_tasks(session: Session, sort_by: str = None) -> Sequence[Task]:
    query = select(Task)

    if sort_by == "title":
        query = query.order_by(Task.title)
    elif sort_by == "status":
        query = query.order_by(Task.status)
    elif sort_by == "created_at":
        query = query.order_by(Task.created_at.desc())

    return session.exec(query).all()


def get_top_tasks(session: Session, top_n: int) -> Sequence[Task]:
    return session.exec(select(Task).order_by(Task.priority.desc()).limit(top_n)).all()


def search_tasks(session: Session, query: str) -> Sequence[Task]:
    return session.exec(
        select(Task).where(Task.title.contains(query) | Task.description.contains(query))
    ).all()


def update_task(session: Session, task_id: int, task_update: TaskUpdate) -> Task:
    task = session.get(Task, task_id)
    if not task:
        return None

    for field, value in task_update.dict(exclude_unset=True).items():
        setattr(task, field, value)

    session.commit()
    session.refresh(task)
    return task


def delete_task(session: Session, task_id: int):
    task = session.get(Task, task_id)
    if task:
        session.delete(task)
        session.commit()
