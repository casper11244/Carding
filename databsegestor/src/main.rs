mod api;
mod models;
mod ui;
mod services;
mod database;
mod utils;

use ui::console::HackerConsole;
use services::tarjeta_service::TarjetaService;
use std::sync::Arc;
use tokio::sync::Mutex;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    // Inicializar el cliente HTTP
    let client = api::client::ApiClient::new("http://localhost:8080/api/v1")?;
    let client = Arc::new(Mutex::new(client));

    // Inicializar el servicio de tarjetas
    let tarjeta_service = TarjetaService::new(client);

    // Inicializar y ejecutar la consola hacker
    let mut console = HackerConsole::new(tarjeta_service);
    console.run().await?;

    Ok(())
}