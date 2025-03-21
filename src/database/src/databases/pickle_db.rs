use async_trait::async_trait;
use std::collections::HashMap;
use std::sync::Mutex;
use crate::kv_store::KvStore;

pub struct PickleDb {
    store: Mutex<HashMap<Vec<u8>, Vec<u8>>>,
}

impl PickleDb {
    pub fn new() -> Self {
        Self {
            store: Mutex::new(HashMap::new()),
        }
    }
}

#[async_trait]
impl KvStore for PickleDb {
    async fn get(&self, key: &[u8]) -> Result<Option<Vec<u8>>, Box<dyn std::error::Error + Send + Sync>> {
        let store = self.store.lock().unwrap();
        Ok(store.get(key).cloned())
    }

    async fn set(&self, key: &[u8], value: &[u8]) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
        let mut store = self.store.lock().unwrap();
        store.insert(key.to_vec(), value.to_vec());
        Ok(())
    }

    async fn range_get(&self, start: &[u8], end: &[u8]) -> Result<Vec<(Vec<u8>, Vec<u8>)>, Box<dyn std::error::Error + Send + Sync>> {
        // let store: std::sync::MutexGuard<'_, HashMap<Vec<u8>, Vec<u8>>> = self.store.lock().unwrap();
        // let mut pairs: Vec<_> = store.iter()
        //     .filter(|(k, _)| *k >= start && *k < end)
        //     .map(|(k, v)| (k.clone(), v.clone()))
        //     .collect();
        // pairs.sort_by(|(a, _), (b, _)| a.cmp(b));
        // Ok(pairs)
        Err("Not implemented".into())
    }

    async fn range_set(&self, pairs: Vec<(&[u8], &[u8])>) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
        // let mut store = self.store.lock().unwrap();
        // for (k, v) in pairs {
        //     store.insert(k.to_vec(), v.to_vec());
        // }
        // Ok(())
        Err("Not implemented".into())
    }
}
