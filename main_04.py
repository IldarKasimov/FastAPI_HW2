# Задание №4
# Напишите API для управления списком задач. Для этого создайте модель Task со следующими полями:
# ○ id: int (первичный ключ)
# ○ title: str (название задачи)
# ○ description: str (описание задачи)
# ○ done: bool (статус выполнения задачи)

# API должно поддерживать следующие операции:
# ○ Получение списка всех задач: GET /tasks/
# ○ Получение информации о конкретной задаче: GET /tasks/{task_id}/
# ○ Создание новой задачи: POST /tasks/
# ○ Обновление информации о задаче: PUT /tasks/{task_id}/
# ○ Удаление задачи: DELETE /tasks/{task_id}/
# Для валидации данных используйте параметры Field модели Task.
# Для работы с базой данных используйте SQLAlchemy и модуль databases.

from fastapi import FastAPI
from pydantic import BaseModel, Field
import sqlalchemy
import databases
from random import randint
from typing import List

DATABASE_URL = "sqlite:///mydatabaseHW.db"
database = databases.Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()

tasks = sqlalchemy.Table(
    'tasks',
    metadata,
    sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column('title', sqlalchemy.String(20)),
    sqlalchemy.Column('description', sqlalchemy.String(50)),
    sqlalchemy.Column('done', sqlalchemy.Boolean),
)

engine = sqlalchemy.create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
metadata.create_all(engine)

app = FastAPI()


class Task(BaseModel):
    title: str = Field(..., max_length=20)
    description: str = Field(..., max_length=50)
    done: bool = Field(..., ge=0, le=1)


class TaskIn(Task):
    id: int


# Заполнение таблицы
@app.get('/great_tasks/{count}')
async def great_tasks(count: int):
    for i in range(1, count + 1):
        query = tasks.insert().values(title=f'Name_task{i}', description=f'desc_task{i}',
                                      done=[False, True][randint(0, 1)])
        await database.execute(query)
    return {'msg': 'great task'}


# Получение списка всех задач
@app.get('/tasks/', response_model=List[TaskIn])
async def get_tasks():
    query = tasks.select()
    return await database.fetch_all(query)


# Получение информации о конкретной задаче
@app.get('/tasks/{task_id}/', response_model=TaskIn)
async def get_task(task_id: int):
    query = tasks.select().where(tasks.c.id == task_id)
    return await database.fetch_one(query)


# Создание новой задачи
@app.post('/tasks/', response_model=Task)
async def add_task(task: Task):
    query = tasks.insert().values(**task.model_dump())
    great_id = await database.execute(query)
    return await get_task(great_id)


# Обновление информации о задаче
@app.put('/tasks/{task_id}/', response_model=TaskIn)
async def update_task(task_id: int, task: Task):
    query = tasks.update().where(tasks.c.id == task_id).values(**task.model_dump())
    await database.execute(query)
    return await get_task(task_id)


# Удаление задачи
@app.delete('/tasks/{task_id}/')
async def del_task(task_id: int):
    query = tasks.delete().where(tasks.c.id == task_id)
    await database.execute(query)
    return {'msg': f'Deleted task with {task_id=}'}
