use crate::context::AppContext;
use miette::{IntoDiagnostic, Result};
use vetta_core::{
    Embedder, LocalEmbeddingsStrategy, LocalRerankerStrategy, LocalSttStrategy, Reranker, Stt,
};

pub async fn build_stt(ctx: &AppContext) -> Result<Box<dyn Stt>> {
    let stt = LocalSttStrategy::connect(&ctx.config.socket_path)
        .await
        .into_diagnostic()?;

    Ok(Box::new(stt))
}

pub async fn build_embedder(ctx: &AppContext) -> Result<Box<dyn Embedder>> {
    let embedder = LocalEmbeddingsStrategy::connect(&ctx.config.socket_path)
        .await
        .into_diagnostic()?;

    Ok(Box::new(embedder))
}

pub async fn build_reranker(ctx: &AppContext) -> Result<Box<dyn Reranker>> {
    let reranker = LocalRerankerStrategy::connect(&ctx.config.socket_path)
        .await
        .into_diagnostic()?;

    Ok(Box::new(reranker))
}
