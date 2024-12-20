import boto3.session
from fastapi import FastAPI,UploadFile,File
import json
import digitalocean
from dotenv import load_dotenv
import requests
import urllib
import subprocess
from fastapi.responses import FileResponse
import boto3


regions= [
    #'ap-east-1',
    'ap-northeast-1',
    'ap-northeast-2',
    'ap-south-1',
    'ap-southeast-1',
    'ap-southeast-2',
    'ca-central-1',
    'eu-central-1',
    'eu-north-1',
    'eu-west-1',
    'eu-west-2',
    'eu-west-3',
    #'me-south-1',
    'sa-east-1',
    'us-east-1',
    'us-east-2',
    'us-west-1',
    'us-west-2'
    ]

# Load environment variables from a .env file (if using .env)
load_dotenv()
import os
manager = digitalocean.Manager(token=os.getenv("Digital_Token"))
from fastapi.middleware.cors import CORSMiddleware

session = boto3.Session(
    aws_access_key_id=os.getenv("aws_accesskey"),
    aws_secret_access_key=os.getenv("aws_secretekey"),
    region_name="us-west-1"
)



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


@app.get("/GetEc2")

async def getEc2():
    regions_dict = {}  # Initialize the dictionary to store results
    
    for region_name in regions:
        print(f"Region Name: {region_name}")
        
        ec2 = session.resource('ec2', region_name=region_name)
        instances = ec2.meta.client.describe_instances()
        
        instances_list = []  # Temporary list to store instances for this region
        
        for reservation in instances['Reservations']:
            for instance1 in reservation['Instances']:
                instance_info = {
                    'InstanceId': instance1['InstanceId'],
                    'InstanceType': instance1['InstanceType'],
                    'State': instance1['State']['Name'],
                    'LaunchTime': instance1['LaunchTime'].strftime("%Y-%m-%d %H:%M:%S"),
                }
                
                # Add tags if they exist
                if 'Tags' in instance1:
                    instance_info['Tags'] = {tag['Key']: tag['Value'] for tag in instance1['Tags']}
                
                # Add public IP if it exists
                if 'PublicIpAddress' in instance1:
                    instance_info['PublicIpAddress'] = instance1['PublicIpAddress']
                
                instances_list.append(instance_info)
        
        # Assign the list of instances to the region key in the dictionary
        if (instances_list!=[]):

            regions_dict[region_name] = instances_list

    return {"Ec2":[regions_dict]}

@app.post("/StopEc2/{id}/{region}")

def stopEc2(id:str,region:str):
    ec2=session.client('ec2',region_name=region)
    
    ec2.stop_instances(InstanceIds=[id])
    return{"ok":200}
@app.post("/StartEc2/{id}/{region}")

def stopEc2(id:str,region:str):
    ec2=session.client('ec2',region_name=region)
    
    ec2.start_instances(InstanceIds=[id])
    return{"ok":200}
   



