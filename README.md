# Le Stats Sportif - Assignment 1
## Mara Fichios 331CA

## Overview

For this assignment, I’ve implemented a multi-threaded Python server that processes various health-related statistics based on a CSV dataset. The server handles incoming requests for different statistical calculations like averages, differences from the global mean, and more, using threads.

The server exposes multiple API endpoints built with Flask. When a request is made to an endpoint, the server processes it by calculating the requested statistics and returns the results once the calculations are complete. 

Since processing the data can take time, the **task queue** and **thread pool** come in handy, as they can handle multiple requests concurrently. Each job is assigned a unique `job_id` which can be used to check the status of the request and retrieve the results later.

### The Flow Of The Program

1. **Job ID**: When a request is made, the server generates a unique `job_id` for each task. This ID allows clients to check/count the status of the job and check if it’s still being processed or if it’s done.

2. **Task Queue**: Each request (calculation) is placed into a task queue, and worker threads from a **ThreadPool** pick up the jobs for processing. This allows the server to handle multiple requests simultaneously without blocking.

3. **TaskRunner**: The worker threads, implemented in the `TaskRunner` class, get tasks from the queue and execute them. Once a task is completed, the result is saved to the file with the id of the task, and the task is marked as completed.

4. **Results**: After a job is done, the result is stored in a file (under the `results/` directory) named after the `job_id`. The client can check the status of a job and download the result by querying with the `job_id`.


### DataIngestor

The `DataIngestor` class is responsible for loading the CSV dataset and computing the required statistics. Important methods I've implemented:

- **Loading the Data**: The constructor (`__init__`) reads the CSV file and stores the data in a list of dictionaries. Each dictionary holds information about a state, the specific question asked, the data value, and its category.

- **Calculating Global Mean**: The `compute_global_mean` method calculates the average of all values for a given question across all states. This is done by filtering the dataset for the specified question and computing the mean of the `Data_Value` column.

- **State Mean**: The `compute_state_mean` method calculates the average for a specific state. It filters the dataset by both the state and the given question and computes the mean for that state.

- **State-wise Calculations**: The `compute_states_mean` method calculates the average for each state and sorts them based on the mean value. This is useful for answering requests that need a list of states ordered by their mean value for a specific question.

- **Best and Worst States**: The `compute_best5` and `compute_worst5` methods calculate the top 5 best and worst states based on a given question. The sorting criteria depend on whether the question asks for a higher or lower value to be considered better.

- **Category Mean**: The `compute_mean_by_category` and `compute_state_mean_by_category` methods compute the mean value for each category within a state, depending on the stratification categories (like age or income).


## TaskRunner & Thread Pool

The `TaskRunner` class represents the worker thread that processes the jobs. Here’s how it works:

1. **Job Processing**: Each thread constantly pulls tasks from the queue. When a task is fetched, the `run` method of `TaskRunner` is called, which executes the task and handles exceptions if any errors occur during the calculation.

2. **Storing Results**: After completing the task, the result is stored in a JSON file within the `results/` directory. The file is named after the `job_id`, so the client can easily retrieve the result later. Once the task is finished, the status of the job is updated, and the thread marks the task as done in the queue.

The `ThreadPool` class initializes a number of worker threads (based on the CPU count or an environment variable). It maintains a task queue and ensures that threads are working in parallel to handle multiple requests without blocking. When a new job (task) is **submitted** to the server, it's added to the task queue and processed by one of the worker threads. The server supports a **graceful shutdown**, which ensures that all tasks are completed before the server stops accepting new requests.




