import boto3

ec2 = boto3.client('ec2')


def get_public_ip_from_ec2(instance_id):
    response = ec2.describe_instances(InstanceIds=[instance_id])
    public_ip = response['Reservations'][0]['Instances'][0]['NetworkInterfaces'][0]['Association']['PublicIp']
    return public_ip


def get_private_ip_from_ec2(instance_id):
    response = ec2.describe_instances(InstanceIds=[instance_id])
    private_ip = response['Reservations'][0]['Instances'][0]['NetworkInterfaces'][0]['PrivateIpAddress']
    return private_ip
