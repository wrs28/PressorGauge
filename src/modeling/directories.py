import sqlalchemy
import os


# directory where project lives
project_dir = "/Users/wrs/Documents/insight/PressorGauge"


# directory where model lives
model_dir = "/Users/wrs/Documents/insight/PressorGauge/src/modeling"


# directory where mimic data lives
mimic_dir = "/Volumes/gaia/mimic"


# directory for logs
logs_dir = "/Users/wrs/Documents/insight/PressorGauge/logs"


engine = sqlalchemy.create_engine('postgres://postgres:postgres@localhost/PressorGauge')


def print_log(*message, mode="a"):
    message = [str(sub) for sub in message]
    print(*message)
    with open(os.path.join(logs_dir,"model.log"),mode) as f:
        f.write(" ".join(message) + "\n")
