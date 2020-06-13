import boto3

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
