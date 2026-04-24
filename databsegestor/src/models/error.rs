use thiserror::Error;

#[derive(Error, Debug)]
pub enum AppError {
    #[error("Error de API: {0}")]
    ApiError(#[from] crate::api::client::ApiError),

    #[error("Error de validación: {0:?}")]
    ValidacionError(Vec<String>),

    #[error("Error de caché: {0}")]
    CacheError(String),

    #[error("Error de IO: {0}")]
    IoError(#[from] std::io::Error),
}