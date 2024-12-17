from fastapi.testclient import TestClient
import requests
import main
import time

client = TestClient(main.app)

def test_getallDo_test():
    response = client.get("/GetAllDO")
    assert response.status_code == 200
    assert response.json() == {
  "droplets": [
    {
      "id": "452240096",
      "name": "centos-s-2vcpu-2gb-blr1-01",
      "status": "off"
    },
    {
      "id": "452635730",
      "name": "centos-s-1vcpu-1gb-amd-blr1-01-mattermost",
      "status": "off"
    },
    {
      "id": "452687350",
      "name": "centos-s-1vcpu-1gb-blr1-01-gitea",
      "status": "off"
    }
  ]
}

time.sleep(20)
    
def test_spoolUpDO():
    response = client.post("/SpoolUpDO")
    assert response.status_code == 200
    assert response.json() == {"poweron":"ok","status_code":200}
def test_SpoolDownDO():
    response = client.post("/SpoolDownDO")
    assert response.status_code == 200
    assert response.json() == {"shutdown":"ok","status_code":200}

def test_spoolUpDOid():
    response = client.post("/SpoolUpDO/452635730")
    assert response.json()=={"status":200}

def test_spoolDownDOid():
    response = client.post("/SpoolDownDO/452635730")
    assert response.json()=={"status":200}
def test_SpoolDownDO1():
    response = client.post("/SpoolDownDO")
    assert response.status_code == 200
    assert response.json() == {"shutdown":"ok","status_code":200}

