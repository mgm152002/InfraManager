from fastapi import FastAPI,UploadFile,File,Query
import json
import digitalocean
from dotenv import load_dotenv
import requests
import urllib
import subprocess
from fastapi.responses import FileResponse
import boto3

from typing import List, Optional

# Load environment variables from a .env file (if using .env)
load_dotenv()
import os
manager = digitalocean.Manager(token=os.getenv("Digital_Token"))
from fastapi.middleware.cors import CORSMiddleware



app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins; replace with specific origins if needed
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods
    allow_headers=["*"],  # Allows all headers
)


@app.get("/GetAllDO")
async def root():
   alldroplets = {"droplets":[],}

   droplets =  manager.get_all_droplets()
   
   for droplet in droplets:
            
      strdrop=str(droplet)
      strdrop=strdrop[10:]
      strdrop=strdrop[:-1]
      id=strdrop.split(" ")
      print(droplet)
      alldroplets["droplets"].append({"id":id[0],"name":id[1],"status":droplet.status})

     
   return(alldroplets)
@app.post("/SpoolDownDO")
async def shutdowm():
    droplets =  manager.get_all_droplets()
    for droplet in droplets:
        try: 
            droplet.shutdown()
        except:
            return ("error occured")
    return{"shutdown":"ok","status_code":200}
@app.post("/SpoolUpDO")
async def SpoolUp():
    droplets =  manager.get_all_droplets()
    for droplet in droplets:
        try: 
            droplet.power_on()
        except:
            return ("error occured")
    return{"poweron":"ok","status_code":200}
@app.post("/SpoolDownDO/{id}")
async def SpoolDown(id:int):
    try:
        droplet=manager.get_droplet(id)
        droplet.power_off()
        return{"status":200}
    except:
        return{"error"}
@app.post('/SpoolUpDO/{id}')
async def SpoolUp(id:int):
    try:
        droplet=manager.get_droplet(id)
        droplet.power_on()
        return{"status":200}
    except:
        return{"error"}

@app.get('/DetailsDO/{id}')
async def Details(id:int):
    url=f'https://api.digitalocean.com/v2/droplets/{id}'
    print(url)
    try:
        token=os.getenv("Digital_Token")
        response = requests.get(url,headers={'Content-Type': 'application/json',"Authorization": f"Bearer {token}"})

        
        data = response.json()
        return data
        
    except requests.exceptions.RequestException as e:
        print('Error:', e)
        return None
    
@app.post("/autoOsPatchDO/{id}")
 
async def Auto(id: int, ssh: UploadFile = File(...)):
    url = f'https://api.digitalocean.com/v2/droplets/{id}'
    print(url)
    
    try:
        # Retrieve the token from environment variables
        token = os.getenv("Digital_Token")
        if not token:
            raise EnvironmentError("Digital_Token not found in environment variables")
        
        # Fetch droplet details
        response = requests.get(
            url,
            headers={
                'Content-Type': 'application/json',
                "Authorization": f"Bearer {token}"
            }
        )
        response.raise_for_status()  # Raise an error for HTTP status codes 4xx/5xx
        
        data = response.json()
        ipv4 = data["droplet"]["networks"]["v4"][0]["ip_address"]
        print(f"Droplet IPv4: {ipv4}")
        
        # Save the uploaded SSH key to a file
        with open("Desktop", "wb") as f:
            f.write(await ssh.read())
        subprocess.run(['chmod', '700', './Desktop'])

        # Create inventory.ini file
        with open("inventory.ini", "w") as f:
            f.write(f"[myserver]\n{ipv4}\n[myserver:vars]\nansible_ssh_private_key_file=./Desktop\nansible_user=root")
        
        # Download the playbook
        playbook_url = "https://infraautomation.blr1.cdn.digitaloceanspaces.com/PatchingAutomation/os_patch.yml"
        playbook_filename = "os_patch.yml"
        response = requests.get(playbook_url)
        response.raise_for_status()
        
        with open(playbook_filename, "wb") as f:
            f.write(response.content)
        
        # Run the ansible-playbook command
        command = ["ansible-playbook", "-i", "inventory.ini", playbook_filename]
        output_file = "playbook_output.log"
        with open(output_file, "w") as f:
            subprocess.run(command, stdout=f, stderr=subprocess.STDOUT)
        
        # Cleanup temporary files
        os.remove("Desktop")
        os.remove("inventory.ini")
        os.remove(playbook_filename)
        #os.remove("playbook_output.log")

        # Return the output log file as a response
        return FileResponse(output_file, media_type="text/plain", filename="playbook_output.log" )
    
    except requests.exceptions.RequestException as e:
        print('Error during API request:', e)
        return {"error": "API request failed"}
    except Exception as e:
        print('Error:', e)
        return {"error": str(e)}



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







