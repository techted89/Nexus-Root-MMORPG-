"""
Service for scheduling and managing server-side events.
"""

import asyncio
from typing import Callable, Coroutine

class EventService:
    """
    Manages the asynchronous execution of long-running commands using asyncio.
    """
    def __init__(self):
        self.tasks = set()

    async def schedule_event(self, delay: float, callback: Coroutine):
        """
        Schedules a coroutine to be executed after a specified delay.
        """
        async def task_wrapper():
            await asyncio.sleep(delay)
            await callback

        task = asyncio.create_task(task_wrapper())
        self.tasks.add(task)
        task.add_done_callback(self.tasks.discard)
        return task

    def cancel_event(self, task):
        """
        Cancels a scheduled event.
        """
        task.cancel()
