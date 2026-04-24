use std::{thread, time::Duration};
use std::io::{self, Write};

pub struct Animaciones;

impl Animaciones {
    pub fn escribir_efecto_maquina(texto: &str) {
        for c in texto.chars() {
            print!("{}", c);
            io::stdout().flush().unwrap();
            thread::sleep(Duration::from_millis(30));
        }
        println!();
    }

    pub fn barra_progreso(mensaje: &str, segundos: u64) {
        print!("{} ", mensaje);
        for i in 0..20 {
            print!("█");
            io::stdout().flush().unwrap();
            thread::sleep(Duration::from_millis(segundos * 50));
        }
        println!(" 100%");
    }

    pub fn spinner(mensaje: &str, duracion: Duration) {
        let spinner_chars = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏'];
        let start = std::time::Instant::now();

        while start.elapsed() < duracion {
            for c in &spinner_chars {
                print!("\r{} {} ", c, mensaje);
                io::stdout().flush().unwrap();
                thread::sleep(Duration::from_millis(80));
            }
        }
        println!();
    }

    pub fn efecto_glitch(texto: &str) {
        for _ in 0..3 {
            print!("\r{}", texto);
            thread::sleep(Duration::from_millis(100));
            print!("\r{}", "█".repeat(texto.len()));
            thread::sleep(Duration::from_millis(50));
        }
        print!("\r{}\n", texto);
    }
}