use crate::database;

use tonic::{Request, Response, Status};
use std::hash::{DefaultHasher, Hash, Hasher};
use std::sync::Arc;
use crate::kv_store::InMemoryStore;
use crate::types::Bytes;
use crate::config::{NUM_INSTANCES, REPLICATION_FACTOR};

use database::database_server::{Database};
use database::{
    HelloRequest, HelloReply,
    GetRequest, GetReply,
    SetRequest, SetReply,
    BatchGetSetRequest, BatchGetSetReply, KeyValue,
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
        let key = Bytes(req.key);
        let value = Bytes(req.value);
        self.store.set(&key, &value).await;
        Ok(Response::new(SetReply { success: true }))
    }
    
    async fn batch_get_set(&self, request: Request<BatchGetSetRequest>) -> Result<Response<BatchGetSetReply>, Status> {
        let req = request.into_inner();
        // Convert get_keys from Vec<Vec<u8>> to Vec<Bytes>
        let get_keys: Vec<Bytes> = req.get_keys.into_iter().map(Bytes).collect();
        // Convert set_pairs from Vec<KeyValue> to Vec<(Bytes, Bytes)>
        let set_pairs: Vec<(Bytes, Bytes)> = req.set_pairs.into_iter()
            .map(|kv| (Bytes(kv.key), Bytes(kv.value)))
            .collect();
        let (pairs, success) = self.store.batch_get_set(get_keys, set_pairs).await;
        // Convert result pairs back into Vec<KeyValue>
        let result_pairs = pairs.into_iter()
            .map(|(k, v)| KeyValue { key: k.0, value: v.0 })
            .collect();
        Ok(Response::new(BatchGetSetReply { pairs: result_pairs, success }))
    }

    async fn get_read_regions(&self, request: Request<RegionRequest>) -> Result<Response<ReadRegionReply>, Status> {
        let key: Bytes = request.into_inner().key.into();
        
        let mut hasher = DefaultHasher::new();
        key.hash(&mut hasher);
        let hash_value = hasher.finish();

        const OFFSET: u64 = NUM_INSTANCES / (REPLICATION_FACTOR+1);
        
        // Get the three regions for the key
        let regions = vec![
            self.vms[((hash_value + 1*OFFSET) % NUM_INSTANCES) as usize].clone(),
            self.vms[((hash_value + 2*OFFSET) % NUM_INSTANCES) as usize].clone(),
            self.vms[((hash_value + 3*OFFSET) % NUM_INSTANCES) as usize].clone(),
        ];

        Ok(Response::new(ReadRegionReply { regions }))
    }

    async fn get_write_region(&self, request: Request<RegionRequest>) -> Result<Response<WriteRegionReply>, Status> {
        let key: Bytes = request.into_inner().key.into();
        
        let mut hasher = DefaultHasher::new();
        key.hash(&mut hasher);
        let hash_value = hasher.finish();

        let region = self.vms[(hash_value % NUM_INSTANCES) as usize].clone();

        Ok(Response::new(WriteRegionReply { region }))        
    }
}
