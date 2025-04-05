# gen_database_proto.py

import os
import sys
from grpc_tools import protoc

TARGETS = ["database.proto", "dbr.proto"]
OUT_DIRS = ["src/generated", "client/generated"]

def gen_protos(root_dir):
    proto_include = os.path.abspath(os.path.join(root_dir, "src", "protos"))
    proto_files = [os.path.join(proto_include, target) for target in TARGETS]

    # Build the argument list similar to:
    # python -m grpc_tools.protoc -I../protos --python_out=. --grpc_python_out=. ../protos/database.proto

    for out_dir in OUT_DIRS:
        # Create the output directory if it doesn't exist
        out_path = os.path.join(root_dir, out_dir)
        print(f"Generating protos in {out_path}")
        os.makedirs(out_path, exist_ok=True)

        protoc_args = [
            "",  # Dummy entry for the program name
            f"-I{proto_include}",
            f"--python_out={out_path}",
            f"--grpc_python_out={out_path}",
            *proto_files,
        ]
    
        print("Running protoc with the following arguments:")
        print(" ".join(protoc_args))
        
        if protoc.main(protoc_args) != 0:
            sys.exit("Error: protoc command failed.")


if __name__ == "__main__":
    root_dir = os.environ.get("ROOT_DIR", None)
    if root_dir is None:
        print("Error: ROOT_DIR environment variable not set.")
        sys.exit(1)
    gen_protos(root_dir)
