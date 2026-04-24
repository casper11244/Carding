pub struct Endpoints;

impl Endpoints {
    pub const TARJETAS: &str = "/tarjetas";

    pub fn tarjeta_por_id(id: u64) -> String {
        format!("/tarjetas/{}", id)
    }

    pub fn buscar_por_anio(anio: u32) -> String {
        format!("/tarjetas/buscar?anio={}", anio)
    }
}