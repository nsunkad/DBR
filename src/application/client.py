import grpc
import database_pb2
import database_pb2_grpc

def run():
    # Create an insecure channel to the Rust server (change to secure_channel if needed)
    channel = grpc.insecure_channel('localhost:50051')
    
    # Create a stub (client) for the Database service.
    stub = database_pb2_grpc.DatabaseStub(channel)
    
    # Create a HelloRequest message.
    request = database_pb2.HelloRequest(name="World")
    response = stub.SayHello(request)
    print("Server responded:", response.message)

    request = database_pb2.SetRequest(key=b"key", value=b"value2")
    response = stub.Set(request)
    print("Server responded:", response.success)
    
    request = database_pb2.GetRequest(key=b"key")
    response = stub.Get(request)
    print("Server responded:", response.value)

    

if __name__ == '__main__':
    run()
