
import threading
import time

from pyspark.context import SparkContext
from pyspark.status import SparkJobInfo
from pyspark.status import SparkStageInfo

from decorators import accepts


class ProgressTracker(threading.Thread):

    @accepts(object, name=basestring, spark_context=SparkContext, rest_api_url=basestring, delay=int)
    def __init__(self, name='thread', spark_context=None, rest_api_url=None, delay=30):
        super(ProgressTracker, self).__init__(name=name)
        self._spark_context = spark_context
        self._rest_api_url = rest_api_url
        self._delay = delay

    def run(self):
        while True:
            job_status = self._get_job_status()
            # TODO: send job status data to rest api
            if job_status.jobs_complete():
                break
            time.sleep(self._delay)

    def _get_job_status(self):
        job_status_result = JobStatusResult()
        status = self._spark_context.statusTracker()
        for job_id in sorted(status.getJobIdsForGroup()):
            job_info = status.getJobInfo(job_id)
            job_status_result.add_job_info(job_info)
            for stage_id in sorted(job_info.stageIds):
                stage_info = status.getStageInfo(stage_id)
                job_status_result.add_stage_info_for_job(job_info, stage_info)
        return job_status_result



class JobStatusResult:

    def __init__(self):
        self._status_info = {}


    @accepts(object, SparkJobInfo)
    def add_job_info(self, job_info):
        if not self._status_info.has_key(job_info):
            self._status_info[job_info] = []

    @accepts(object, SparkJobInfo, SparkStageInfo)
    def add_stage_info_for_job(self, job_info, stage_info):
        if not self._status_info.has_key(job_info):
            self._status_info[job_info] = []
        if not stage_info in self._status_info.get(job_info):
            self._status_info[job_info].append(stage_info)

    def jobs_complete(self):
        if len(self._status_info.keys()) ==0:
            return False

        for job_info in self._status_info.keys():
            for stage_info in self._status_info.get(job_info):
                if stage_info.numCompletedTasks + stage_info.numFailedTasks < stage_info.numTasks:
                    return False
        return True

    def as_dict(self):
        result = {}
        for job_info in self._status_info.keys():
            job_id = job_info.jobId
            result[job_id] = {'status': job_info.status, 'stages': []}
            for stage_info in self._status_info.get(job_info):
                result.get(job_id).get('stages').append(dict(stage_info._asdict()))

        return result
