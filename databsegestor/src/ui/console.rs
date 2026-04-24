use crate::services::tarjeta_service::TarjetaService;
use crate::models::tarjeta::Tarjeta;
use crate::ui::animaciones::Animaciones;
use crate::ui::colores::Colores;
use colored::*;
use std::io::{self, Write};
use std::thread;
use std::time::Duration;

pub struct HackerConsole {
    service: TarjetaService,
}

impl HackerConsole {
    pub fn new(service: TarjetaService) -> Self {
        Self { service }
    }

    pub async fn run(&mut self) -> Result<(), Box<dyn std::error::Error>> {
        self.mostrar_banner_inicial();

        loop {
            self.mostrar_menu();

            let opcion = self.leer_opcion();

            match opcion {
                1 => self.crear_tarjeta().await,
                2 => self.listar_tarjetas().await,
                3 => self.ver_tarjeta().await,
                4 => self.actualizar_tarjeta().await,
                5 => self.eliminar_tarjeta().await,
                6 => self.buscar_por_anio().await,
                0 => {
                    self.mostrar_despedida();
                    break;
                }
                _ => self.mostrar_error("Opción inválida"),
            }
        }

        Ok(())
    }

    fn mostrar_banner_inicial(&self) {
        print!("\x1b[2J\x1b[1;1H"); // Limpiar pantalla

        let banner = r#"
    ╔══════════════════════════════════════════════════════════════╗
    ║                 ██████╗ ██████╗ ███████╗██████╗             ║
    ║                ██╔════╝ ██╔══██╗██╔════╝██╔══██╗            ║
    ║                ██║  ███╗██████╔╝█████╗  ██║  ██║            ║
    ║                ██║   ██║██╔══██╗██╔══╝  ██║  ██║            ║
    ║                ╚██████╔╝██████╔╝███████╗██████╔╝            ║
    ║                 ╚═════╝ ╚═════╝ ╚══════╝╚═════╝             ║
    ║                                                              ║
    ║              SISTEMA DE GESTIÓN DE TARJETAS                 ║
    ║                    [ MODO HACKER ]                           ║
    ╚══════════════════════════════════════════════════════════════╝
        "#;

        println!("{}", Colores::verde_neon(banner));
        Animaciones::escribir_efecto_maquina("Inicializando conexión segura...");
        Animaciones::barra_progreso("Conectando a API", 3);
        println!("\n✅ {} {}",
                 Colores::verde("[CONEXIÓN ESTABLECIDA]"),
                 Colores::cyan("API: http://localhost:8080/api/v1")
        );
        println!("{} {}\n",
                 Colores::amarillo("⏰"),
                 Colores::gris(&chrono::Local::now().format("%Y-%m-%d %H:%M:%S").to_string())
        );
    }

    fn mostrar_menu(&self) {
        println!("\n{}", Colores::cyan(&"═".repeat(60)));
        println!("{}", Colores::verde_neon("☠  MENÚ PRINCIPAL - SISTEMA TARJETA DB  ☠"));
        println!("{}", Colores::cyan(&"═".repeat(60)));

        let opciones = [
            ("1", "Crear Tarjeta", "📝"),
            ("2", "Listar Todas las Tarjetas", "📋"),
            ("3", "Buscar Tarjeta por ID", "🔍"),
            ("4", "Actualizar Tarjeta", "🔄"),
            ("5", "Eliminar Tarjeta", "💀"),
            ("6", "Buscar Tarjetas por Año", "📅"),
            ("0", "Salir del Sistema", "👋"),
        ];

        for (key, desc, icon) in opciones.iter() {
            println!("  {} {}  {:<30} {}",
                     Colores::amarillo_bold(&format!("[{}]", key)),
                     icon,
                     Colores::blanco(desc),
                     Colores::gris(" //")
            );
        }
        println!("{}", Colores::cyan(&"═".repeat(60)));
        print!("{} ", Colores::verde_neon(">>>"));
        io::stdout().flush().unwrap();
    }

    async fn crear_tarjeta(&mut self) {
        println!("\n{}", Colores::magenta("╔══════════════════════════════════╗"));
        println!("{}", Colores::magenta("║      CREAR NUEVA TARJETA         ║"));
        println!("{}", Colores::magenta("╚══════════════════════════════════╝"));

        let numero = self.leer_input_con_validacion("Número de tarjeta (16 dígitos)", |v| v.len() == 16);
        let mes = self.leer_numero_con_validacion("Mes (1-12)", |v| v >= 1 && v <= 12);
        let anio = self.leer_numero_con_validacion("Año (2024-2030)", |v| v >= 2024 && v <= 2030);
        let ccv = self.leer_numero_con_validacion("CCV (3 dígitos)", |v| v >= 100 && v <= 999);

        let tarjeta = Tarjeta::new(numero, mes, anio, ccv);

        self.mostrar_animacion_progreso("Creando tarjeta");

        match self.service.crear_tarjeta(tarjeta).await {
            Ok(tarjeta_creada) => {
                println!("\n{} {}",
                         Colores::verde("[✓] TARJETA CREADA EXITOSAMENTE"),
                         Colores::cyan(&format!("ID: {}", tarjeta_creada.id_tarjeta.unwrap_or(0)))
                );
                self.mostrar_detalles_tarjeta(&tarjeta_creada);
            }
            Err(e) => self.mostrar_error(&e.to_string()),
        }
    }