# def shutdown_ec2_instances(region):
#     """
#     Shut down all running EC2 instances in a specified AWS region.
    
#     Args:
#         region (str): The AWS region name (e.g., 'us-east-1').
    
#     Returns:
#         dict: A summary of the stopped instances and any errors.
#     """
#     ec2_client = boto3.client('ec2', region_name=region)
#     stopped_instances = []
#     errors = []

#     try:
#         # Retrieve all instances in the specified region
#         response = ec2_client.describe_instances(
#             Filters=[{"Name": "instance-state-name", "Values": ["running"]}]
#         )

#         # List of instance IDs to stop
#         instance_ids = [
#             instance["InstanceId"]
#             for reservation in response["Reservations"]
#             for instance in reservation["Instances"]
#         ]

#         if instance_ids:
#             print(f"Stopping the following instances in {region}: {instance_ids}")
#             stop_response = ec2_client.stop_instances(InstanceIds=instance_ids)

#             # Capture the stopped instances
#             for stopping_instance in stop_response["StoppingInstances"]:
#                 stopped_instances.append({
#                     "InstanceId": stopping_instance["InstanceId"],
#                     "PreviousState": stopping_instance["PreviousState"]["Name"],
#                     "CurrentState": stopping_instance["CurrentState"]["Name"]
#                 })
#         else:
#             print(f"No running instances found in region {region}.")
        
#     except Exception as e:
#         errors.append(str(e))
#         print(f"Error stopping instances in region {region}: {str(e)}")

#     return {"StoppedInstances": stopped_instances, "Errors": errors}


# if __name__ == "__main__":
#     # Example usage
#     region_name = "us-west-1"  # Replace with the desired AWS region
#     result = shutdown_ec2_instances(region_name)
#     print("Shutdown Summary:")
#     print(result)


# @app.post("/shutdown-ec2/{region}")
# async def shutdown_region(region: str):
#     result = shutdown_ec2_instances(region)
#     return result
def shutdown_ec2_instances(region, instance_ids=None):
    """
    Shut down EC2 instances in a specified AWS region. Stops specified instances 
    or all running instances if no IDs are provided.

    Args:
        region (str): The AWS region name (e.g., 'us-east-1').
        instance_ids (list[str], optional): List of instance IDs to stop. Defaults to None.

    Returns:
        dict: A summary of the stopped instances and any errors.
    """
    ec2_client = boto3.client('ec2', region_name=region)
    stopped_instances = []
    errors = []

    try:
        if not instance_ids:
            # Retrieve all running instances in the specified region
            response = ec2_client.describe_instances(
                Filters=[{"Name": "instance-state-name", "Values": ["running"]}]
            )

            # List of all running instance IDs
            instance_ids = [
                instance["InstanceId"]
                for reservation in response["Reservations"]
                for instance in reservation["Instances"]
            ]

        if instance_ids:
            print(f"Stopping the following instances in {region}: {instance_ids}")
            stop_response = ec2_client.stop_instances(InstanceIds=instance_ids)

            # Capture the stopped instances
            for stopping_instance in stop_response["StoppingInstances"]:
                stopped_instances.append({
                    "InstanceId": stopping_instance["InstanceId"],
                    "PreviousState": stopping_instance["PreviousState"]["Name"],
                    "CurrentState": stopping_instance["CurrentState"]["Name"]
                })
        else:
            print(f"No running instances found in region {region}.")
        
    except Exception as e:
        errors.append(str(e))
        print(f"Error stopping instances in region {region}: {str(e)}")

    return {"StoppedInstances": stopped_instances, "Errors": errors}

@app.post("/shutdown-ec2/{region}")
async def shutdown_region(region: str, instance_ids: Optional[List[str]] = Query(None)):
    """
    FastAPI endpoint to stop EC2 instances in a specified region.
    
    Args:
        region (str): The AWS region name (e.g., 'us-east-1').
        instance_ids (list[str], optional): List of instance IDs to stop.
    
    Returns:
        dict: Shutdown summary.
    """
    try:
        result = shutdown_ec2_instances(region, instance_ids)
        return result
    except Exception as e:
        return {"error": str(e)}    



