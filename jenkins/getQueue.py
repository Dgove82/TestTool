from conf import *
import requests
import json

# 查询构建队列
queur_url = f'{jenkins_url}/queue/api/json'
resposne = requests.get(queur_url, auth=(username, api_token))
res = resposne.json()
if resposne.status_code == 200:
    print(json.dumps(res, indent=4))
else:
    print('fail to search')

# 取消队列中的作业
job_name = 'test_add_job'
for item in res['items']:
    if item['task']['name'] == job_name:
        queue_id = item['id']
        # 从队列中取出作业
        cancel_queue_api = f'{jenkins_url}queue/cancelItem?id={queue_id}'
        cancel_response = requests.post(cancel_queue_api, auth=(username, api_token))
        if cancel_response.status_code == 204:
            print(f'Job <job-name> has been removed from the queue.')
        else:
            print(f'Failed to remove job <job-name> from the queue. Status code: {cancel_response.status_code}')

