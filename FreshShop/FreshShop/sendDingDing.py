import requests
import json

url = 'https://oapi.dingtalk.com/robot/send?access_token=3b2957bb82d4620fa4c6e35e1b314f84ab3f79ed3a764778a817669a523174b2'

headers = {
    'Content-Type': 'application/json',
    'Chartset' :'utf-8'
}

requests_data = {
    'msgtype' :'text',
    'text' :{
        'content' :'你瞅啥'
    },
    'at' :{
        'atMobiles' :[
        ],
    },
    'isAtAII' :True
}
sendData = json.dumps(requests_data)
response = requests.post(url ,headers=headers ,data=sendData)
content = response.json()
print(content)