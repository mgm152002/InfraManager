from fastapi import FastAPI
import json
import digitalocean
from dotenv import load_dotenv

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



    

