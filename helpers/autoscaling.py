import boto3
import logging

autoscaling = boto3.client('autoscaling')


def get_tag_value(autoscaling_group_name, tag_name):
    response = autoscaling.describe_tags(
        Filters=[
            {
                'Name': 'auto-scaling-group',
                'Values': [
                    autoscaling_group_name
                ]
            }
        ]
    )
    tags = response['Tags']

    for tag in tags:
        if tag['Key'] == tag_name:
            tag_value = tag['Value']
            return tag_value


def finish_autoscaling_lifecycle(message):
    if 'LifecycleHookName' in message and 'AutoScalingGroupName' in message:
        response = autoscaling.complete_lifecycle_action(
            LifecycleHookName=message['LifecycleHookName'],
            AutoScalingGroupName=message['AutoScalingGroupName'],
            InstanceId=message['EC2InstanceId'],
            LifecycleActionToken=message['LifecycleActionToken'],
            LifecycleActionResult='CONTINUE'
        )
        logging.info("Finish autoscaling lifecycle complete: {}".format(response))
    else:
        logging.error("No valid JSON message")
