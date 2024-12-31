from fastapi import FastAPI,UploadFile,File,Query,Form 
import json
import digitalocean
from dotenv import load_dotenv
import requests
import urllib
import subprocess
from fastapi.responses import FileResponse
import boto3
import os
from fastapi.responses import HTMLResponse
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
    



INSTANCE_TYPES = ["t2.micro", "t2.small", "t2.medium", "m5.large", "m5.xlarge"]
AWS_REGIONS = ["us-east-1", "us-west-1", "eu-west-1", "ap-south-1"]

@app.get("/", response_class=HTMLResponse)
async def create_instance_form():
    instance_type_options = "".join(
        f"<option value='{t}'>{t}</option>" for t in INSTANCE_TYPES
    )
    region_options = "".join(
        f"<option value='{r}'>{r}</option>" for r in AWS_REGIONS
    )

    form_html = f"""
    <html>
        <head>
            <title>Create EC2 Instance</title>
            <style>
                body {{
                    font-family: 'Arial', sans-serif;
                    background-color: #f4f4f9;
                    margin: 0;
                    padding: 0;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                }}
                h1 {{
                    color: #333;
                    text-align: center;
                    margin-bottom: 20px;
                }}
                form {{
                    background-color: #fff;
                    border-radius: 8px;
                    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
                    width: 400px;
                    padding: 30px;
                    box-sizing: border-box;
                    transition: transform 0.3s ease, box-shadow 0.3s ease;
                }}
                form:hover {{
                    transform: scale(1.02);
                    box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
                }}
                label {{
                    display: block;
                    margin-bottom: 8px;
                    color: #555;
                    font-weight: bold;
                }}
                input[type="text"], select {{
                    width: 100%;
                    padding: 10px;
                    margin-bottom: 20px;
                    border: 1px solid #ccc;
                    border-radius: 4px;
                    font-size: 16px;
                    box-sizing: border-box;
                    transition: border-color 0.3s ease, box-shadow 0.3s ease;
                }}
                input[type="text"]:focus, select:focus {{
                    border-color: #007BFF;
                    box-shadow: 0 0 4px #007BFF;
                }}
                input[type="submit"] {{
                    width: 100%;
                    background-color: #007BFF;
                    color: #fff;
                    border: none;
                    border-radius: 4px;
                    padding: 12px;
                    font-size: 16px;
                    cursor: pointer;
                    transition: background-color 0.3s ease, transform 0.2s ease;
                }}
                input[type="submit"]:hover {{
                    background-color: #0056b3;
                    transform: translateY(-2px);
                }}
                input[type="submit"]:active {{
                    transform: translateY(0);
                }}
                @media (max-width: 500px) {{
                    form {{
                        width: 90%;
                    }}
                }}
            </style>
        </head>
        <body>
            <h1>Create a New EC2 Instance</h1>
            <form action="/create-instance" method="post">
                <label for="instance_name">Instance Name:</label>
                <input type="text" id="instance_name" name="instance_name" required>
                <label for="instance_type">Instance Type:</label>
                <select id="instance_type" name="instance_type">
                    {instance_type_options}
                </select>
                <label for="region">Region:</label>
                <select id="region" name="region">
                    {region_options}
                </select>
                <input type="submit" value="Create Instance">
            </form>
        </body>
    </html>
    """
    return form_html    



@app.post("/create-instance")
async def create_instance(
    instance_name: str = Form(...),
    instance_type: str = Form(...),
    region: str = Form(...),
):
    """
    Create an EC2 instance based on user input.
    """
    try:
        # Create EC2 client
        ec2 = boto3.client("ec2", region_name=region)

        # Launch the instance
        response = ec2.run_instances(
            ImageId="ami-0819a8650d771b8be",  # Replace with an appropriate AMI ID for the region
            InstanceType=instance_type,
            MinCount=1,
            MaxCount=1,
            TagSpecifications=[
                {
                    "ResourceType": "instance",
                    "Tags": [{"Key": "Name", "Value": instance_name}],
                }
            ],
        )

        instance_id = response["Instances"][0]["InstanceId"]
        return {
            "message": "Instance created successfully!",
            "InstanceId": instance_id,
            "InstanceName": instance_name,
            "InstanceType": instance_type,
            "Region": region,
        }
    except Exception as e:
        return {"error": str(e)}
    



aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
aws_default_region = os.getenv("AWS_DEFAULT_REGION")

# Verify credentials are loaded
if not aws_access_key_id or not aws_secret_access_key:
    raise ValueError("AWS credentials not found in the environment.")

# Configure Boto3 with credentials
session = boto3.Session(
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
    region_name=aws_default_region,
)

# Example: Use the session to interact with AWS
ec2 = session.client("ec2")

# List EC2 instances as a test
try:
    response = ec2.describe_instances()
    print("Successfully connected to AWS and retrieved instances:")
    print(response)
except Exception as e:
    print(f"Error connecting to AWS: {e}")