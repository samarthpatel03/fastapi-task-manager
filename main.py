from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
from fastapi import HTTPException
import json
import os

FILE_NAME="tasks.json"

if os.path.exists(FILE_NAME):
    with open(FILE_NAME,"r") as f:
        tasks=json.load(f)
else:
    tasks=[]

def save_tasks():
    with open(FILE_NAME,"w") as f:
        json.dump(tasks,f,indent=4)

class Task(BaseModel):
    title: str

app = FastAPI()
id_counter=max([task["id"] for task in tasks],default=0)+1

@app.get("/")
def read_root():
    return {"Hello": "Welcome to Task Manager API"}

@app.post("/tasks")
def create_task(task:Task):
    global id_counter
    new_task={
        "id": id_counter,
        "title": task.title,
        "completed": False
    }
    tasks.append(new_task)
    save_tasks()
    id_counter+=1
    return new_task
    

class TaskResponse(BaseModel):
    id:int
    title:str
    completed:bool
@app.get("/tasks",response_model=list[TaskResponse])
def get_tasks(completed: Optional[bool]=None):
    if completed is None:
        return tasks
    filtered_tasks=[task for task in tasks if task["completed"]==completed]
    return filtered_tasks

@app.get("/tasks/{task_id}")
def get_task(task_id:int):
    for task in tasks:
        if task["id"]==task_id:
            return task
    raise HTTPException(status_code=404,detail="Task not found")

@app.put("/tasks/{task_id}")
def mark_complete(task_id:int):
    for task in tasks:
        if task["id"]==task_id:
            task["completed"]=True
            save_tasks()
            return task
    raise HTTPException(status_code=404,detail="Task not found")

@app.delete("/tasks/{task_id}")
def delete_task(task_id:int):
    for task in tasks:
        if task["id"]==task_id:
            tasks.remove(task)
            save_tasks()
            return {"message":"Task deleted"}
    raise HTTPException(status_code=404,detail="Task not found")