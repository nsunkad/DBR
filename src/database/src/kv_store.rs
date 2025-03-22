use async_trait::async_trait;
use std::collections::HashMap;
use tokio::sync::RwLock;
use crate::types::Bytes;

/// A trait for a simple asynchronous key–value store.
#[async_trait]
pub trait KvStore: Send + Sync {
    async fn get(&self, key: &Bytes) -> Option<Bytes>;
    async fn set(&self, key: &Bytes, value: &Bytes);
    async fn batch_get_set(
        &self,
        get_keys: Vec<Bytes>,
        set_pairs: Vec<(Bytes, Bytes)>
    ) -> (Vec<(Bytes, Bytes)>, bool);
}

/// An in‑memory implementation using a Tokio‑protected HashMap.
pub struct InMemoryStore {
    pub map: RwLock<HashMap<Bytes, Bytes>>,
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
    async fn get(&self, key: &Bytes) -> Option<Bytes> {
        let map = self.map.read().await;
        map.get(key).cloned()
    }

    async fn set(&self, key: &Bytes, value: &Bytes) {
        let mut map = self.map.write().await;
        map.insert(key.clone(), value.clone());
    }

    async fn batch_get_set(
        &self,
        get_keys: Vec<Bytes>,
        set_pairs: Vec<(Bytes, Bytes)>
    ) -> (Vec<(Bytes, Bytes)>, bool) {
        let mut map = self.map.write().await;
        // Perform batch set: update the map.
        for (k, v) in set_pairs {
            map.insert(k, v);
        }
        // Perform batch get: collect key-value pairs for requested keys.
        let results = get_keys.into_iter()
            .filter_map(|k| map.get(&k).map(|v| (k, v.clone())))
            .collect();
        (results, true)
    }
}
