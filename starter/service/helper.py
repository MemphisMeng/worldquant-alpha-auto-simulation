import boto3, json

def publish_sqs(queue_url,message):
    sqs = boto3.client('sqs')
    # publish message to sqs per every game ingested
    r = sqs.send_message(
        QueueUrl=queue_url,
        MessageBody=(
            json.dumps(message)
        ),
        #DelaySeconds = delay_seconds               
    )
    return r