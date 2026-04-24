use base64::{Engine as _, engine::general_purpose};
use rand::Rng;

pub fn 1encriptar_basico(texto: &str) -> String {
    // Encriptación básica para demostración
    let mut rng = rand::thread_rng();
    let salt: u8 = rng.gen();

    let encriptado: String = texto
        .chars()
        .map(|c| ((c as u8) ^ salt) as char)
        .collect();

    general_purpose::STANDARD.encode(format!("{:02x}{}", salt, encriptado))
}

pub fn desencriptar_basico(encriptado: &str) -> Option<String> {
    if let Ok(decodificado) = general_purpose::STANDARD.decode(encriptado) {
        if decodificado.len() > 2 {
            let salt = u8::from_str_radix(&format!("{:02x}", decodificado[0]), 16).ok()?;

            let desencriptado: String = decodificado[2..]
                .iter()
                .map(|&c| ((c ^ salt) as char))
                .collect();

            Some(desencriptado)
        } else {
            None
        }
    } else {
        None
    }
}