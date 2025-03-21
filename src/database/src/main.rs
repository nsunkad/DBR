use database::database_server::{Database, DatabaseServer};
use database::{HelloReply, HelloRequest};
use tonic::{transport::Server, Request, Response, Status};

pub mod database {
    tonic::include_proto!("database");
}

// #[derive(Default)]
// pub struct DB {}

// #[tonic::async_trait]
// impl Database for DB {
//     async fn say_hello(
//         &self,
//         request: Request<HelloRequest>, // Incoming request
//     ) -> Result<Response<HelloReply>, Status> {
//         println!("Received request: {:?}", request);
//         let reply = HelloReply {
//             message: format!("Hello {}!", request.into_inner().name),
//         };
//         Ok(Response::new(reply))
//     }
// }

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    // let addr = "[::1]:50051".parse()?;
    // let db = DB::default();

    // println!("Server listening on {}", addr);
    // Server::builder()
    //     .add_service(DatabaseServer::new(db)) // Fixed: Use DatabaseServer instead of GreeterServer
    //     .serve(addr)
    //     .await?;

    Ok(())
}
