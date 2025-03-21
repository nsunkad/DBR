use crate::database;

use tonic::{Request, Response, Status};
use async_trait::async_trait;
use std::sync::Arc;
use crate::kv_store::KvStore;
use database::database_server::{Database, DatabaseServer};
use database::{
    HelloRequest, HelloReply, GetRequest, GetReply, SetRequest, SetReply,
    BatchGetRequest, BatchGetReply, BatchSetRequest, BatchSetReply, KeyValue,
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
        let value = self.store.get(&req.key).await.unwrap_or_default();
        Ok(Response::new(GetReply { value }))
    }

    async fn set(&self, request: Request<SetRequest>) -> Result<Response<SetReply>, Status> {
        let req = request.into_inner();
        self.store.set(&req.key, &req.value).await;
        Ok(Response::new(SetReply { success: true }))
    }

    async fn batch_get(&self, request: Request<BatchGetRequest>) -> Result<Response<BatchGetReply>, Status> {
        let req = request.into_inner();
        let pairs = self.store.batch_get(req.keys).await;
        let reply = BatchGetReply {
            pairs: pairs.into_iter()
                        .map(|(k, v)| KeyValue { key: k, value: v })
                        .collect(),
        };
        Ok(Response::new(reply))
    }

    async fn batch_set(&self, request: Request<BatchSetRequest>) -> Result<Response<BatchSetReply>, Status> {
        let req = request.into_inner();
        let pairs = req.pairs.into_iter()
                             .map(|kv| (kv.key, kv.value))
                             .collect();
        self.store.batch_set(pairs).await;
        Ok(Response::new(BatchSetReply { success: true }))
    }
}
