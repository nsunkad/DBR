import os
import sys
from grpc_tools import protoc

def main():
    # Compute the absolute path to the protos folder (one level up from application)
    proto_include = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "protos"))
    # Full path to the proto file
    proto_file = os.path.join(proto_include, "database.proto")
    
    # Build the argument list similar to:
    # python -m grpc_tools.protoc -I../protos --python_out=. --grpc_python_out=. ../protos/database.proto
    protoc_args = [
        "",  # Dummy entry for the program name
        f"-I{proto_include}",
        "--python_out=.",
        "--grpc_python_out=.",
        proto_file,
    ]
    
    print("Running protoc with the following arguments:")
    print(" ".join(protoc_args))
    
    if protoc.main(protoc_args) != 0:
        sys.exit("Error: protoc command failed.")

if __name__ == "__main__":
    main()
