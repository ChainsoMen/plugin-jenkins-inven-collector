import logging
import jenkins

from spaceone.core.connector import BaseConnector

_LOGGER = logging.getLogger(__name__)

class JenkinsConnector(BaseConnector):
    def __init__(self, url: str, username: str, password: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client = jenkins.Jenkins(url, username=username, password=password)

    def get_jobs(self):
        try:
            jobs = self.client.get_all_jobs()
            return jobs
        except Exception as e:
            _LOGGER.error(f"Error fetching jobs from Jenkins: {e}")
            return []

    def get_job_info(self, job_name: str):
        try:
            job_info = self.client.get_job_info(job_name)
            return job_info
        except Exception as e:
            _LOGGER.error(f"Error fetching job info from Jenkins: {e}")
            return {}
