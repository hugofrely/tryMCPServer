import asyncio
from typing import Callable


class AsyncTaskExecutor:
    def __init__(self):
        self.tasks = {}

    def add_task(self, name: str, task: Callable):
        self.tasks[name] = task

    def execute(self, name: str, *args, **kwargs):
        task = self.tasks[name]
        asyncio.create_task(asyncio.to_thread(task, *args, **kwargs))
