from bi import master
from sparkjobserver.api import SparkJob, build_problems


class JobScript(SparkJob):
    def validate(self, context, runtime, config):
        job_data = None
        problems = []
        if config.get('cfgpath', None):
            job_data = config.get('cfgpath')
        else:
            problems.append('Missing cfgpath data')
        if len(problems) == 0:
            return job_data
        else:
            return build_problems(problems)

    def run_job(self, context, runtime, data):
        confPath = data[0]
        print 'confPath', confPath
        master.main(confPath)
        return "Done the regression job"
