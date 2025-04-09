"""Module for implementing a thread pool and task runner for job processing."""
import os
import json
from queue import Queue, Empty
from threading import Thread, Event, Lock

class ThreadPool:
    """A thread pool for processing submitted tasks concurrently."""

    def __init__(self):
        """Initialize the thread pool and start the worker threads."""
        num_threads = int(os.environ.get("TP_NUM_OF_THREADS", os.cpu_count()))
        self.task_queue = Queue()
        self.shutdown_event = Event()
        self.job_counter = 0
        self.jobs_status = {}
        self.status_lock = Lock()
        self.threads = []

        #Make sure the directory exists
        if not os.path.exists("results"):
            os.makedirs("results")

        #Start worker threads for the thread pool
        for _ in range(num_threads):
            thread = TaskRunner(self.task_queue, self.shutdown_event, self)
            thread.start()
            self.threads.append(thread)

    def submit(self, task):
        #Lock to safely increment job_counter and update job status
        with self.status_lock:
            job_id = f"job_id_{self.job_counter}"
            self.job_counter += 1
            self.jobs_status[job_id] = "running"
        #Add the task in the queue for processing
        self.task_queue.put({"id": job_id, "task": task})
        return job_id

    def register_task(self, task):
        return self.submit(task)

    def update_status(self, job_id, status):
        with self.status_lock:
            self.jobs_status[job_id] = status
        

    def get_status(self, job_id):
        with self.status_lock:
            return self.jobs_status.get(job_id)

    def get_all_statuses(self):
        with self.status_lock:
            return dict(self.jobs_status)

    def get_pending_jobs_count(self):
        return self.task_queue.qsize()

    def shutdown(self):
        #Set shutdown event to signal workers to stop
        self.shutdown_event.set()
        self.task_queue.join()
        for thread in self.threads:
            thread.join()

class TaskRunner(Thread):
    """Worker thread that processes tasks from the thread pool."""

    def __init__(self, task_queue, shutdown_event, thread_pool):
        """Initialize the task runner with a queue and shutdown event."""
        super().__init__()
        self.task_queue = task_queue
        self.shutdown_event = shutdown_event
        self.thread_pool = thread_pool

    def run(self):
        """Continuously process tasks until shutdown is signaled."""
        while not self.shutdown_event.is_set() or not self.task_queue.empty():
            try:
                job = self.task_queue.get(timeout=1)
                job_id = job["id"]
                task = job["task"]
                try:
                    #Execute the task
                    result = task()
                    #Then save the result to the required file
                    with open(
                        os.path.join("results", f"{job_id}.json"),
                        'w',
                        encoding = "utf-8"
                    ) as f:
                        json.dump({"status": "done", "data": result}, f)
                    #Update the job status
                    self.thread_pool.update_status(job_id, "done")
                except Exception as e: # pylint: disable=broad-exception-caught
                    #Same for error case and log the error also
                    with open(
                        os.path.join("results", f"{job_id}.json"),
                        'w',
                        encoding = "utf-8"
                    ) as f:
                        json.dump({"status": "error", "reason": str(e)}, f)
                    self.thread_pool.update_status(job_id, "error")
                finally:
                    self.task_queue.task_done()
            except Empty:
                continue