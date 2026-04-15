use crate::reranker::errors::RerankerError;
use async_trait::async_trait;
use serde::{Deserialize, Serialize};

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct DomainRerankResult {
    pub relevance_score: f32,
    pub index: usize,
    pub document: Option<String>,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct DomainRerankResponse {
    pub model: String,
    pub results: Vec<DomainRerankResult>,
    pub total_tokens: u32,
}

#[async_trait]
pub trait Reranker: Send + Sync {
    async fn rerank(
        &self,
        model: &str,
        query: &str,
        documents: Vec<String>,
        top_k: Option<i32>,
    ) -> Result<DomainRerankResponse, RerankerError>;
}
