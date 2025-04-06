import json
from flask import Flask, request, jsonify
from enums import DBRStatus, QueryType
from generated import dbr_pb2
from orchestration.dbr_service import dbr_servicer
from orchestration.types import DBR
from constants import LOCAL_REGION

app = Flask(__name__)
dbr_statuses = {}

def convert_dbr_to_proto(dbr):
    print("CONVERTING")
    proto_dbr = dbr_pb2.DBReq()
    proto_dbr.id = str(dbr.id)
    proto_dbr.name = dbr.name
    proto_dbr.status = dbr.status.value
    proto_dbr.client_location = LOCAL_REGION

    print("PREDECESSOR")
    if dbr.predecessor_location is not None:
        proto_dbr.predecessor_location = dbr.predecessor_location
    
    print("LOGIC FUNCTIONS")
    for logic_function in dbr.logic_functions:
        print("LOGIC_FN", logic_function)
        proto_dbr.logic_functions.append(logic_function)
        print("done")
    # print("post")
    # print(proto_dbr.logic_functions)

    print("env")
    for key, value in dbr.environment.env.items():
        proto_dbr.environment.environment.append(dbr_pb2.EnvEntry(key=key, value=value))

    print("queries")
    for query in dbr.queries.values():
        if query.query_type == QueryType.GET:
            proto_query = dbr_pb2.GetQuery(id=str(query.id), key=query.key)
            proto_dbr.queries.append(dbr_pb2.Query(get_query=proto_query))
            continue
        
        if query.query_type == QueryType.SET:
            proto_query = dbr_pb2.SetQuery(id=str(query.id), key=query.key, value=query.value)
            proto_dbr.queries.append(dbr_pb2.Query(set_query=proto_query))
            continue
        
        raise ValueError("Unsupported query type")

    print("PROTO DBR", proto_dbr)
    return proto_dbr

@app.route('/execute', methods=['POST'])
def execute_dbr():
    print("IN")
    req_data = json.loads(request.get_json())
    try:
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
        dbr_statuses[db_id] = {"status": DBRStatus.DBR_RUNNING, "result": None}
    
    return jsonify({"success": response.success})

@app.route('/set_dbr_status', methods=['POST'])
def set_dbr_status():
    data = request.get_json()
    db_id = data.get("id")
    status = data.get("status")
    result = data.get("result")
    if not db_id:
        return jsonify({"success": False, "error": "No id provided"}), 400
    dbr_statuses[db_id] = {"status": status, "result": result}
    return jsonify({"success": True})

@app.route('/check_dbr_status', methods=['GET'])
def check_dbr_status():
    db_id = request.args.get("id")
    if not db_id:
        return jsonify({"error": "No id provided"}), 400
    if db_id in dbr_statuses:
        return jsonify(dbr_statuses[db_id])
    else:
        return jsonify({"error": "No such DBR"}), 404
    
@app.route('/all-status', methods=['GET'])
def all_status():
    return jsonify(dbr_statuses), 200