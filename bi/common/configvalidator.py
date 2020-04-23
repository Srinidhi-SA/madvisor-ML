class ConfigValidator:
    def __init__(self,dataframe_context = None):
        self._dataframe_context = dataframe_context

    def check_for_target_column(self):
        targetCol = self._dataframe_context.get_result_column()
        if targetCol != "":
            return True
        else:
            return False

    def get_sanity_check(self):
        jobType = self._dataframe_context.get_job_type()
        if jobType not in ["subSetting","metaData","stockAdvisor"]:
            return self.check_for_target_column()
        else:
            return True
