import json
from flask import Flask, request, jsonify
from enums import DBRStatus, QueryType
from generated import dbr_pb2
from orchestration.dbr_service import dbr_servicer
from orchestration.types import DBR

app = Flask(__name__)
dbr_statuses = {}

@app.route('/execute', methods=['POST'])
def execute_dbr():
    req_data = json.loads(request.get_json())
    try:
        in_dbr = DBR.model_validate(req_data)
        
        out_dbr = dbr_pb2.DBReq()
        out_dbr.id = str(in_dbr.id)
        out_dbr.name = in_dbr.name
        out_dbr.status = in_dbr.status.value
        if in_dbr.predecessor_location is not None:
            out_dbr.predecessor_location = in_dbr.predecessor_location

        for key, value in in_dbr.environment.env.items():
            out_dbr.environment.environment.append(dbr_pb2.KeyValue(key=key, value=value))

        for query in in_dbr.queries.values():
            if query.query_type == QueryType.GET:
                out_query = dbr_pb2.GetQuery(id=str(query.id), key=query.key)
                out_dbr.queries.append(dbr_pb2.Query(get_query=out_query))
                continue
            
            if query.query_type == QueryType.SET:
                out_query = dbr_pb2.SetQuery(id=str(query.id), key=query.key, value=query.value)
                out_dbr.queries.append(dbr_pb2.Query(set_query=out_query))
                continue
            
            raise ValueError("Unsupported query type")
        print("post queries")
        

    except Exception as e:
        print(e)
        return jsonify({"success": False, "error": str(e)}), 400

    response = dbr_servicer.Schedule(out_dbr, None)
    
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