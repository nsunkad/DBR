use async_trait::async_trait;
use std::collections::HashMap;
use tokio::sync::RwLock;
use std::hash::{Hash, Hasher};

/// A newtype wrapper around Vec<u8> for strong typing.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Bytes(pub Vec<u8>);

impl From<Vec<u8>> for Bytes {
    fn from(vec: Vec<u8>) -> Self {
        Bytes(vec)
    }
}

impl From<Bytes> for Vec<u8> {
    fn from(b: Bytes) -> Self {
        b.0
    }
}

impl AsRef<[u8]> for Bytes {
    fn as_ref(&self) -> &[u8] {
        &self.0
    }
}

impl Hash for Bytes {
    fn hash<H: Hasher>(&self, state: &mut H) {
        self.0.hash(state);
    }
}

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
