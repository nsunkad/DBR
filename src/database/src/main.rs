mod database;
mod kv_store;
mod service;

use std::sync::Arc;
use tonic::transport::Server;
use service::DB;
use kv_store::{KvStore, InMemoryStore};

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let addr = "[::1]:50051".parse()?;
    println!("Server listening on {}", addr);

    let store: Arc<dyn KvStore> = Arc::new(InMemoryStore::new());
    let db_service = DB::new(store);

    Server::builder()
        .add_service(database::database_server::DatabaseServer::new(db_service))
        .serve(addr)
        .await?;

    Ok(())
}
