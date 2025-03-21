use async_trait::async_trait;
use std::collections::BTreeMap;
use std::sync::Mutex;
use crate::kv_store::KvStore;

pub struct FjallDb {
    store: Mutex<BTreeMap<Vec<u8>, Vec<u8>>>,
}

impl FjallDb {
    pub fn new() -> Self {
        Self {
            store: Mutex::new(BTreeMap::new()),
        }
    }
}

#[async_trait]
impl KvStore for FjallDb {
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
        // let store = self.store.lock().unwrap();
        // let range = store.range(start.to_vec()..end.to_vec())
        //     .map(|(k, v)| (k.clone(), v.clone()))
        //     .collect();
        // Ok(range)
        Err("not implemented".into())
    }

    async fn range_set(&self, pairs: Vec<(&[u8], &[u8])>) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
        // let mut store = self.store.lock().unwrap();
        // for (k, v) in pairs {
        //     store.insert(k.to_vec(), v.to_vec());
        // }
        // Ok(())
        Err("not implemented".into())
    }
}
