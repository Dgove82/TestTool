import requests
import json
from conf import *

# 查询数据
select_api = f'{jenkins_url}api/json?tree=jobs[name]'
response = requests.get(select_api, auth=(username, api_token))
jobs = response.json()
res = json.loads("""
{"_class": "hudson.model.Hudson", "assignedLabels": [{"name": "built-in"}], "mode": "NORMAL",
       "nodeDescription": "the Jenkins controller's built-in node", "nodeName": "", "numExecutors": 0,
       "description": null, "jobs": [{"_class": "hudson.model.FreeStyleProject", "name": "normal_pytest",
                                      "url": "http://10.211.55.19:8090/job/normal_pytest/", "color": "blue"},
                                     {"_class": "hudson.model.FreeStyleProject", "name": "pytest",
                                      "url": "http://10.211.55.19:8090/job/pytest/", "color": "blue"},
                                     {"_class": "hudson.model.FreeStyleProject", "name": "test",
                                      "url": "http://10.211.55.19:8090/job/test/", "color": "blue"}], "overallLoad": {},
       "primaryView": {"_class": "hudson.model.AllView", "name": "all", "url": "http://10.211.55.19:8090/"},
       "quietDownReason": null, "quietingDown": false, "slaveAgentPort": 8091,
       "unlabeledLoad": {"_class": "jenkins.model.UnlabeledLoadStatistics"}, "url": "http://10.211.55.19:8090/",
       "useCrumbs": true, "useSecurity": true,
       "views": [{"_class": "hudson.model.AllView", "name": "all", "url": "http://10.211.55.19:8090/"}]}
""")
print(json.dumps(jobs, indent=4))
