# Copyright 2014: Mirantis Inc.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from rally.benchmark.scenarios import base
from rally.benchmark.scenarios.sahara import utils
from rally.benchmark import validation
from rally import consts
from rally.openstack.common import log as logging

LOG = logging.getLogger(__name__)


class SaharaJob(utils.SaharaScenario):

    @validation.required_services(consts.Service.SAHARA)
    @validation.required_contexts("users", "sahara_image", "sahara_edp",
                                  "sahara_cluster")
    @base.scenario(context={"cleanup": ["sahara"]})
    def create_launch_job(self, job_type, configs, job_idx=0):
        """Test the Sahara EDP Job execution.

        :param job_type: The type of the Data Processing Job
        :param configs: The configs dict that will be passed to a Job Execution
        :param job_idx: The index of a job in a sequence. This index will be
        used to create different atomic actions for each job in a sequence

        This scenario Creates a Job entity and launches an execution on a
        Cluster.

        """

        tenant_id = self.clients("keystone").tenant_id
        mains = self.context()["sahara_mains"][tenant_id]
        libs = self.context()["sahara_libs"][tenant_id]

        name = self._generate_random_name(prefix="job_")
        job = self.clients("sahara").jobs.create(name=name,
                                                 type=job_type,
                                                 description="",
                                                 mains=mains,
                                                 libs=libs)

        cluster_id = self.context()["sahara_clusters"][tenant_id]

        if job_type.lower() == "java":
            input_id = None
            output_id = None
        else:
            input_id = self.context()["sahara_inputs"][tenant_id]
            output_id = self._create_output_ds().id

        self._run_job_execution(job_id=job.id,
                                cluster_id=cluster_id,
                                input_id=input_id,
                                output_id=output_id,
                                configs=configs,
                                job_idx=job_idx)

    @validation.required_services(consts.Service.SAHARA)
    @validation.required_contexts("users", "sahara_image", "sahara_edp",
                                  "sahara_cluster")
    @base.scenario(context={"cleanup": ["sahara"]})
    def create_launch_job_sequence(self, jobs):
        """Test the Sahara EDP Job sequence execution.

        :param jobs: The list of jobs that should be executed in one context

        This scenario Creates a Job entity and launches an execution on a
        Cluster for every job object provided.

        """

        for idx, job in enumerate(jobs):
            self.create_launch_job(job["job_type"], job["configs"], idx)