    async fn listar_tarjetas(&mut self) {
        println!("\n{}", Colores::magenta("╔══════════════════════════════════╗"));
        println!("{}", Colores::magenta("║      LISTADO DE TARJETAS         ║"));
        println!("{}", Colores::magenta("╚══════════════════════════════════╝"));

        self.mostrar_animacion_progreso("Consultando base de datos");

        match self.service.listar_tarjetas().await {
            Ok(tarjetas) => {
                if tarjetas.is_empty() {
                    println!("\n{}", Colores::amarillo("[!] No se encontraron tarjetas registradas"));
                } else {
                    println!("\n{} {}",
                             Colores::verde(&format!("[✓] {} TARJETAS ENCONTRADAS", tarjetas.len())),
                             Colores::gris("───")
                    );

                    for tarjeta in &tarjetas {
                        self.mostrar_tarjeta_resumen(tarjeta);
                    }
                }
            }
            Err(e) => self.mostrar_error(&e.to_string()),
        }
    }

    // Agrega estos métodos DENTRO del bloque impl HackerConsole {

    fn leer_opcion(&self) -> u32 {
        loop {
            let mut input = String::new();
            io::stdin().read_line(&mut input).unwrap();
            match input.trim().parse::<u32>() {
                Ok(num) => return num,
                Err(_) => {
                    self.mostrar_error("Por favor, ingresa un número válido");
                    print!("{} ", Colores::verde_neon(">>>"));
                    io::stdout().flush().unwrap();
                }
            }
        }
    }

    fn leer_input_con_validacion<F>(&self, mensaje: &str, validador: F) -> String
    where F: Fn(&str) -> bool
    {
        loop {
            print!("{}: ", Colores::cyan(mensaje));
            io::stdout().flush().unwrap();
            let mut input = String::new();
            io::stdin().read_line(&mut input).unwrap();
            let input = input.trim().to_string();

            if validador(&input) {
                return input;
            } else {
                self.mostrar_error(&format!("Entrada inválida para {}", mensaje.to_lowercase()));
            }
        }
    }

    fn leer_numero_con_validacion<F>(&self, mensaje: &str, validador: F) -> u32
    where F: Fn(u32) -> bool
    {
        loop {
            print!("{}: ", Colores::cyan(mensaje));
            io::stdout().flush().unwrap();
            let mut input = String::new();
            io::stdin().read_line(&mut input).unwrap();

            match input.trim().parse::<u32>() {
                Ok(num) if validador(num) => return num,
                Ok(_) => self.mostrar_error(&format!("El valor no cumple con los requisitos para {}", mensaje.to_lowercase())),
                Err(_) => self.mostrar_error("Por favor, ingresa un número válido"),
            }
        }
    }

    fn mostrar_error(&self, mensaje: &str) {
        println!("\n{} {}", Colores::rojo_error("[ERROR]"), Colores::rojo_error(mensaje));
        thread::sleep(Duration::from_millis(500));
    }

    fn mostrar_animacion_progreso(&self, mensaje: &str) {
        Animaciones::spinner(mensaje, Duration::from_millis(500));
    }

    async fn ver_tarjeta(&mut self) {
        println!("\n{}", Colores::magenta("╔══════════════════════════════════╗"));
        println!("{}", Colores::magenta("║      BUSCAR TARJETA POR ID       ║"));
        println!("{}", Colores::magenta("╚══════════════════════════════════╝"));

        let id = self.leer_numero_con_validacion("ID de la tarjeta", |v| v > 0) as u64;

        self.mostrar_animacion_progreso("Buscando tarjeta");

        match self.service.obtener_tarjeta(id).await {
            Ok(tarjeta) => {
                println!("\n{}", Colores::verde("[✓] TARJETA ENCONTRADA"));
                self.mostrar_detalles_tarjeta(&tarjeta);
            }
            Err(e) => self.mostrar_error(&e.to_string()),
        }
    }

