"""This module defines the API routes for the webserver."""
import os
import json

from flask import request, jsonify
from app import webserver

# Example endpoint definition
@webserver.route('/api/post_endpoint', methods=['POST'])
def post_endpoint():
    """Handle POST requests to the /api/post_endpoint."""
    if request.method == 'POST':
        # Assuming the request contains JSON data
        data = request.json
        print(f"got data in post {data}")

        # Process the received data
        # For demonstration purposes, just echoing back the received data
        response = {"message": "Received data successfully", "data": data}

        # Sending back a JSON response
        return jsonify(response)

    return jsonify({"error": "Method not allowed"}), 405

@webserver.route('/api/get_results/<job_id>', methods=['GET'])
def get_response(job_id):
    """Check the status and return result of the job if done."""

    #Retreive the current status and return specific message
    status = webserver.tasks_runner.get_status(job_id)

    if status is None:
        webserver.logger.warning("[GET /api/get_results/%s] Invalid job ID", job_id)
        return jsonify({
            "status": "error",
            "reason": "Invalid job_id"
        }), 400

    if status == "running":
        webserver.logger.info("[GET /api/get_results/%s] Job still running", job_id)
        return jsonify({ "status": "running" }), 200

    result_path = os.path.join("results", f"{job_id}.json")

    #If finished, return the data and write it in the file
    try:
        with open(result_path, "r", encoding="utf-8") as f:
            result_data = json.load(f)
        webserver.logger.info("[GET /api/get_results/%s] Result successfully loaded", job_id)
        return jsonify({
            "status": "done",
            "data": result_data["data"]
        }), 200
    except (FileNotFoundError, json.JSONDecodeError) as e:
        webserver.logger.error("[GET /api/get_results/%s] Error loading result: %s", job_id, str(e))

        return jsonify({
            "status": "error",
            "reason": "Result file not found or invalid"
        }), 500


@webserver.route('/api/states_mean', methods=['POST'])
def states_mean_request():
    """Handle states_mean request."""

    webserver.logger.info("[POST /api/states_mean] Received request: %s", request.json)

    #Check if the server is shutting down
    if webserver.tasks_runner.shutdown_event.is_set():
        webserver.logger.warning("[POST /api/states_mean] Rejected - Server is shutting down")
        return jsonify({
            "status": "error",
            "reason": "shutting down"
        }), 503

    #Extract the data from the request
    data = request.json

    if not data or 'question' not in data:
        webserver.logger.error("[POST /api/states_mean] Missing question")
        return jsonify({"error": "Missing question parameter"}), 400

    #Call specific function that computes the result for this request
    def task():
        states_data = webserver.data_ingestor.compute_states_mean(data)
        return states_data

    #Register the job id and return it
    job_id = webserver.tasks_runner.register_task(task)

    webserver.logger.info("[POST /api/states_mean] Job submitted with ID: %s", job_id)

    return jsonify({"job_id": job_id})

#Same steps for all other requests
@webserver.route('/api/state_mean', methods=['POST'])
def state_mean_request():
    """Handle state_mean request."""
    webserver.logger.info("[POST /api/state_mean] Received request: %s", request.json)

    if webserver.tasks_runner.shutdown_event.is_set():
        webserver.logger.warning("[POST /api/state_mean] Rejected - Server is shutting down")
        return jsonify({
            "status": "error",
            "reason": "shutting down"
        }), 503
    data = request.json

    if not data or 'question' not in data:
        webserver.logger.error("[POST /api/state_mean] Missing question")
        return jsonify({"error": "Missing question parameter"}), 400

    def task():
        states_data = webserver.data_ingestor.compute_state_mean(data)
        return states_data

    job_id = webserver.tasks_runner.register_task(task)

    webserver.logger.info("[POST /api/state_mean] Job submitted with ID: %s", job_id)

    return jsonify({"job_id": job_id})


@webserver.route('/api/best5', methods=['POST'])
def best5_request():
    """Handle best5 request."""
    webserver.logger.info("[POST /api/best5] Received request: %s", request.json)

    if webserver.tasks_runner.shutdown_event.is_set():
        webserver.logger.warning("[POST /api/best5] Rejected - Server is shutting down")
        return jsonify({
            "status": "error",
            "reason": "shutting down"
        }), 503
    data = request.json

    if not data or 'question' not in data:
        webserver.logger.error("[POST /api/best5] Missing question")
        return jsonify({"error": "Missing question parameter"}), 400

    def task():
        best5_data = webserver.data_ingestor.compute_best5(data)
        return best5_data

    job_id = webserver.tasks_runner.register_task(task)

    webserver.logger.info("[POST /api/best5] Job submitted with ID: %s", job_id)
    return jsonify({"job_id": job_id})


