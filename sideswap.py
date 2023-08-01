#!/usr/bin/env python
# coding: utf-8

import json
import sys
import requests
from websockets.sync.client import connect
import requests
import greenaddress as ga
import subprocess

MAINNET = {
    # USDt mainnet
    "asset": "ce091c998b83c78bb71a632313ba3760f1763d9cfcffae02258ffa9865a37bd2",
    "api_url": "wss://api.sideswap.io/json-rpc-ws"
}
SUBACCOUNT = 0
NET = MAINNET


def start_swap(net):
    with connect(net["api_url"]) as ws:
        ws.send(json.dumps(
            {
                "id": 1,
                "method": "subscribe_price_stream",
                "params": {
                    "asset": net["asset"],
                    "send_bitcoins": True,
                    "send_amount": 1666
                }
            }
        ))
        response = ws.recv()
        result = json.loads(response)["result"]
        ws.send(json.dumps(
            {
                "id": 2,
                "method": "start_swap_web",
                "params": {
                    "send_bitcoins": True,
                    "price": result["price"],
                    "asset": net["asset"],
                    "send_amount": result["send_amount"],
                    "recv_amount": result["recv_amount"],
                }
            }
        ))
        response = ws.recv()
        print(json.loads(response))
        result = json.loads(response)["result"]
        return result




############## START SWAP (WEBSOCKET) ##############
swap_data = start_swap(NET)
print(swap_data)

with open('/tmp/1.dat', "w") as f:
    json.dump(swap_data, f)

with open('/tmp/1.dat', "r") as f:
    data = json.load(f)

print(data)
data['subaccount']=0

with open('/tmp/1.dat', "w") as f:
    json.dump(data, f)

############## CREATE PSET (CLI) ###################
process = subprocess.Popen("green-cli --network electrum-liquid createpset /tmp/1.dat", shell=True, stdout=subprocess.PIPE)
output, _ = process.communicate()
print(output)
print(json.loads(output))
create_pset_result = json.loads(output)


############## UPLOAD SWAP INPUTS (HTTP POST) ##############
swap_start_request ={
    "id": None,
    "method": "swap_start",
    "params": {
        "change_addr": create_pset_result['change_addr'],
        "recv_addr":   create_pset_result['recv_addr'],
        "inputs":      create_pset_result['inputs'],
        "order_id":    swap_data['order_id'],
        "recv_amount": swap_data['recv_amount'],
        "recv_asset":  swap_data['recv_asset'],
        "send_amount": swap_data['send_amount'],
        "send_asset":  swap_data['send_asset']
    }
}
sideswap_pset_data = requests.post(swap_data["upload_url"], json=swap_start_request).json()['result']
print(sideswap_pset_data)

########### SIGN PSET ##########################
sign_pset_req = {
    "subaccount": SUBACCOUNT,
    "send_asset": swap_data["send_asset"],
    "send_amount": swap_data["send_amount"],
    "recv_asset": swap_data["recv_asset"],
    "recv_amount": swap_data["recv_amount"],
    "pset": sideswap_pset_data["pset"]
}
#sign_result = session.sign_pset(sign_pset_req).resolve()

with open('/tmp/2.dat', "w") as f:
    json.dump(sign_pset_req, f)

process = subprocess.Popen("green-cli --network electrum-liquid signpset /tmp/2.dat", shell=True, stdout=subprocess.PIPE)
output, _ = process.communicate()
print(output)
print(json.loads(output))
sign_result = json.loads(output)
print(sign_result)


########### SUBMIT SIGNED PSET (HTTP POST) ##########################
upload_request = {
    "id": None,
    "method": "swap_sign",
    "params": {
        "order_id": swap_data["order_id"],
        "pset": sign_result["pset"],
        "submit_id": sideswap_pset_data["submit_id"]
    }
}
response = requests.post(swap_data["upload_url"], json=upload_request)
print(response.json())
