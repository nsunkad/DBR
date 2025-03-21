mod database;
mod kv_store;
mod service;
mod databases;

use std::sync::Arc;
use tonic::transport::Server;
use service::DB;
use kv_store::KvStore;

// Choose backend:
// use databases::fjall_db::FjallDb;
use databases::pickle_db::PickleDb;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let addr = "[::1]:50051".parse()?;
    println!("Server listening on {}", addr);

    // Initialize the backend
    // let store: Arc<dyn KvStore> = Arc::new(FjallDb::new());
    let store: Arc<dyn KvStore> = Arc::new(PickleDb::new());

    let db_service = DB::new(store);

    Server::builder()
        .add_service(database::database_server::DatabaseServer::new(db_service))
        .serve(addr)
        .await?;

    Ok(())
}