@webserver.route('/api/worst5', methods=['POST'])
def worst5_request():
    """Handle worst5 request."""
    webserver.logger.info("[POST /api/worst5] Received request: %s", request.json)

    if webserver.tasks_runner.shutdown_event.is_set():
        webserver.logger.warning("[POST /api/worst5] Rejected - Server is shutting down")
        return jsonify({
            "status": "error",
            "reason": "shutting down"
        }), 503

    data = request.json

    if not data or 'question' not in data:
        webserver.logger.error("[POST /api/worst5] Missing question")
        return jsonify({"error": "Missing question parameter"}), 400

    def task():
        worst5_data = webserver.data_ingestor.compute_worst5(data)
        return worst5_data

    job_id = webserver.tasks_runner.register_task(task)

    webserver.logger.info("[POST /api/worst5] Job submitted with ID: %s", job_id)

    return jsonify({"job_id": job_id})


@webserver.route('/api/global_mean', methods=['POST'])
def global_mean_request():
    """Handle global_mean request."""
    webserver.logger.info("[POST /api/global_mean] Received request: %s", request.json)

    if webserver.tasks_runner.shutdown_event.is_set():
        webserver.logger.warning("[POST /api/global_mean] Rejected - Server is shutting down")
        return jsonify({
            "status": "error",
            "reason": "shutting down"
        }), 503

    data = request.json

    print(f"Global mean req recieved {data}")

    if not data or 'question' not in data:
        webserver.logger.error("[POST /api/global_mean] Missing question")
        return jsonify({"error": "Missing question parameter"}), 400

    def task():
        result = webserver.data_ingestor.compute_global_mean(data)
        return {"global_mean": result}

    job_id = webserver.tasks_runner.register_task(task)

    webserver.logger.info("[POST /api/global_mean] Job submitted with ID: %s", job_id)

    return jsonify({"job_id": job_id})

@webserver.route('/api/diff_from_mean', methods=['POST'])
def diff_from_mean_request():
    """Handle diff_from_mean request."""
    webserver.logger.info("[POST /api/diff_from_mean] Received request: %s", request.json)

    if webserver.tasks_runner.shutdown_event.is_set():
        webserver.logger.warning("[POST /api/diff_from_mean] Rejected - Server is shutting down")
        return jsonify({
            "status": "error",
            "reason": "shutting down"
        }), 503
    data = request.json

    if not data or 'question' not in data:
        webserver.logger.error("[POST /api/diff_from_mean] Missing question")
        return jsonify({"error": "Missing question parameter"}), 400

    def task():
        diff_data = webserver.data_ingestor.compute_diff_from_mean(data)
        return diff_data

    job_id = webserver.tasks_runner.register_task(task)
    webserver.logger.info("[POST /api/diff_from_mean] Job submitted with ID: %s", job_id)

    return jsonify({"job_id": job_id})


@webserver.route('/api/state_diff_from_mean', methods=['POST'])
def state_diff_from_mean_request():
    """Handle state_diff_from_mean request."""
    webserver.logger.info("[POST /api/state_diff_from_mean] Received request: %s", request.json)

    if webserver.tasks_runner.shutdown_event.is_set():
        webserver.logger.warning("[POST /api/state_diff_from_mean] Rejected - Server is shutting down")
        return jsonify({
            "status": "error",
            "reason": "shutting down"
        }), 503
    data = request.json

    if not data or 'question' not in data:
        webserver.logger.error("[POST /api/state_diff_from_mean] Missing question")
        return jsonify({"error": "Missing question parameter"}), 400
    
    def task():
        diff_data = webserver.data_ingestor.compute_diff_from_state_mean(data)
        return diff_data
    
    job_id = webserver.tasks_runner.register_task(task)
    webserver.logger.info("[POST /api/state_diff_from_mean] Job submitted with ID: %s", job_id)

    return jsonify({"job_id": job_id})


