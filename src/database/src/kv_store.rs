use async_trait::async_trait;
use std::collections::HashMap;
use tokio::sync::RwLock;

#[async_trait]
pub trait KvStore: Send + Sync {
    async fn get(&self, key: &[u8]) -> Option<Vec<u8>>;
    async fn set(&self, key: &[u8], value: &[u8]);
    async fn batch_get(&self, keys: Vec<Vec<u8>>) -> Vec<(Vec<u8>, Vec<u8>)>;
    async fn batch_set(&self, pairs: Vec<(Vec<u8>, Vec<u8>)>);
}

pub struct InMemoryStore {
    pub map: RwLock<HashMap<Vec<u8>, Vec<u8>>>,
}

impl InMemoryStore {
    pub fn new() -> Self {
        Self {
            map: RwLock::new(HashMap::new()),
        }
    }
}

#[async_trait]
impl KvStore for InMemoryStore {
    async fn get(&self, key: &[u8]) -> Option<Vec<u8>> {
        let map = self.map.read().await;
        map.get(key).cloned()
    }

    async fn set(&self, key: &[u8], value: &[u8]) {
        let mut map = self.map.write().await;
        map.insert(key.to_vec(), value.to_vec());
    }

    async fn batch_get(&self, keys: Vec<Vec<u8>>) -> Vec<(Vec<u8>, Vec<u8>)> {
        let map = self.map.read().await;
        keys.into_iter()
            .filter_map(|k| map.get(&k).map(|v| (k, v.clone())))
            .collect()
    }

    async fn batch_set(&self, pairs: Vec<(Vec<u8>, Vec<u8>)>) {
        let mut map = self.map.write().await;
        for (k, v) in pairs {
            map.insert(k, v);
        }
    }
}
