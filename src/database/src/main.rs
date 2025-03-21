use database::database_server::{Database, DatabaseServer};
use database::{HelloReply, HelloRequest, GetRequest, GetReply, SetRequest, SetReply, RangeGetRequest, RangeGetReply, RangeSetRequest, RangeSetReply};
use tonic::{transport::Server, Request, Response, Status};

pub mod database {
    tonic::include_proto!("database");
}

#[derive(Default)]
pub struct DB {}

#[tonic::async_trait]
impl Database for DB {
    async fn say_hello(
        &self,
        request: Request<HelloRequest>, // Incoming request
    ) -> Result<Response<HelloReply>, Status> {
        println!("Received request: {:?}", request);
        let reply = HelloReply {
            message: format!("Hello {}!", request.into_inner().name),
        };
        Ok(Response::new(reply))
    }

    async fn get(
        &self,
        request: Request<database::GetRequest>,
    ) -> Result<Response<database::GetReply>, Status> {
        println!("Received request: {:?}", request);
        let reply = database::GetReply {
            value: b"Hello World!".to_vec(),
        };
        Ok(Response::new(reply))
    }

    async fn set(
        &self,
        request: Request<database::SetRequest>,
    ) -> Result<Response<database::SetReply>, Status> {
        println!("Received request: {:?}", request);
        let reply = database::SetReply { success: true };
        Ok(Response::new(reply))
    }

    async fn range_get(
        &self,
        request: Request<database::RangeGetRequest>,
    ) -> Result<Response<database::RangeGetReply>, Status> {
        println!("Received request: {:?}", request);
        let reply = database::RangeGetReply {
            pairs: vec![database::KeyValue {
                key: b"key".to_vec(),
                value: b"value".to_vec(),
            }],
        };
        Ok(Response::new(reply))
    }

    async fn range_set(
        &self,
        request: Request<database::RangeSetRequest>,
    ) -> Result<Response<database::RangeSetReply>, Status> {
        println!("Received request: {:?}", request);
        let reply = database::RangeSetReply { success: true };
        Ok(Response::new(reply))
    }
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    println!("Hello, world!");
    let addr = "[::1]:50051".parse()?;
    let db = DB::default();

    println!("Server listening on {}", addr);
    Server::builder()
        .add_service(DatabaseServer::new(db)) // Fixed: Use DatabaseServer instead of GreeterServer
        .serve(addr)
        .await?;

    Ok(())
}
