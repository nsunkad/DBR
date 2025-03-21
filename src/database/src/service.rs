use crate::database;

use tonic::{Request, Response, Status};
use std::sync::Arc;
use crate::kv_store::KvStore;
use crate::types::Bytes;


use database::database_server::{Database, DatabaseServer};
use database::{
    HelloRequest, HelloReply,
    GetRequest, GetReply,
    SetRequest, SetReply,
    BatchGetSetRequest, BatchGetSetReply, KeyValue,
};

#[derive(Clone)]
pub struct DB {
    pub store: Arc<dyn KvStore>,
}

impl DB {
    pub fn new(store: Arc<dyn KvStore>) -> Self {
        Self { store }
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
}
