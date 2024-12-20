# import boto3
# def get_ec2_instances():
#     # Create EC2 client for us-west-1 region
#     ec2 = boto3.client('ec2', region_name='ap-south-1')
    
#     try:
#         # Get all instances
#         response = ec2.describe_instances()
#         instances = []
        
#         for reservation in response['Reservations']:
#             for instance in reservation['Instances']:
#                 instance_info = {
#                     'InstanceId': instance['InstanceId'],
#                     'InstanceType': instance['InstanceType'],
#                     'State': instance['State']['Name'],
#                     'LaunchTime': instance['LaunchTime'].strftime("%Y-%m-%d %H:%M:%S"),
#                 }
                
#                 # Add tags if they exist
#                 if 'Tags' in instance:
#                     instance_info['Tags'] = {tag['Key']: tag['Value'] for tag in instance['Tags']}
                
#                 # Add public IP if it exists
#                 if 'PublicIpAddress' in instance:
#                     instance_info['PublicIpAddress'] = instance['PublicIpAddress']
                
#                 instances.append(instance_info)
        
#         return instances
    
#     except Exception as e:
#         print(f"Error occurred: {str(e)}")
#         return None

# def main():
#     instances = get_ec2_instances()
#     if instances:
#         print(f"Found {len(instances)} instances:")
#         for instance in instances:
#             print("\nInstance Details:")
#             for key, value in instance.items():
#                 print(f"{key}: {value}")

# if __name__ == "__main__":
#     main()

from fastapi import FastAPI
import boto3

app = FastAPI()

def get_all_ec2_instances():
    """
    Retrieve EC2 instance details from all AWS regions.
    """
    ec2 = boto3.client("ec2")
    regions = ec2.describe_regions()["Regions"]
    region_names = [region["RegionName"] for region in regions]

    all_instances = []

    for region in region_names:
        ec2_client = boto3.client("ec2", region_name=region)
        try:
            response = ec2_client.describe_instances()
            for reservation in response["Reservations"]:
                for instance in reservation["Instances"]:
                    instance_info = {
                        "Region": region,
                        "InstanceId": instance["InstanceId"],
                        "InstanceType": instance["InstanceType"],
                        "State": instance["State"]["Name"],
                        "LaunchTime": instance["LaunchTime"].strftime("%Y-%m-%d %H:%M:%S"),
                    }

                    # Add tags if they exist
                    if "Tags" in instance:
                        instance_info["Tags"] = {tag["Key"]: tag["Value"] for tag in instance["Tags"]}

                    # Add public IP if it exists
                    if "PublicIpAddress" in instance:
                        instance_info["PublicIpAddress"] = instance["PublicIpAddress"]

                    all_instances.append(instance_info)
        except Exception as e:
            print(f"Error retrieving instances from region {region}: {str(e)}")

    return all_instances


@app.get("/GetAllEC2Regions")
async def get_all_ec2_regions():
    """
    FastAPI endpoint to fetch all EC2 instances across all regions.
    """
    try:
        instances = get_all_ec2_instances()
        if instances:
            return {"instances": instances, "status_code": 200}
        else:
            return {"error": "No EC2 instances found", "status_code": 404}
    except Exception as e:
        return {"error": str(e), "status_code": 500}



