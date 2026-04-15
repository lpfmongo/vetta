use thiserror::Error;

#[derive(Error, Debug)]
pub enum RerankerError {
    #[error("gRPC error: {0}")]
    Grpc(#[from] tonic::Status),
    #[error("Connection error: {0}")]
    Connection(String),
}
