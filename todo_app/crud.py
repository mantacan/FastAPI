from sqlalchemy.orm import Session
from . import models, schemas

def create_task(db: Session, task: schemas.TaskCreate, user: models.User):
    db_task = models.Task(**task.dict(), owner_id=user.id)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

def get_tasks(db: Session, sort_by: str = None, user: models.User = None):
    query = db.query(models.Task).filter(models.Task.owner_id == user.id)

    if sort_by == "title":
        query = query.order_by(models.Task.title.asc())
    elif sort_by == "status":
        query = query.order_by(models.Task.status.asc())
    elif sort_by == "created_at":
        query = query.order_by(models.Task.created_at.asc())

    return query.all()

def get_task(db: Session, task_id: int):
    return db.query(models.Task).filter(models.Task.id == task_id).first()

def update_task(db: Session, task_id: int, task_update: schemas.TaskUpdate):
    task = get_task(db, task_id)
    if not task:
        return None
    for key, value in task_update.dict(exclude_unset=True).items():
        setattr(task, key, value)
    db.commit()
    db.refresh(task)
    return task

def delete_task(db: Session, task_id: int):
    task = get_task(db, task_id)
    if not task:
        return None
    db.delete(task)
    db.commit()
    return task

def search_tasks(db: Session, query: str, user: models.User):
    all_tasks = db.query(models.Task).filter(models.Task.owner_id == user.id).all()
    q = query.lower()
    return [
        task for task in all_tasks
        if q in (task.title or "").lower() or q in (task.description or "").lower()
    ]

def get_top_tasks(db: Session, limit: int = 5, user: models.User = None):
    return (
        db.query(models.Task)
        .filter(models.Task.owner_id == user.id)
        .order_by(models.Task.priority.desc())
        .limit(limit)
        .all()
    )
