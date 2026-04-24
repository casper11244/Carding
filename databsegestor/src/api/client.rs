use reqwest::{Client, Response, StatusCode};
use serde::{de::DeserializeOwned, Serialize};
use thiserror::Error;

#[derive(Error, Debug)]
pub enum ApiError {
    #[error("Error de conexión: {0}")]
    Connection(String),
    #[error("Error HTTP {0}: {1}")]
    HttpError(u16, String),
    #[error("Error de serialización: {0}")]
    Serialization(String),
}

pub struct ApiClient {
    client: Client,
    base_url: String,
}

impl ApiClient {
    pub fn new(base_url: &str) -> Result<Self, ApiError> {
        let client = Client::builder()
            .timeout(std::time::Duration::from_secs(10))
            .build()
            .map_err(|e| ApiError::Connection(e.to_string()))?;

        Ok(Self {
            client,
            base_url: base_url.to_string(),
        })
    }

    pub async fn get<T: DeserializeOwned>(&self, path: &str) -> Result<T, ApiError> {
        let url = format!("{}{}", self.base_url, path);
        let response = self.client.get(&url).send().await
            .map_err(|e| ApiError::Connection(e.to_string()))?;

        self.handle_response(response).await
    }

    pub async fn post<T: Serialize, R: DeserializeOwned>(&self, path: &str, body: &T) -> Result<R, ApiError> {
        let url = format!("{}{}", self.base_url, path);
        let response = self.client.post(&url)
            .json(body)
            .send().await
            .map_err(|e| ApiError::Connection(e.to_string()))?;

        self.handle_response(response).await
    }

    pub async fn put<T: Serialize, R: DeserializeOwned>(&self, path: &str, body: &T) -> Result<R, ApiError> {
        let url = format!("{}{}", self.base_url, path);
        let response = self.client.put(&url)
            .json(body)
            .send().await
            .map_err(|e| ApiError::Connection(e.to_string()))?;

        self.handle_response(response).await
    }

    pub async fn delete<R: DeserializeOwned>(&self, path: &str) -> Result<R, ApiError> {
        let url = format!("{}{}", self.base_url, path);
        let response = self.client.delete(&url).send().await
            .map_err(|e| ApiError::Connection(e.to_string()))?;

        self.handle_response(response).await
    }

    async fn handle_response<T: DeserializeOwned>(&self, response: Response) -> Result<T, ApiError> {
        let status = response.status();

        if status.is_success() {
            response.json::<T>().await
                .map_err(|e| ApiError::Serialization(e.to_string()))
        } else if status == StatusCode::NOT_FOUND {
            let error_body = response.text().await.unwrap_or_default();
            Err(ApiError::HttpError(404, error_body))
        } else if status == StatusCode::BAD_REQUEST {
            let error_body = response.text().await.unwrap_or_default();
            Err(ApiError::HttpError(400, error_body))
        } else {
            let error_body = response.text().await.unwrap_or_default();
            Err(ApiError::HttpError(status.as_u16(), error_body))
        }
    }
}