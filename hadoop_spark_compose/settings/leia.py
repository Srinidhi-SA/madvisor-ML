from base import *
import datetime


# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DEBUG = False

ALLOWED_HOSTS = ['*']

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
#     }
# }

DATABASES = {
    'default1': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    },
    "default": {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'madvisor2',
        'USER': 'root',
        'PASSWORD': 'Marlabs@123',
        'HOST': '172.31.53.141',
        'PORT': '',
        }
}


PROJECT_APP = [
]

INSTALLED_APPS += PROJECT_APP


HADOOP_MASTER = '172.31.64.29'
"""
HADOOP_MASTER = '172.31.50.84'

YARN = {
    "host": HADOOP_MASTER,
    "port": 8088,
    "timeout": 30
}

HDFS = {

    # Give host name without http
    'host': HADOOP_MASTER,
    'port': '50070', #webhdfs port
    'uri': '/webhdfs/v1',
    'user.name': 'hduser',
    'hdfs_port': '9000', #hdfs port
    'base_path' : '/dev/dataset/'
}
"""

HADOOP_MASTER = '172.31.64.29'

YARN = {
    "host": HADOOP_MASTER,
    "port": 8088,
    "timeout": 30
}

HDFS = {

    # Give host name without http
    'host': HADOOP_MASTER,
    'port': '50070', #webhdfs port
    'uri': '/webhdfs/v1',
    'user.name': 'hduser',
    'hdfs_port': '9000', #hdfs port
    'base_path' : '/dev/dataset/'
}


EMR = {
    "emr_pem_path": "",
    "home_path": "/home/hadoop"
}

KAFKA = {
    'host': 'localhost',
    'port': '9092',
    'topic': 'my-topic'
}


JOBSERVER = {
    'host': '172.31.50.84',
    'port': '8090',
    'app-name': 'luke',
    'context': 'pysql-context',
    'master': 'bi.sparkjobs.JobScript',
    'metadata': 'bi.sparkjobs.JobScript',
    'model': 'bi.sparkjobs.JobScript',
    'score': 'bi.sparkjobs.JobScript',
    'filter': 'bi.sparkjobs.filter.JobScript',
    'robo': 'bi.sparkjobs.JobScript',
    'subSetting': 'bi.sparkjobs.JobScript',
    'stockAdvisor': 'bi.sparkjobs.JobScript'
}

THIS_SERVER_DETAILS = {
    "host": "madvisor2.marlabsai.com",
    "port": "80",
    "initail_domain": "/api"
}

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://172.31.53.141:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient"
        },
        "KEY_PREFIX": "local"
    }
}
CACHE_TTL = 60 * 15
REDIS_SALT = "123"


APPEND_SLASH=False
DATA_UPLOAD_MAX_MEMORY_SIZE = 1024*1024*1024

SCORES_SCRIPTS_FOLDER = '/home/ubuntu/mAdvisorScores/'
IMAGE_URL = "/api/get_profile_image/"

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = "smtp.office365.com"
EMAIL_PORT = 587
EMAIL_HOST_USER = "product@marlabs.com"
EMAIL_HOST_PASSWORD = "BImarlabs@123"
EMAIL_USE_TLS = ""
EMAIL_USE_SSL = ""

JOBSERVER_FROM_EMAIL = "ankush.patel@marlabs.com"
JOBSERVER_SENDTO_EMAIL_LIST = [
    'ankush.patel@marlabs.com',
    'vivekananda.tadala@marlabs.com',
    'gulshan.gaurav@marlabs.com',
    'mukesh.kumar@marlabs.com'
]
FUNNY_EMAIL_LIST = [
    'ankush.patel@marlabs.com',
    'sabretooth.rog@gmail.com'
]


JOBSERVER_EMAIL_TEMPLATE = "Please restart jobserver- IP-"

DEPLOYMENT_ENV = "prod"

HADOOP_CONF_DIR= False
HADOOP_USER_NAME="hduser"

CELERY_BROKER_URL = 'redis://172.31.53.141:6379/'
CELERY_RESULT_BACKEND = 'redis://172.31.53.141:6379/'
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE
CELERYD_MAX_TASKS_PER_CHILD = 4
CELERYD_CONCURRENCY = 2
# queue related settings
CELERY_DEFAULT_QUEUE = config_file_name_to_run.CONFIG_FILE_NAME
CELERY_QUEUES = {
    config_file_name_to_run.CONFIG_FILE_NAME: {
        "binding_key": "task.#",
        "exchange": config_file_name_to_run.CONFIG_FILE_NAME,
        "routing": config_file_name_to_run.CONFIG_FILE_NAME
    }
}

PEM_KEY = "/keyfiles/TIAA.pem"
ENABLE_KYLO = True
KYLO_UI_URL = "http://data-management.marlabsai.com"


USE_YARN_DEFAULT_QUEUE=True
# USE_YARN_DEFAULT_QUEUE=False

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'guardian.backends.ObjectPermissionBackend'
)


# SUBMIT_JOB_THROUGH_CELERY = False
SUBMIT_JOB_THROUGH_CELERY = True

CELERY_SCRIPTS_DIR="/home/hadoop/codebase/mAdvisor-api_2/scripts/"
END_RESULTS_SHOULD_BE_PROCESSED_IN_CELERY = True

CELERY_ONCE_CONFIG = {
  'backend': 'celery_once.backends.Redis',
  'settings': {
    'url': 'redis://172.31.53.141:6379/',
    'default_timeout': 60 * 60
  }
}

KYLO_SERVER_DETAILS = {
    "host": "34.200.233.5",
    "port" : 8088,
    "user": "ankush",
    "key_path": "~/.ssh/ankush.pem",
    "group_propertie_quote": "madvisor,user",
    "kylo_file_path":"/opt/kylo/"
}
