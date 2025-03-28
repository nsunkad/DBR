# gen_database_proto.py

import os
import sys
from grpc_tools import protoc

TARGETS = ["database.proto", "dbr.proto"]
OUT_DIR = "generated"

def gen_protos():
    # Compute the absolute path to the protos folder (one level up from application)
    proto_include = os.path.abspath(os.path.join(os.path.dirname(__file__), "protos"))
    proto_files = [os.path.join(proto_include, target) for target in TARGETS]

    out_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), OUT_DIR))
    os.makedirs(out_dir, exist_ok=True)
    
    # Build the argument list similar to:
    # python -m grpc_tools.protoc -I../protos --python_out=. --grpc_python_out=. ../protos/database.proto
    protoc_args = [
        "",  # Dummy entry for the program name
        f"-I{proto_include}",
        f"--python_out={out_dir}",
        f"--grpc_python_out={out_dir}",
        *proto_files,
    ]
    
    print("Running protoc with the following arguments:")
    print(" ".join(protoc_args))
    
    if protoc.main(protoc_args) != 0:
        sys.exit("Error: protoc command failed.")


if __name__ == "__main__":
    gen_protos()
