KUBECONF = '/home/vm1/.kube/config'

DATABASE_FILE = 'database.db'

SERVER_PORT = 8887
SERVICE_PORT = 80
TARGET_PORT = 9376

MAX_IDLE_TIME = 60 # time in seconds after which a service is considered idle. If the optimizer is running, it will stop the deployment of the service.
POLLING_INTERVAL = 10 # time in seconds after which the optimizer will poll the database for idle services.

CPU_LIMIT = "500m"
CPU_SCALING_THRESH = 50

MAX_RESPONSE_WAIT_TIME = 30
