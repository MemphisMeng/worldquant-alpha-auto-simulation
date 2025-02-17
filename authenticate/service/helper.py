import boto3, json, requests
from botocore.exceptions import ClientError
from requests.auth import HTTPBasicAuth

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

def authenticate():
    username, password = list(json.loads(get_secret()).items())[0]

    # 向API发送POST请求进行身份验证
    response = requests.post(
        url='https://api.worldquantbrain.com/authentication',
        auth=HTTPBasicAuth(username=username, password=password))
    response.raise_for_status()

    if response.status_code == 200:
        cookies = response.cookies
        return cookies
    else:
        raise ValueError("No cookies are received from the authentication.")
    
def publish_sqs(queue_url,message):
    sqs = boto3.client('sqs')
    # publish message to sqs per every game ingested
    r = sqs.send_message(
        QueueUrl=queue_url,
        MessageBody=(
            str(message)
        ),
        #DelaySeconds = delay_seconds               
    )
    return r