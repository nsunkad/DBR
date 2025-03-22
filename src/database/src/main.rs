mod database;
mod kv_store;
mod service;
mod types;
mod config;

use std::{env, fs, sync::Arc};
use tonic::transport::Server;
use service::DB;
use kv_store::{KvStore, InMemoryStore};

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let args: Vec<String> = env::args().collect();
    if args.len() < 2 {
        eprintln!("Usage: {} <vms_file_path>", args[0]);
        std::process::exit(1);
    }

    let vms_file_path = &args[1];
    let content = fs::read_to_string(vms_file_path)?;
    let vms: Vec<String> = content
        .lines()
        .map(|line| line.trim().to_string())
        .filter(|line| !line.is_empty())
        .collect();

    let addr = config::ADDR.parse()?;
    println!("Server listening on {}", addr);

    let store: Arc<dyn KvStore> = Arc::new(InMemoryStore::new());
    let db_service = DB::new(store, vms);

    Server::builder()
        .add_service(database::database_server::DatabaseServer::new(db_service))
        .serve(addr)
        .await?;

    Ok(())
}
