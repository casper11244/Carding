use colored::*;

pub struct Colores;

impl Colores {
    pub fn verde_neon(texto: &str) -> String {
        texto.green().bold().to_string()
    }

    pub fn cian_neon(texto: &str) -> String {
        texto.cyan().bold().to_string()
    }

    pub fn rojo_error(texto: &str) -> String {
        texto.red().bold().to_string()
    }

    pub fn gris_oscuro(texto: &str) -> String {
        texto.dimmed().to_string()
    }

    pub fn titulo(texto: &str) -> String {
        texto.bright_green().bold().underline().to_string()
    }

    pub fn verde(msg: &str) -> ColoredString {
        msg.green()
    }

    pub fn cyan(msg: &str) -> ColoredString {
        msg.cyan()
    }

    pub fn amarillo(msg: &str) -> ColoredString {
        msg.yellow()
    }

    pub fn amarillo_bold(msg: &str) -> ColoredString {
        msg.yellow().bold()
    }

    pub fn gris(msg: &str) -> ColoredString {
        msg.dimmed()
    }

    pub fn blanco(msg: &str) -> ColoredString {
        msg.white()
    }

    pub fn magenta(msg: &str) -> ColoredString {
        msg.magenta()
    }
}