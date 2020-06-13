import json
import logging

from helpers import autoscaling
from helpers import route53
from helpers import ec2


def process_record(message):
    lifecycle_transition = message['LifecycleTransition']
    autoscaling_group_name = message['AutoScalingGroupName']
    instance_id = message['EC2InstanceId']
    instance_id_replaced = instance_id.replace("i-", "")

    domain = autoscaling.get_tag_value(autoscaling_group_name, "AutoscalingDNS_Domain")
    ip_type = autoscaling.get_tag_value(autoscaling_group_name, "AutoscalingDNS_IPType")
    sub_domain_prefix = autoscaling.get_tag_value(autoscaling_group_name, "AutoscalingDNS_SubDomainPrefix")
    sub_domain = "{}-{}".format(sub_domain_prefix, instance_id_replaced)

    if lifecycle_transition == "autoscaling:EC2_INSTANCE_LAUNCHING":
        record_operation = "UPSERT"

        if ip_type == "public":
            public_ip = ec2.get_public_ip_from_ec2(instance_id)
            record = route53.change_resource_record_sets(domain, public_ip, sub_domain, record_operation)
            logging.info("Record {} is updated".format(record))
        elif ip_type == "private":
            private_ip = ec2.get_private_ip_from_ec2(instance_id)
            record = route53.change_resource_record_sets(domain, private_ip, sub_domain, record_operation)
            logging.info("Record {} is updated".format(record))
        else:
            logging.error("Unknown tag value AutoscalingDNS_IPType: {}".format(ip_type))

    elif lifecycle_transition == "autoscaling:EC2_INSTANCE_TERMINATING" or \
            lifecycle_transition == "autoscaling:EC2_INSTANCE_LAUNCH_ERROR":
        record_operation = "DELETE"
        ip = route53.get_ip_from_resource_record_sets(domain, sub_domain)
        if ip:
            record = route53.change_resource_record_sets(domain, ip, sub_domain, record_operation)
            logging.info("Record {} is deleted".format(record))
        else:
            logging.error("A record was not found in route53 for the terminated instance")
    else:
        logging.error("Unknown event type: {}".format(lifecycle_transition))


def lambda_handler(event, context):
    try:
        logging.info("Processing SNS event: {}".format(json.dumps(event)))
        for record in event['Records']:
            message = json.loads(record['Sns']['Message'])
            process_record(message)

    except Exception as ex:
        logging.error(ex)
        raise
