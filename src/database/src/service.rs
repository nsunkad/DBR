use tonic::{Request, Response, Status};
use async_trait::async_trait;
use std::sync::Arc;
use crate::kv_store::KvStore;

use crate::database::database_server::{Database, DatabaseServer};
use crate::database::{HelloRequest, HelloReply, GetRequest, GetReply, SetRequest, SetReply, RangeGetRequest, RangeGetReply, RangeSetRequest, RangeSetReply, KeyValue};

#[derive(Clone)]
pub struct DB {
    pub store: Arc<dyn KvStore>,
}

impl DB {
    pub fn new(store: Arc<dyn KvStore>) -> Self {
        Self { store }
    }
}

#[async_trait]
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
        let value = self.store.get(&req.key)
            .await
            .map_err(|e| Status::internal(e.to_string()))?;
        Ok(Response::new(GetReply {
            value: value.unwrap_or_default(),
        }))
    }
    
    async fn set(&self, request: Request<SetRequest>) -> Result<Response<SetReply>, Status> {
        let req = request.into_inner();
        self.store.set(&req.key, &req.value)
            .await
            .map_err(|e| Status::internal(e.to_string()))?;
        Ok(Response::new(SetReply { success: true }))
    }
    
    async fn range_get(&self, request: Request<RangeGetRequest>) -> Result<Response<RangeGetReply>, Status> {
        let req = request.into_inner();
        let pairs = self.store.range_get(&req.start_key, &req.end_key)
            .await
            .map_err(|e| Status::internal(e.to_string()))?;
        let reply = RangeGetReply {
            pairs: pairs.into_iter().map(|(k, v)| KeyValue { key: k, value: v }).collect(),
        };
        Ok(Response::new(reply))
    }
    
    async fn range_set(&self, request: Request<RangeSetRequest>) -> Result<Response<RangeSetReply>, Status> {
        let req = request.into_inner();
        let kv_pairs: Vec<(&[u8], &[u8])> = req.pairs.iter()
            .map(|kv| (kv.key.as_slice(), kv.value.as_slice()))
            .collect();
        self.store.range_set(kv_pairs)
            .await
            .map_err(|e| Status::internal(e.to_string()))?;
        Ok(Response::new(RangeSetReply { success: true }))
    }
}
