use crate::database;

use tonic::{Request, Response, Status};
use std::hash::{DefaultHasher, Hash, Hasher};
use std::sync::Arc;
use crate::kv_store::InMemoryStore;
use crate::types::Bytes;
use crate::config::{NUM_INSTANCES};

use database::database_server::{Database};
use database::{
    HelloRequest, HelloReply,
    GetRequest, GetReply,
    SetRequest, SetReply,
    RegionRequest, ReadRegionReply, WriteRegionReply,
};

#[derive(Clone)]
pub struct DB {
    pub store: Arc<InMemoryStore>,
    pub vms: Vec<String>,
}

impl DB {
    pub fn new(store: Arc<InMemoryStore>, vms: Vec<String>) -> Self {
        Self { store, vms }
    }

    pub fn get_region(&self, key: &Bytes) -> String {
        let mut hasher = DefaultHasher::new();
        key.hash(&mut hasher);
        let hash_value = hasher.finish();

        self.vms[(hash_value % NUM_INSTANCES) as usize].clone()
    }
}

#[tonic::async_trait]
impl Database for DB {
    async fn say_hello(&self, request: Request<HelloRequest>) -> Result<Response<HelloReply>, Status> {
        let name = request.into_inner().name;
        let reply = HelloReply {
            message: format!("Hello {}!", name),
        };
        Ok(Response::new(reply))
    }
    
    async fn get(&self, request: Request<GetRequest>) -> Result<Response<GetReply>, Status> {
        let req = request.into_inner();
        let key = Bytes(req.key);
        let value = self.store.get(&key).await;
        let value_vec = value.map(|b| b.0).unwrap_or_default();
        Ok(Response::new(GetReply { value: value_vec }))
    }
    
    async fn set(&self, request: Request<SetRequest>) -> Result<Response<SetReply>, Status> {
        let req = request.into_inner();

        let key_clone = req.key.clone();
        let value_clone = req.value.clone();

        let key = Bytes(key_clone.clone());
        let value = Bytes(value_clone.clone());

        // get env value of HOSTNAME
        let hostname = std::env::var("HOSTNAME").unwrap();
        
        if hostname != self.get_region(&key) {
            return Ok(Response::new(SetReply { success: false }));
        }

        self.store.set(&key, &value).await;

        Ok(Response::new(SetReply { success: true }))
    }

    async fn get_read_regions(&self, request: Request<RegionRequest>) -> Result<Response<ReadRegionReply>, Status> {
        println!("Received get_read_regions request");
        let key: Bytes = request.into_inner().key.into();
        
        let region = self.get_region(&key);
        let regions = vec![region];

        println!("Read regions: {:?}", regions);
        Ok(Response::new(ReadRegionReply { regions }))
    }

    async fn get_write_region(&self, request: Request<RegionRequest>) -> Result<Response<WriteRegionReply>, Status> {
        println!("Received get_write_region request");
        let key: Bytes = request.into_inner().key.into();
        let region = self.get_region(&key);

        println!("Write region: {}", region);

        Ok(Response::new(WriteRegionReply { region }))        
    }
}
