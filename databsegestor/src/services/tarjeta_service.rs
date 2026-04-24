use crate::api::client::{ApiClient, ApiError};
use crate::api::endpoints::Endpoints;
use crate::models::tarjeta::{Tarjeta, TarjetaResponse, MensajeResponse};
use std::sync::Arc;
use tokio::sync::Mutex;

pub struct TarjetaService {
    client: Arc<Mutex<ApiClient>>,
}

impl TarjetaService {
    pub fn new(client: Arc<Mutex<ApiClient>>) -> Self {
        Self { client }
    }

    pub async fn crear_tarjeta(&self, tarjeta: Tarjeta) -> Result<Tarjeta, ApiError> {
        let client = self.client.lock().await;
        let response: TarjetaResponse = client.post(Endpoints::TARJETAS, &tarjeta).await?;
        Ok(Tarjeta::from(response))
    }

    pub async fn listar_tarjetas(&self) -> Result<Vec<Tarjeta>, ApiError> {
        let client = self.client.lock().await;
        let response: Vec<TarjetaResponse> = client.get(Endpoints::TARJETAS).await?;
        Ok(response.into_iter().map(Tarjeta::from).collect())
    }

    pub async fn obtener_tarjeta(&self, id: u64) -> Result<Tarjeta, ApiError> {
        let client = self.client.lock().await;
        let response: TarjetaResponse = client.get(&Endpoints::tarjeta_por_id(id)).await?;
        Ok(Tarjeta::from(response))
    }

    pub async fn actualizar_tarjeta(&self, id: u64, tarjeta: Tarjeta) -> Result<Tarjeta, ApiError> {
        let client = self.client.lock().await;
        let response: TarjetaResponse = client.put(&Endpoints::tarjeta_por_id(id), &tarjeta).await?;
        Ok(Tarjeta::from(response))
    }

    pub async fn eliminar_tarjeta(&self, id: u64) -> Result<String, ApiError> {
        let client = self.client.lock().await;
        let response: MensajeResponse = client.delete(&Endpoints::tarjeta_por_id(id)).await?;
        Ok(response.mensaje)
    }

    pub async fn buscar_por_anio(&self, anio: u32) -> Result<Vec<Tarjeta>, ApiError> {
        let client = self.client.lock().await;
        let response: Vec<TarjetaResponse> = client.get(&Endpoints::buscar_por_anio(anio)).await?;
        Ok(response.into_iter().map(Tarjeta::from).collect())
    }
}