from bi.scripts import metadata
from sparkjobserver.api import SparkJob, build_problems


class JobScript(SparkJob):

    def validate(self, context, runtime, config):
        if config.get('input.strings', None):
            return config.get('input.strings')
        else:
            return build_problems(['config input.strings not found'])
        #return "Done"

    def run_job(self, context, runtime, data):
        inputpath = data[0]
        resultpath = data[1]
        metadata.main(inputpath,resultpath)
        return "Done the regression job"
