import os
import json
from datetime import datetime
from flask import Flask, request, jsonify
from enums import DBRStatus
from constants import LOCAL_HOSTNAME
from orchestration.dbr_service import dbr_servicer
from custom_types import DBR
from utils import convert_dbr_to_proto

app = Flask(__name__)
dbr_statuses = {}

ROOT_DIR = os.environ.get("ROOT_DIR", None)
os.makedirs(os.path.join(ROOT_DIR, "dumps"), exist_ok=True)


@app.route('/execute', methods=['POST'])
def execute_dbr():
    req_data = json.loads(request.get_json())
    recv_time = datetime.now()
    try:
        print(req_data)
        in_dbr = DBR.model_validate(req_data)
        print("INIT DBR", in_dbr)
        proto_dbr = convert_dbr_to_proto(in_dbr)
        print("PROTO DBR", proto_dbr)
    except Exception as e:
        print(e)
        return jsonify({"success": False, "error": str(e)}), 400
    
    print("PRE-SCHEDULE")
    response = dbr_servicer.Schedule(proto_dbr, None)
    print("POST-SCHEDULE")
    
    if db_id := req_data.get('id'):
        print(db_id)
        dbr_statuses[db_id] = {"status": DBRStatus.DBR_RUNNING, "env": None}
        with open(f"{ROOT_DIR}/dumps/{db_id}.dump", "w") as f:
            f.write("")
        with open(f"{ROOT_DIR}/dumps/{db_id}.dump", "a") as f:
            f.write(f"INIT {recv_time}\n")
    
    return jsonify({"success": response.success})

@app.route('/set_dbr_status', methods=['POST'])
def set_dbr_status():
    data = json.loads(request.get_json())
    db_id = data.get("id")
    status = data.get("status")
    env = data.get("env")

    if not db_id:
        return jsonify({"success": False, "error": "No id provided"}), 400
    
    dbr_statuses[db_id] = {"status": status, "env": env}
    return jsonify({"success": True})

@app.route('/check', methods=['GET'])
def check_dbr_status():
    db_id = request.args.get("id")
    print(db_id, db_id in dbr_statuses)
    if not db_id:
        return jsonify({"error": "No id provided"}), 400
    if db_id in dbr_statuses:
        return jsonify(dbr_statuses[db_id])
    else:
        return jsonify({"error": "No such DBR"}), 404
    
@app.route('/dump', methods=['POST'])
def dump():
    data = request.get_json()
    dbr_id = data.get("id")
    recv_time = datetime.now()
    
    if not dbr_id:
        return jsonify({"error": "No id provided"}), 400
    
    cleaned_data = " ".join(f"{key}:{value}" for key, value in data.items() if key != "id")
    with open(f"{ROOT_DIR}/dumps/{dbr_id}.dump", "a") as f: 
        f.write(f"DUMP {recv_time} {cleaned_data}\n")

    return jsonify({"success": True})

@app.route('/read-dump', methods=['GET'])
def status():
    dbr_id = request.args.get("id")
    if not dbr_id:
        return jsonify({"error": "No id provided"}), 400
    
    with open(f"{ROOT_DIR}/dumps/{dbr_id}.dump", "r") as f:
        data = f.read()

    return jsonify({"data": data}), 200

@app.route('/all-status', methods=['GET'])
def all_status():
    return jsonify(dbr_statuses), 200