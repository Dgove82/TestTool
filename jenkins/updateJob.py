import requests
import json
from conf import *
# 获取配置模版方法
# http://<jenkins-server-url>/job/<job-name>/config.xml

# 更新job配置
# job_name = 'test_add_job'
# update_job_api = f'{jenkins_url}job/{job_name}/config.xml'
# headers = {'Content-Type': 'application/xml; charset=UTF-8'}
# with open('config.xml', 'rb') as f:
#     config = f.read()
# response = requests.post(update_job_api, data=config, headers=headers, auth=(username, api_token))
# if response.status_code == 200:
#     print(f'Job {job_name} configuration updated successfully.')
# else:
#     print(f'Failed to update job {job_name} configuration. Status code: {response.status_code}')


# 获取config.xml
# job_name = 'test_add_job'
# fetch_job_api = f'{jenkins_url}job/{job_name}/config.xml'
# response = requests.get(fetch_job_api, auth=(username, api_token))
# if response.status_code == 200:
#     print(response.text)
# else:
#     print(f'Failed to fetch job {job_name} configuration. Status code: {response.status_code}')

# 删除job
# job_name = 'test_add_job'
# delete_job_api = f'{jenkins_url}job/{job_name}/'
# response = requests.delete(delete_job_api, auth=(username, api_token))
# if response.status_code == 204:
#     print(f'Job {job_name} delete successfully.')
# else:
#     print(f'Failed to delete job {job_name}. Status code: {response.status_code}')


# 检索版本
# job_name = 'test_add_job'
# retireving_builds = f'{jenkins_url}/job/{job_name}/api/xml'
# response = requests.get(retireving_builds, auth=(username, api_token))
# if response.status_code == 200:
#     print(response.text)
# else:
#     print(f'Failed to fetch job {job_name} configuration. Status code: {response.status_code}')

# 将任务构建加入队列，等待节点上线
job_name = 'test_add_job'
perform_build = f'{jenkins_url}job/{job_name}/build?delay=0sec'
response = requests.post(perform_build, auth=(username, api_token))
if response.status_code == 201:
    print(f'Successfully added job {job_name}')
else:
    print(f'Failed to add job {job_name}')

# 查询构建
# job_name = 'test_add_job'
# build_status = f'{jenkins_url}job/{job_name}/api/json'
# response = requests.get(build_status, auth=(username, api_token))
# if response.status_code == 200:
#     print(json.dumps(response.json(), indent=4))
# else:
#     print(f'Failed to get job info')

