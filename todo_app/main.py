from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from . import models, schemas, crud, database, auth
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from .database import get_db
from contextlib import asynccontextmanager
from todo_app.database import Base, engine

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield
app = FastAPI()

models.Base.metadata.create_all(bind=database.engine)

@app.post("/register/", response_model=schemas.UserOut)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(models.User).filter(models.User.username == user.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Пользователь с таким именем уже существует")

    hashed_pw = auth.pwd_context.hash(user.password)
    db_user = models.User(username=user.username, hashed_password=hashed_pw)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@app.post("/token", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = auth.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Неверный логин или пароль")
    access_token = auth.create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/tasks/", response_model=schemas.TaskOut)
def create(
    task: schemas.TaskCreate,
    db: Session = Depends(get_db),
    user: models.User = Depends(auth.get_current_user)
):
    return crud.create_task(db, task, user)

@app.get("/tasks/", response_model=list[schemas.TaskOut])
def read_tasks(
    sort_by: str = Query(None, enum=["title", "status", "created_at"]),
    db: Session = Depends(get_db),
    user: models.User = Depends(auth.get_current_user)
):
    return crud.get_tasks(db, sort_by, user)

@app.get("/tasks/{task_id}", response_model=schemas.TaskOut)
def read_task(
    task_id: int,
    db: Session = Depends(get_db),
    user: models.User = Depends(auth.get_current_user)
):
    task = crud.get_task(db, task_id)
    if not task or task.owner_id != user.id:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    return task


@app.put("/tasks/{task_id}", response_model=schemas.TaskOut)
def update_task(
    task_id: int,
    task_update: schemas.TaskUpdate,
    db: Session = Depends(get_db),
    user: models.User = Depends(auth.get_current_user)
):
    task = crud.get_task(db, task_id)
    if not task or task.owner_id != user.id:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    return crud.update_task(db, task_id, task_update)


@app.delete("/tasks/{task_id}", response_model=schemas.TaskOut)
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    user: models.User = Depends(auth.get_current_user)
):
    task = crud.get_task(db, task_id)
    if not task or task.owner_id != user.id:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    return crud.delete_task(db, task_id)


@app.get("/tasks/top/", response_model=list[schemas.TaskOut])
def read_top_tasks(
    n: int = Query(5, gt=0),
    db: Session = Depends(get_db),
    user: models.User = Depends(auth.get_current_user)
):
    return crud.get_top_tasks(db, limit=n, user=user)


@app.get("/tasks/search/", response_model=list[schemas.TaskOut])
def search_tasks(
    q: str = Query(..., min_length=1),
    db: Session = Depends(get_db),
    user: models.User = Depends(auth.get_current_user)
):
    return crud.search_tasks(db, q, user)

