from fastapi import FastAPI,UploadFile,File
import json
import digitalocean
from dotenv import load_dotenv
import requests
import urllib
import subprocess
from fastapi.responses import FileResponse



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


@app.get("/GetAll")
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
@app.post("/SpoolDown")
async def shutdowm():
    droplets =  manager.get_all_droplets()
    for droplet in droplets:
        try: 
            droplet.shutdown()
        except:
            return ("error occured")
    return{"shutdown":"ok","status_code":200}
@app.post("/SpoolUp")
async def SpoolUp():
    droplets =  manager.get_all_droplets()
    for droplet in droplets:
        try: 
            droplet.power_on()
        except:
            return ("error occured")
    return{"poweron":"ok","status_code":200}
@app.post("/SpoolDown/{id}")
async def SpoolDown(id:int):
    droplet=manager.get_droplet(id)
    droplet.power_off()
    return{"status":200}
@app.post('/SpoolUp/{id}')
async def SpoolUp(id:int):
    droplet=manager.get_droplet(id)
    droplet.power_on()
    return{"status":200}

@app.get('/Details/{id}')
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
    
@app.post("/autoOsPatchDigitalOcean/")
 
async def Details(id: int, ssh: UploadFile = File(...)):
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
        return FileResponse(output_file, media_type="text/plain", filename="playbook_output.log")
    
    except requests.exceptions.RequestException as e:
        print('Error during API request:', e)
        return {"error": "API request failed"}
    except Exception as e:
        print('Error:', e)
        return {"error": str(e)}





    

