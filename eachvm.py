import docker
import requests
import datetime
import json
from flask import Flask
import boto3

lambda_client = boto3.client("lambda", region='ap-south-1')
app = Flask(__name__)

containers = dict()

users_in_vm = []
start_time = dict()
stop_time = dict()


def check_for_backup(mail):
    function = "backupLambda"
    # url = "https://example.com/api/endpoint"
    data = {'key': 'value'}
    # response = requests.post(url, json=data)
    # message = response.text
    # return (1 if message.equals("True") else 0)
    response = lambda_client.invoke(
        FunctionName=function,
        InvocationType='RequestResponse',
        Payload=json.dumps(data)
    )
    return response['Status']


def upload_data(mail, start_time, stop_time):
    function = "updation"
    # url = "https://example.com/api/endpoint"
    data = {"user_mail": mail, "start_time": start_time, "stop_time": stop_time}
    json_data = json.dumps(data)
    # headers = {"Content-Type": "application/json"}
    # response = requests.post(url, data=json_data, headers=headers)
    response = lambda_client.invoke(
        FunctionName=function,
        InvocationType='RequestResponse',
        Payload=json.dumps(data)
    )
    return response['Status']


def start_container(mail):
    mailc = mail.replace('@', '-')
    client = docker.from_env()
    container_name = mailc
    image_name = "flask:v1"
    container = client.containers.run(image_name, detach=True, name=container_name)
    containers[mailc] = container
    users_in_vm.append(mail)
    start_time[mail] = datetime.datetime.now()


def stop_container(mail):
    mailc = mail.replace('@', '-')
    containers[mailc].stop()
    containers[mailc].remove()
    stop_time[mail] = datetime.datetime.now()
    upload_data(mail, start_time[mail], stop_time[mail])
    check_for_backup(mail)  # backup_data(mail)


@app.route('/')
def hello_world():
    return "This is each VM server"


@app.route('/start/<mail>', methods=['POST'])
def start(mail):
    start_container(mail)
    return "Container started for {}".format(mail)


@app.route('/stop/<mail>', methods=['POST'])
def stop(mail):
    stop_container(mail)
    return "Container stopped for {}".format(mail)


if __name__ == '__main__':
    app.run(port=8000)
