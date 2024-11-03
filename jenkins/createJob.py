import requests

from conf import *
# 获取配置模版方法
# http://<jenkins-server-url>/job/<job-name>/config.xml

# 创建job
new_job_name = 'test_add_job'
create_job_api = f'{jenkins_url}createItem?name={new_job_name}'
headers = {'Content-Type': 'application/xml; charset=UTF-8'}
with open('config.xml', 'rb') as f:
    config = f.read()
response = requests.post(create_job_api, data=config, headers=headers, auth=(username, api_token))
if response.status_code == 200:
    print(f'Job {new_job_name} created successfully.')
else:
    print(f'Failed to create job {new_job_name}. Status code: {response.status_code}')
