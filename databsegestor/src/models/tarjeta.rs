use serde::{Deserialize, Serialize};
use crate::utils::validators;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Tarjeta {
    #[serde(skip_serializing_if = "Option::is_none")]
    pub id_tarjeta: Option<u64>,
    pub numero: String,
    pub mes: u32,
    pub anio: u32,
    pub ccv: u32,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TarjetaResponse {
    #[serde(alias = "idTarjeta")]
    pub id_tarjeta: Option<u64>,
    pub numero: String,
    pub mes: u32,
    pub anio: u32,
    pub ccv: u32,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct MensajeResponse {
    pub mensaje: String,
}

impl Tarjeta {
    pub fn new(numero: String, mes: u32, anio: u32, ccv: u32) -> Self {
        Self {
            id_tarjeta: None,
            numero,
            mes,
            anio,
            ccv,
        }
    }

    pub fn validar(&self) -> Result<(), Vec<String>> {
        let mut errores = Vec::new();

        if !validators::validar_numero_tarjeta(&self.numero) {
            errores.push("El número debe tener 16 dígitos".to_string());
        }

        if !validators::validar_mes(self.mes) {
            errores.push("El mes debe ser entre 1 y 12".to_string());
        }

        if !validators::validar_anio(self.anio) {
            errores.push("El año debe ser válido".to_string());
        }

        if !validators::validar_ccv(self.ccv) {
            errores.push("El CCV debe tener 3 dígitos".to_string());
        }

        if errores.is_empty() {
            Ok(())
        } else {
            Err(errores)
        }
    }

    pub fn enmascarar_numero(&self) -> String {
        if self.numero.len() >= 4 {
            format!("****-****-****-{}", &self.numero[self.numero.len()-4..])
        } else {
            "****".to_string()
        }
    }
}

impl From<TarjetaResponse> for Tarjeta {
    fn from(response: TarjetaResponse) -> Self {
        Self {
            id_tarjeta: response.id_tarjeta,
            numero: response.numero,
            mes: response.mes,
            anio: response.anio,
            ccv: response.ccv,
        }
    }
}