@webserver.route('/api/mean_by_category', methods=['POST'])
def mean_by_category_request():
    """Handle mean_by_category request."""
    webserver.logger.info("[POST /api/mean_by_category] Received request: %s", request.json)

    if webserver.tasks_runner.shutdown_event.is_set():
        webserver.logger.warning("[POST /api/mean_by_category] Rejected - Server is shutting down")
        return jsonify({
            "status": "error",
            "reason": "shutting down"
        }), 503

    data = request.json

    if not data or 'question' not in data:
        webserver.logger.error("[POST /api/mean_by_category] Missing question")
        return jsonify({"error": "Missing question parameter"}), 400
    
    def task():
        mean_data = webserver.data_ingestor.compute_mean_by_category(data)
        return mean_data
    
    job_id = webserver.tasks_runner.register_task(task)
    webserver.logger.info("[POST /api/mean_by_category] Job submitted with ID: %s", job_id)

    return jsonify({"job_id": job_id})


@webserver.route('/api/state_mean_by_category', methods=['POST'])
def state_mean_by_category_request():
    """Handle state_mean_by_category request."""
    webserver.logger.info("[POST /api/state_mean_by_category] Received request: %s", request.json)

    if webserver.tasks_runner.shutdown_event.is_set():
        webserver.logger.warning("[POST /api/state_mean_by_category] Rejected - Server is shutting down")
        return jsonify({
            "status": "error",
            "reason": "shutting down"
        }), 503

    data = request.json

    if not data or 'question' not in data:
        webserver.logger.error("[POST /api/state_mean_by_category] Missing question")
        return jsonify({"error": "Missing question parameter"}), 400
    
    def task():
        mean_data = webserver.data_ingestor.compute_state_mean_by_category(data)
        return mean_data
    
    job_id = webserver.tasks_runner.register_task(task)
    webserver.logger.info("[POST /api/state_mean_by_category] Job submitted with ID: %s", job_id)

    return jsonify({"job_id": job_id})

@webserver.route('/api/graceful_shutdown', methods=['GET'])
def graceful_shutdown():
    """Handle graceful shutdown request."""
    webserver.logger.info("[GET /api/graceful_shutdown] Request received")

    #Check if there are pending jobs and log it
    pending_jobs = webserver.tasks_runner.get_pending_jobs_count()
    if pending_jobs > 0:
        webserver.logger.info("[GET /api/graceful_shutdown] Still %d jobs running", pending_jobs)
        return jsonify({"status": "running"}), 200

    # Shutdown the task runner
    webserver.tasks_runner.shutdown()
    webserver.logger.info("[GET /api/graceful_shutdown] All jobs done. Shutdown initiated.")

    return jsonify({"status": "done"}), 200

@webserver.route('/api/jobs', methods=['GET'])
def jobs():
    """Return all job IDs and their current status."""
    job_statuses = webserver.tasks_runner.get_all_statuses()

    job_list = [{job_id: status} for job_id, status in job_statuses.items()]
    webserver.logger.info("[GET /api/jobs] Job statuses done: %s", job_list)

    return jsonify({
        "status": "done",
        "data": job_list
    }), 200

@webserver.route('/api/num_jobs', methods=['GET'])
def num_jobs():
    """Return number of jobs left to process."""
    num_jobs_left = webserver.tasks_runner.get_pending_jobs_count()

    if webserver.tasks_runner.shutdown_event.is_set() and num_jobs_left == 0:
        webserver.logger.info("[GET /api/num_jobs] No jobs left. Server is shutting down.")
        return jsonify({
            "status": "done",
            "num_jobs": 0
        }), 200

    webserver.logger.info("[GET /api/num_jobs] Number of jobs left: %d", num_jobs_left)

    return jsonify({
        "status": "done",
        "num_jobs": num_jobs_left
    }), 200


# You can check localhost in your browser to see what this displays
@webserver.route('/')
@webserver.route('/index')
def index():
    """Display all defined routes."""
    routes = get_defined_routes()
    msg = "Hello, World!\n Interact with the webserver using one of the defined routes:\n"

    # Display each route as a separate HTML <p> tag
    paragraphs = ""
    for route in routes:
        paragraphs = "".join(f"<p>{route}</p>")

    msg += paragraphs
    return msg

def get_defined_routes():
    """Return a list of defined routes with their methods."""
    routes = []
    for rule in webserver.url_map.iter_rules():
        methods = ', '.join(rule.methods)
        routes.append(f"Endpoint: \"{rule}\" Methods: \"{methods}\"")
    return routes