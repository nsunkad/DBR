use async_trait::async_trait;

#[async_trait]
pub trait KvStore: Send + Sync {
    async fn get(&self, key: &[u8]) -> Result<Option<Vec<u8>>, Box<dyn std::error::Error + Send + Sync>>;
    async fn set(&self, key: &[u8], value: &[u8]) -> Result<(), Box<dyn std::error::Error + Send + Sync>>;
    async fn range_get(
        &self,
        start: &[u8],
        end: &[u8]
    ) -> Result<Vec<(Vec<u8>, Vec<u8>)>, Box<dyn std::error::Error + Send + Sync>>;
    async fn range_set(&self, pairs: Vec<(&[u8], &[u8])>) -> Result<(), Box<dyn std::error::Error + Send + Sync>>;
}
