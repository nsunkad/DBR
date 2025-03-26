
use std::collections::HashMap;
use tokio::sync::RwLock;
use crate::types::Bytes;

pub struct InMemoryStore {
    pub map: RwLock<HashMap<Bytes, Bytes>>,
}

impl InMemoryStore {
    pub fn new() -> Self {
        Self {
            map: RwLock::new(HashMap::new()),
        }
    }
    
    pub async fn get(&self, key: &Bytes) -> Option<Bytes> {
        let map = self.map.read().await;
        map.get(key).cloned()
    }

    pub async fn set(&self, key: &Bytes, value: &Bytes) {
        let mut map = self.map.write().await;
        map.insert(key.clone(), value.clone());
    }
}
