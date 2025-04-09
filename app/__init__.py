import os
import logging
from logging.handlers import RotatingFileHandler
import time
from flask import Flask
from app.data_ingestor import DataIngestor
from app.task_runner import ThreadPool

if not os.path.exists('results'):
    os.mkdir('results')

webserver = Flask(__name__)
webserver.tasks_runner = ThreadPool()

# webserver.task_runner.start()

webserver.data_ingestor = DataIngestor("./nutrition_activity_obesity_usa_subset.csv")

webserver.job_counter = 1

logger = logging.getLogger('webserver')
logger.setLevel(logging.INFO)

log_file = "webserver.log"
max_size = 10 * 1024 * 1024  # 10 MB
backup_count = 5

handler = RotatingFileHandler(log_file, maxBytes=max_size, backupCount=backup_count)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

handler.setFormatter(formatter)
handler.formatTime = lambda record, datefmt: time.strftime(datefmt, time.gmtime(record.created))

if not logger.handlers:
    logger.addHandler(handler)

webserver.logger = logger


from app import routes
