pub fn validar_numero_tarjeta(numero: &str) -> bool {
    numero.len() == 16 && numero.chars().all(|c| c.is_digit(10))
}

pub fn validar_mes(mes: u32) -> bool {
    mes >= 1 && mes <= 12
}

pub fn validar_anio(anio: u32) -> bool {
    anio >= 2024 && anio <= 2100
}

pub fn validar_ccv(ccv: u32) -> bool {
    ccv >= 100 && ccv <= 999
}

pub fn validar_id(id: &str) -> Result<u64, String> {
    id.parse::<u64>()
        .map_err(|_| "El ID debe ser un número válido".to_string())
}