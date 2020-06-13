import boto3

route53 = boto3.client('route53')


def get_zone_id(domain):
    response = route53.list_hosted_zones_by_name(
        DNSName=domain,
        MaxItems='1'
    )
    zone_id = response['HostedZones'][0]['Id']
    return zone_id


def format_record(domain, sub_domain):
    record = "{}.{}.".format(sub_domain, domain)
    return record


def change_resource_record_sets(domain, ip, sub_domain, operation):
    record = format_record(domain, sub_domain)
    zone_id = get_zone_id(domain)

    route53.change_resource_record_sets(
        HostedZoneId=zone_id,
        ChangeBatch={
            'Changes': [
                {
                    'Action': operation,
                    'ResourceRecordSet': {
                        'Name': record,
                        'Type': 'A',
                        'TTL': 60,
                        'ResourceRecords': [{'Value': ip}]
                    }
                }
            ]
        }
    )
    return record


def get_ip_from_resource_record_sets(domain, sub_domain):
    record = format_record(domain, sub_domain)
    zone_id = get_zone_id(domain)

    response = route53.list_resource_record_sets(
        HostedZoneId=zone_id
    )
    resource_record_sets = response['ResourceRecordSets']
    for resource_record_set in resource_record_sets:
        if resource_record_set['Name'] == record:
            ip = resource_record_set['ResourceRecords'][0]['Value']
            return ip