def test_detailsIdDO():
    response = client.get("/DetailsDO/452635730")
    assert response.status_code == 200
    assert response.json()== {
  "droplet": {
    "id": 452635730,
    "name": "centos-s-1vcpu-1gb-amd-blr1-01-mattermost",
    "memory": 1024,
    "vcpus": 1,
    "disk": 25,
    "disk_info": [
      {
        "type": "local",
        "size": {
          "amount": 25,
          "unit": "gib"
        }
      }
    ],
    "locked": "false",
    "status": "off",
    "kernel": "null",
    "created_at": "2024-10-19T09:45:38Z",
    "features": [
      "droplet_agent",
      "private_networking"
    ],
    "backup_ids": [],
    "next_backup_window": "null",
    "snapshot_ids": [],
    "image": {
      "id": 135125666,
      "name": "9 Stream x64",
      "distribution": "CentOS",
      "slug": "centos-stream-9-x64",
      "public": "true",
      "regions": [
        "nyc3",
        "nyc1",
        "sfo1",
        "nyc2",
        "ams2",
        "sgp1",
        "lon1",
        "ams3",
        "fra1",
        "tor1",
        "sfo2",
        "blr1",
        "sfo3",
        "syd1"
      ],
      "created_at": "2023-06-22T20:26:46Z",
      "min_disk_size": 10,
      "type": "base",
      "size_gigabytes": 0.5,
      "description": "CentOS Stream 9 x64",
      "tags": [],
      "status": "available"
    },
    "volume_ids": [],
    "size": {
      "slug": "s-1vcpu-1gb-amd",
      "memory": 1024,
      "vcpus": 1,
      "disk": 25,
      "transfer": 1,
      "price_monthly": 7,
      "price_hourly": 0.01042,
      "regions": [
        "ams3",
        "blr1",
        "fra1",
        "lon1",
        "nyc1",
        "nyc2",
        "nyc3",
        "sfo3",
        "sgp1",
        "syd1",
        "tor1"
      ],
      "available": "true",
      "description": "Basic AMD",
      "networking_throughput": 2000,
      "disk_info": [
        {
          "type": "local",
          "size": {
            "amount": 25,
            "unit": "gib"
          }
        }
      ]
    },
    "size_slug": "s-1vcpu-1gb-amd",
    "networks": {
      "v4": [
        {
          "ip_address": "159.65.152.198",
          "netmask": "255.255.240.0",
          "gateway": "159.65.144.1",
          "type": "public"
        },
        {
          "ip_address": "10.122.0.3",
          "netmask": "255.255.240.0",
          "gateway": "10.122.0.1",
          "type": "private"
        }
      ],
      "v6": []
    },
    "region": {
      "name": "Bangalore 1",
      "slug": "blr1",
      "features": [
        "backups",
        "ipv6",
        "metadata",
        "install_agent",
        "storage",
        "image_transfer"
      ],
      "available": "true",
      "sizes": [
        "s-1vcpu-1gb",
        "s-1vcpu-1gb-amd",
        "s-1vcpu-1gb-intel",
        "s-1vcpu-1gb-35gb-intel",
        "s-1vcpu-2gb",
        "s-1vcpu-2gb-amd",
        "s-1vcpu-2gb-intel",
        "s-1vcpu-2gb-70gb-intel",
        "s-2vcpu-2gb",
        "s-2vcpu-2gb-amd",
        "s-2vcpu-2gb-intel",
        "s-2vcpu-2gb-90gb-intel",
        "s-2vcpu-4gb",
        "s-2vcpu-4gb-amd",
        "s-2vcpu-4gb-intel",
        "s-2vcpu-4gb-120gb-intel",
        "s-2vcpu-8gb-amd",
        "c-2",
        "c2-2vcpu-4gb",
        "s-2vcpu-8gb-160gb-intel",
        "s-4vcpu-8gb",
        "s-4vcpu-8gb-amd",
        "s-4vcpu-8gb-intel",
        "g-2vcpu-8gb",
        "s-4vcpu-8gb-240gb-intel",
        "gd-2vcpu-8gb",
        "g-2vcpu-8gb-intel",
        "gd-2vcpu-8gb-intel",
        "s-4vcpu-16gb-amd",
        "m-2vcpu-16gb",
        "c-4",
        "c2-4vcpu-8gb",
        "s-4vcpu-16gb-320gb-intel",
        "s-8vcpu-16gb",
        "m-2vcpu-16gb-intel",
        "m3-2vcpu-16gb",
        "c-4-intel",
        "m3-2vcpu-16gb-intel",
        "s-8vcpu-16gb-amd",
        "s-8vcpu-16gb-intel",
        "c2-4vcpu-8gb-intel",
        "g-4vcpu-16gb",
        "s-8vcpu-16gb-480gb-intel",
        "so-2vcpu-16gb-intel",
        "so-2vcpu-16gb",
        "m6-2vcpu-16gb",
        "gd-4vcpu-16gb",
        "so1_5-2vcpu-16gb-intel",
        "g-4vcpu-16gb-intel",
        "gd-4vcpu-16gb-intel",
        "so1_5-2vcpu-16gb",
        "s-8vcpu-32gb-amd",
        "m-4vcpu-32gb",
        "c-8",
        "c2-8vcpu-16gb",
        "s-8vcpu-32gb-640gb-intel",
        "m-4vcpu-32gb-intel",
        "m3-4vcpu-32gb",
        "c-8-intel",
        "m3-4vcpu-32gb-intel",
        "c2-8vcpu-16gb-intel",
        "g-8vcpu-32gb",
        "so-4vcpu-32gb-intel",
        "so-4vcpu-32gb",
        "m6-4vcpu-32gb",
        "gd-8vcpu-32gb",
        "so1_5-4vcpu-32gb-intel",
        "g-8vcpu-32gb-intel",
        "gd-8vcpu-32gb-intel",
        "so1_5-4vcpu-32gb",
        "m-8vcpu-64gb",
        "c-16",
        "c2-16vcpu-32gb",
        "m-8vcpu-64gb-intel",
        "m3-8vcpu-64gb",
        "c-16-intel",
        "m3-8vcpu-64gb-intel",
        "c2-16vcpu-32gb-intel",
        "g-16vcpu-64gb",
        "so-8vcpu-64gb-intel",
        "so-8vcpu-64gb",
        "m6-8vcpu-64gb",
        "gd-16vcpu-64gb",
        "so1_5-8vcpu-64gb-intel",
        "g-16vcpu-64gb-intel",
        "gd-16vcpu-64gb-intel",
        "so1_5-8vcpu-64gb",
        "m-16vcpu-128gb",
        "c-32",
        "c2-32vcpu-64gb",
        "m-16vcpu-128gb-intel",
        "m3-16vcpu-128gb",
        "c-32-intel",
        "m3-16vcpu-128gb-intel",
        "c2-32vcpu-64gb-intel",
        "c-48",
        "m-24vcpu-192gb",
        "g-32vcpu-128gb",
        "so-16vcpu-128gb-intel",
        "so-16vcpu-128gb",
        "m6-16vcpu-128gb",
        "gd-32vcpu-128gb",
        "so1_5-16vcpu-128gb-intel",
        "c2-48vcpu-96gb",
        "m-24vcpu-192gb-intel",
        "g-32vcpu-128gb-intel",
        "m3-24vcpu-192gb",
        "g-40vcpu-160gb",
        "gd-32vcpu-128gb-intel",
        "so1_5-16vcpu-128gb",
        "c-48-intel",
        "m3-24vcpu-192gb-intel",
        "m-32vcpu-256gb",
        "gd-40vcpu-160gb",
        "c2-48vcpu-96gb-intel",
        "so-24vcpu-192gb-intel",
        "so-24vcpu-192gb",
        "m6-24vcpu-192gb",
        "m-32vcpu-256gb-intel",
        "c-60-intel",
        "m3-32vcpu-256gb",
        "so1_5-24vcpu-192gb-intel",
        "m3-32vcpu-256gb-intel",
        "g-48vcpu-192gb-intel",
        "c2-60vcpu-120gb-intel",
        "gd-48vcpu-192gb-intel",
        "so1_5-24vcpu-192gb",
        "so-32vcpu-256gb-intel",
        "so-32vcpu-256gb",
        "m6-32vcpu-256gb",
        "so1_5-32vcpu-256gb-intel",
        "m-48vcpu-384gb-intel",
        "so1_5-32vcpu-256gb",
        "m3-48vcpu-384gb-intel"
      ]
    },
    "tags": [],
    "vpc_uuid": "87432e48-292a-4346-9801-cb7c8fec6ba7"
  }
}
    
def test_autoOsPatchDO():
    url = "http://127.0.0.1:8000/autoOsPatchDO/452635730"
    file_path = "/Users/madhushreegm/Desktop/Desktop"
    
    # Open the file and send the POST request
    with open(file_path, "rb") as file:
        response = requests.post(url, files={"file": file})
    
    # Assert the status code is 200
    assert response.status_code == 200
   