    async fn actualizar_tarjeta(&mut self) {
        println!("\n{}", Colores::magenta("╔══════════════════════════════════╗"));
        println!("{}", Colores::magenta("║      ACTUALIZAR TARJETA          ║"));
        println!("{}", Colores::magenta("╚══════════════════════════════════╝"));

        let id = self.leer_numero_con_validacion("ID de la tarjeta a actualizar", |v| v > 0) as u64;

        let numero = self.leer_input_con_validacion("Nuevo número de tarjeta (16 dígitos)", |v| v.len() == 16);
        let mes = self.leer_numero_con_validacion("Nuevo mes (1-12)", |v| v >= 1 && v <= 12);
        let anio = self.leer_numero_con_validacion("Nuevo año (2024-2030)", |v| v >= 2024 && v <= 2030);
        let ccv = self.leer_numero_con_validacion("Nuevo CCV (3 dígitos)", |v| v >= 100 && v <= 999);

        let tarjeta = Tarjeta::new(numero, mes, anio, ccv);

        self.mostrar_animacion_progreso("Actualizando tarjeta");

        match self.service.actualizar_tarjeta(id, tarjeta).await {
            Ok(tarjeta_actualizada) => {
                println!("\n{}", Colores::verde("[✓] TARJETA ACTUALIZADA EXITOSAMENTE"));
                self.mostrar_detalles_tarjeta(&tarjeta_actualizada);
            }
            Err(e) => self.mostrar_error(&e.to_string()),
        }
    }

    async fn eliminar_tarjeta(&mut self) {
        println!("\n{}", Colores::magenta("╔══════════════════════════════════╗"));
        println!("{}", Colores::magenta("║      ELIMINAR TARJETA            ║"));
        println!("{}", Colores::magenta("╚══════════════════════════════════╝"));

        let id = self.leer_numero_con_validacion("ID de la tarjeta a eliminar", |v| v > 0) as u64;

        self.mostrar_animacion_progreso("Eliminando tarjeta");

        match self.service.eliminar_tarjeta(id).await {
            Ok(mensaje) => {
                println!("\n{} {}",
                         Colores::verde("[✓] TARJETA ELIMINADA"),
                         Colores::cyan(&mensaje)
                );
            }
            Err(e) => self.mostrar_error(&e.to_string()),
        }
    }

    async fn buscar_por_anio(&mut self) {
        println!("\n{}", Colores::magenta("╔══════════════════════════════════╗"));
        println!("{}", Colores::magenta("║      BUSCAR TARJETAS POR AÑO     ║"));
        println!("{}", Colores::magenta("╚══════════════════════════════════╝"));

        let anio = self.leer_numero_con_validacion("Año de búsqueda (2024-2030)", |v| v >= 2024 && v <= 2030);

        self.mostrar_animacion_progreso("Buscando tarjetas");

        match self.service.buscar_por_anio(anio).await {
            Ok(tarjetas) => {
                if tarjetas.is_empty() {
                    println!("\n{}", Colores::amarillo("[!] No se encontraron tarjetas para el año especificado"));
                } else {
                    println!("\n{} {}",
                             Colores::verde(&format!("[✓] {} TARJETAS ENCONTRADAS", tarjetas.len())),
                             Colores::gris("───")
                    );
                    for tarjeta in &tarjetas {
                        self.mostrar_tarjeta_resumen(tarjeta);
                    }
                }
            }
            Err(e) => self.mostrar_error(&e.to_string()),
        }
    }

    fn mostrar_despedida(&self) {
        println!("\n{}", Colores::cyan(&"═".repeat(60)));
        println!("{}", Colores::verde_neon("¡DESCONEXIÓN SEGURA REALIZADA!"));
        println!("{}", Colores::gris("Cerrando todos los circuitos..."));
        println!("{}", Colores::cyan(&"═".repeat(60)));
        Animaciones::escribir_efecto_maquina("Hasta la próxima, hacker...");
    }

    fn mostrar_tarjeta_resumen(&self, tarjeta: &Tarjeta) {
        println!("  {} {} {:>6}/{:02}  {}",
                 Colores::cyan("╭─"),
                 Colores::amarillo(&tarjeta.enmascarar_numero()),
                 Colores::blanco(&tarjeta.anio.to_string()),
                 Colores::blanco(&tarjeta.mes.to_string()),
                 Colores::gris(&format!("(ID: {})", tarjeta.id_tarjeta.unwrap_or(0)))
        );
    }

    fn mostrar_detalles_tarjeta(&self, tarjeta: &Tarjeta) {
        println!("\n  {}", Colores::cyan("DETALLES DE LA TARJETA:"));
        println!("  {} {}", Colores::gris("Número:"), Colores::amarillo(&tarjeta.enmascarar_numero()));
        println!("  {} {}", Colores::gris("Mes:"), Colores::blanco(&tarjeta.mes.to_string()));
        println!("  {} {}", Colores::gris("Año:"), Colores::blanco(&tarjeta.anio.to_string()));
    }

    // ... [Continúan más métodos de la consola hacker]
}