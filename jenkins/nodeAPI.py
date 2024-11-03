from conf import *
import requests
import json
import re

# 获取所有节点信息
# get_nodes_api = f'{jenkins_url}computer/api/json'
# response = requests.get(get_nodes_api, auth=(username, api_token))
# if response.status_code == 200:
#     print(json.dumps(response.json(), indent=4))
# else:
#     print(response.status_code)

# 获取特定节点信息
# node = 'test'
# get_node_api = f'{jenkins_url}computer/{node}/api/json'
# response = requests.get(get_node_api, auth=(username, api_token))
# if response.status_code == 200:
#     print(json.dumps(response.json(), indent=4))
# else:
#     print(response.status_code)

# 创建节点
# new_node = 'test'
# add_node_api = f'{jenkins_url}computer/doCreateItem?name={new_node}&type=hudson.slaves.DumbSlave'
# headers = {'Content-Type': 'application/x-www-form-urlencoded'}
#
# node_config = {
#     "name": new_node,
#     "nodeDescription": "",
#     "numExecutors": "1",
#     "remoteFS": "/work",
#     "labelString": new_node,
#     "mode": "NORMAL",
#     "": [
#         "hudson.slaves.JNLPLauncher",
#         "0"
#     ],
#     "launcher": {
#         "stapler-class": "hudson.slaves.JNLPLauncher",
#         "$class": "hudson.slaves.JNLPLauncher"
#     },
#     "retentionStrategy": {
#         "stapler-class": "hudson.slaves.RetentionStrategy$Always",
#         "$class": "hudson.slaves.RetentionStrategy$Always"
#     },
#     "nodeProperties": {
#         "stapler-class-bag": "true"
#     },
#     "type": "hudson.slaves.DumbSlave",
#     "Submit": ""}
#
# response = requests.post(add_node_api, data=f'json={json.dumps(node_config)}', headers=headers, auth=(username, api_token))
# if response.status_code == 200:
#     print(f'create {new_node} successfully')
# else:
#     print(f'create {new_node} failed')
#     print(response.text)

# manage/computer/{node_name}/jenkins-agent.jnlp 获取连接密钥
# jnlp_api = f'{jenkins_url}manage/computer/test/jenkins-agent.jnlp'
# response = requests.get(jnlp_api, auth=(username, api_token))
# res = response.content.decode('utf-8')
# print(res)
# print(re.findall(r'.*?<argument>(.*?)</argument>.*', res))