# def start_ec2_instances(region):
#     """
#     Start all stopped EC2 instances in a specified AWS region.
    
#     Args:
#         region (str): The AWS region name (e.g., 'us-east-1').
    
#     Returns:
#         dict: A summary of the started instances and any errors.
#     """
#     ec2_client = boto3.client('ec2', region_name=region)
#     started_instances = []
#     errors = []

#     try:
#         # Retrieve all instances in the specified region
#         response = ec2_client.describe_instances(
#             Filters=[{"Name": "instance-state-name", "Values": ["stopped"]}]
#         )

#         # List of instance IDs to start
#         instance_ids = [
#             instance["InstanceId"]
#             for reservation in response["Reservations"]
#             for instance in reservation["Instances"]
#         ]

#         if instance_ids:
#             print(f"Starting the following instances in {region}: {instance_ids}")
#             start_response = ec2_client.start_instances(InstanceIds=instance_ids)

#             # Capture the started instances
#             for starting_instance in start_response["StartingInstances"]:
#                 started_instances.append({
#                     "InstanceId": starting_instance["InstanceId"],
#                     "PreviousState": starting_instance["PreviousState"]["Name"],
#                     "CurrentState": starting_instance["CurrentState"]["Name"]
#                 })
#         else:
#             print(f"No stopped instances found in region {region}.")
        
#     except Exception as e:
#         errors.append(str(e))
#         print(f"Error starting instances in region {region}: {str(e)}")

#     return {"StartedInstances": started_instances, "Errors": errors}


# if __name__ == "__main__":
#     # Example usage
#     region_name = "us-west-1"  # Replace with the desired AWS region
#     result = start_ec2_instances(region_name)
#     print("Start Summary:")
#     print(result)


# @app.post("/start-ec2/{region}")
# async def start_ec2(region: str):

    """
    FastAPI endpoint to start all stopped EC2 instances in a specified region.
    """
    try:
        result = start_ec2_instances(region)
        if result["StartedInstances"]:
            return {"message": "Instances started successfully", "details": result}
        else:
            raise HTTPException(status_code=404, detail="No stopped instances found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
def start_ec2_instances(region, instance_ids=None):
    """
    Start EC2 instances in a specified AWS region. Starts specified instances 
    or all stopped instances if no IDs are provided.

    Args:
        region (str): The AWS region name (e.g., 'us-east-1').
        instance_ids (list[str], optional): List of instance IDs to start. Defaults to None.

    Returns:
        dict: A summary of the started instances and any errors.
    """
    ec2_client = boto3.client('ec2', region_name=region)
    started_instances = []
    errors = []

    try:
        if not instance_ids:
            # Retrieve all stopped instances in the specified region
            response = ec2_client.describe_instances(
                Filters=[{"Name": "instance-state-name", "Values": ["stopped"]}]
            )

            # List of all stopped instance IDs
            instance_ids = [
                instance["InstanceId"]
                for reservation in response["Reservations"]
                for instance in reservation["Instances"]
            ]

        if instance_ids:
            print(f"Starting the following instances in {region}: {instance_ids}")
            start_response = ec2_client.start_instances(InstanceIds=instance_ids)

            # Capture the started instances
            for starting_instance in start_response["StartingInstances"]:
                started_instances.append({
                    "InstanceId": starting_instance["InstanceId"],
                    "PreviousState": starting_instance["PreviousState"]["Name"],
                    "CurrentState": starting_instance["CurrentState"]["Name"]
                })
        else:
            print(f"No stopped instances found in region {region}.")
        
    except Exception as e:
        errors.append(str(e))
        print(f"Error starting instances in region {region}: {str(e)}")

    return {"StartedInstances": started_instances, "Errors": errors}


@app.post("/start-ec2/{region}")
async def start_region(region: str, instance_ids: Optional[List[str]] = Query(None)):
    """
    FastAPI endpoint to start EC2 instances in a specified region.
    
    Args:
        region (str): The AWS region name (e.g., 'us-east-1').
        instance_ids (list[str], optional): List of instance IDs to start.
    
    Returns:
        dict: Start summary.
    """
    try:
        result = start_ec2_instances(region, instance_ids)
        return result
    except Exception as e:
        return {"error": str(e)}