import logging
import os

from spaceone.core.manager import BaseManager
from spaceone.inventory.plugin.collector.lib import (
    make_cloud_service_type,
    make_cloud_service_with_metadata,
    make_error_response,
    make_response,
)
from plugin.connector.jenkins_connector import JenkinsConnector

_LOGGER = logging.getLogger(__name__)
_CURRENT_DIR = os.path.dirname(__file__)
_METADATA_DIR = os.path.join(_CURRENT_DIR, "../metadata/")

class JenkinsManager(BaseManager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.provider = "jenkins"
        self.cloud_service_group = "cicd"
        self.cloud_service_type = "JenkinsJob"
        self.metadata_path = os.path.join(
            _METADATA_DIR, "cicd/jenkins.yaml"
        )

    def collect_resources(self, options, secret_data, schema):
        try:
            yield from self.collect_cloud_service_type(options, secret_data, schema)
            yield from self.collect_cloud_service(options, secret_data, schema)
        except Exception as e:
            yield make_error_response(
                error=e,
                provider=self.provider,
                cloud_service_group=self.cloud_service_group,
                cloud_service_type=self.cloud_service_type,
            )

    def collect_cloud_service_type(self, options, secret_data, schema):
        cloud_service_type = make_cloud_service_type(
            name=self.cloud_service_type,
            group=self.cloud_service_group,
            provider=self.provider,
            metadata_path=self.metadata_path,
            is_primary=True,
            is_major=True,
        )

        yield make_response(
            cloud_service_type=cloud_service_type,
            match_keys=[["name", "reference.resource_id", "account", "provider"]],
            resource_type="inventory.CloudServiceType",
        )

    def collect_cloud_service(self, options, secret_data, schema):
        jenkins_connector = JenkinsConnector(
            url=secret_data['jenkins-server-url'],
            username=secret_data['jenkins-username'],
            password=secret_data['jenkins-api-token']
        )
        jobs = jenkins_connector.get_jobs()

        for job in jobs:
            job_info = jenkins_connector.get_job_info(job['name'])
            cloud_service = make_cloud_service_with_metadata(
                name=job['name'],
                cloud_service_type=self.cloud_service_type,
                cloud_service_group=self.cloud_service_group,
                provider=self.provider,
                data=job_info,
                data_format='dict',
                metadata_path=self.metadata_path,
            )
            yield make_response(
                cloud_service=cloud_service,
                match_keys=[['name', 'reference.resource_id', 'account', 'provider']],
            )
