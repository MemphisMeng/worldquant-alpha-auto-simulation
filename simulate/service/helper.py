import boto3, requests, json
from requests.auth import HTTPBasicAuth
from botocore.exceptions import ClientError

def delete_message(url,ReceiptHandle):
    sqs_client = boto3.client("sqs")
    _ = sqs_client.delete_message(
        QueueUrl=url,
        ReceiptHandle=ReceiptHandle
    )

# Pull messages from the queue
def receive_message(url, maxNumberOfMessages=10):
    sqs_client = boto3.client("sqs")
    response = sqs_client.receive_message(
        QueueUrl=url,
        MaxNumberOfMessages=maxNumberOfMessages,
        VisibilityTimeout=120    )
    result=response.get("Messages",[])
    return result

def authenticate():
    username, password = list(json.loads(get_secret()).items())[0]

    # 向API发送POST请求进行身份验证
    response = requests.post(
        url='https://api.worldquantbrain.com/authentication',
        auth=HTTPBasicAuth(username=username, password=password))
    response.raise_for_status()

    if response.status_code == 201:
        cookies = response.cookies
        return cookies
    else:
        raise ValueError("No cookies are received from the authentication.")
    
def get_secret():
    secret_name = "worldquant"
    region_name = "us-east-1"
    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        # For a list of exceptions thrown, see
        # https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
        raise e

    secret = get_secret_value_response['SecretString']
    return secret