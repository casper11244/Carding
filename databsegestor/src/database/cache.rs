use crate::models::tarjeta::Tarjeta;
use std::collections::HashMap;
use std::sync::Arc;
use tokio::sync::Mutex;

pub struct Cache {
    data: Arc<Mutex<HashMap<u64, Tarjeta>>>,
}

impl Cache {
    pub fn new() -> Self {
        Self {
            data: Arc::new(Mutex::new(HashMap::new())),
        }
    }

    pub async fn guardar(&self, tarjeta: &Tarjeta) {
        if let Some(id) = tarjeta.id_tarjeta {
            let mut cache = self.data.lock().await;
            cache.insert(id, tarjeta.clone());
        }
    }

    pub async fn obtener(&self, id: u64) -> Option<Tarjeta> {
        let cache = self.data.lock().await;
        cache.get(&id).cloned()
    }

    pub async fn obtener_todas(&self) -> Vec<Tarjeta> {
        let cache = self.data.lock().await;
        cache.values().cloned().collect()
    }

    pub async fn eliminar(&self, id: u64) {
        let mut cache = self.data.lock().await;
        cache.remove(&id);
    }

    pub async fn limpiar(&self) {
        let mut cache = self.data.lock().await;
        cache.clear();
    }
}