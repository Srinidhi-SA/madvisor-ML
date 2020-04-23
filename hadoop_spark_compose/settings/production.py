from base import *
import datetime


# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DEBUG = False

ALLOWED_HOSTS = ['172.31.50.84', 'leia.marlabsai.com' , 'leia.marlabsai.com', 'localhost', 'luke.marlabsai.com', 'madvisor-leia.marlabsai.com',
                 'madvisor-luke.marlabsai.com', 'madvisor-luke.marlabsai.comleia.marlabsai.com',
                 'madvisor.marlabsai.com', 'madvisor1.marlabsai.com', 'madvisor2.marlabsai.com',
                 'webinar.marlabsai.com']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

PROJECT_APP = [
]

INSTALLED_APPS += PROJECT_APP
HADOOP_MASTER = '172.31.50.84'

YARN = {
    "host": HADOOP_MASTER,
    "port": 8088,
    "timeout": 30
}

HDFS = {

    # Give host name without http
    'host': HADOOP_MASTER,
    'port': '14000', #webhdfs port
    'uri': '/webhdfs/v1',
    'user.name': 'hadoop',
    'hdfs_port': '8020', #hdfs port
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
    'app-name': 'product_revamp',
    'context': 'pysql-context',
    'master': 'bi.sparkjobs.JobScript',
    'metadata': 'bi.sparkjobs.JobScript',
    'model': 'bi.sparkjobs.JobScript',
    'score': 'bi.sparkjobs.JobScript',
    'filter': 'bi.sparkjobs.filter.JobScript',

}

# dev api http://34.196.204.54:9092
THIS_SERVER_DETAILS = {
    "host": "madvisor.marlabsai.com",
    "port": "80",
    "initail_domain": "/api"
}

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
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
END_RESULTS_SHOULD_BE_PROCESSED_IN_CELERY = True
