package tarjetagenerator.ui;

import tarjetagenerator.model.*;
import tarjetagenerator.service.*;
import java.util.*;

public class MenuConsola {
    private final Scanner scanner;
    private final GeneradorTarjetas generador;
    private final FileService fileService;
    private final DatabaseService databaseService;

    // Paleta de colores Hacker / Terminal Retro
    private static final String G = "\u001B[32m";    // Verde (Matrix)
    private static final String BG = "\u001B[1;32m"; // Verde Negrita
    private static final String R = "\u001B[31m";    // Rojo (Alerta)
    private static final String Y = "\u001B[33m";    // Amarillo (Advertencia)
    private static final String B = "\u001B[34m";    // Azul
    private static final String C = "\u001B[36m";    // Cian (Info)
    private static final String W = "\u001B[37m";    // Blanco
    private static final String RESET = "\u001B[0m";

    public MenuConsola() {
        this.scanner = new Scanner(System.in);
        this.generador = new GeneradorTarjetas();
        this.fileService = new FileService();
        this.databaseService = new DatabaseService();
    }

    public void iniciar() {
        limpiarPantalla();
        mostrarBootSequence();
        mostrarBanner();

        while (true) {
            mostrarMenuPrincipal();
            int opcion = leerOpcion();

            switch (opcion) {
                case 1 -> generarTarjetas();
                case 2 -> mostrarInfo();
                case 3 -> {
                    System.out.println(R + "\n[!] TERMINANDO CONEXIÓN..." + RESET);
                    pausa(500);
                    System.out.println(G + "[+] CIERRE DE SISTEMA COMPLETADO. ADIÓS, OPERADOR." + RESET);
                    return;
                }
                default -> System.out.println(R + "\n[!] ACCESO DENEGADO: COMANDO INVÁLIDO" + RESET);
            }
        }
    }

    private void mostrarBootSequence() {
        String[] logs = {
                "[*] INICIALIZANDO KERNEL...",
                "[*] CARGANDO ALGORITMO_LUHN_V2.1...",
                "[*] ESTABLECIENDO ENLACE CON BASE DE DATOS H2...",
                "[*] VERIFICANDO CAPAS DE ENCRIPTACIÓN...",
                "[*] CONEXIÓN SEGURA ESTABLECIDA."
        };
        for (String log : logs) {
            System.out.println(G + log + RESET);
            pausa(300);
        }
        System.out.println("\n");
    }

    private void mostrarBanner() {
        System.out.println(G + "╔══════════════════════════════════════════════════════════════════╗");
        System.out.println(BG + "   ______               ______                                     ");
        System.out.println("  / ____/___ __________/ /     / ____/___  ____  ___  _________ _/ /_____  _____");
        System.out.println(" / /   / __ `/ ___/ __  /     / / __/ _ \\/ __ \\/ _ \\/ ___/ __ `/ __/ __ \\/ ___/");
        System.out.println("/ /___/ /_/ / /  / /_/ /     / /_/ /  __/ / / /  __/ /  / /_/ / /_/ /_/ / /    ");
        System.out.println("\\____/\\__,_/_/   \\__,_/      \\____/\\___/_/ /_/\\___/_/   \\__,_/\\__/\\____/_/     ");
        System.out.println(G + "\n             >> GENERADOR DE DATOS Y ENCRIPTACIÓN <<               ");
        System.out.println("╚══════════════════════════════════════════════════════════════════╝" + RESET);
    }

    private void mostrarMenuPrincipal() {
        System.out.println(G + "\n┌─── " + W + "INTERFAZ DE NÚCLEO" + G + " ──────────────────────────────────────────┐");
        System.out.println("│ " + BG + "[1]" + G + " Generar Tarjetas de Crédito                               │");
        System.out.println("│ " + BG + "[2]" + G + " Reporte del Sistema                                       │");
        System.out.println("│ " + BG + "[3]" + G + " Finalizar Sesión                                          │");
        System.out.println("└────────────────────────────────────────────────────────────────┘");
        System.out.print(BG + "OPERADOR@TERMINAL:~$ " + RESET);
    }

    private int leerOpcion() {
        try {
            return Integer.parseInt(scanner.nextLine().trim());
        } catch (NumberFormatException e) {
            return -1;
        }
    }

    private void mostrarInfo() {
        System.out.println(C + "\n[REPORTE DEL SISTEMA]");
        System.out.println(G + "--------------------------------------------------------------------");
        System.out.println(W + "ESTADO_MOD_10:  " + G + "ACTIVO");
        System.out.println(W + "ENLACE_DB:      " + G + "LOCAL_H2_SQL");
        System.out.println(W + "SALIDA_ARCHIVOS:" + G + " DIRECTORIO: /output/");
        System.out.println(W + "ESQUEMAS_DISP:  ");
        TipoTarjeta.mostrarOpciones();
        System.out.println(G + "--------------------------------------------------------------------" + RESET);
    }

    private void generarTarjetas() {
        System.out.println(Y + "\n[!] CONFIGURANDO PROTOCOLOS DE GENERACIÓN..." + RESET);
        TipoTarjeta.mostrarOpciones();
        System.out.print(BG + "\n[?] SELECCIONE ID DE ESQUEMA: " + RESET);

        int tipoOpcion = leerOpcion();
        TipoTarjeta tipo = TipoTarjeta.fromOpcion(tipoOpcion);

        if (tipo == null) {
            System.out.println(R + "[!] ERROR: ESQUEMA NO VÁLIDO - OPERACIÓN ABORTADA" + RESET);
            return;
        }

        System.out.print(BG + "[?] CANTIDAD DE CARGA (1-1000): " + RESET);
        int cantidad;
        try {
            cantidad = Integer.parseInt(scanner.nextLine().trim());
            if (cantidad <= 0 || cantidad > 1000) {
                System.out.println(R + "[!] ERROR: PREVENCIÓN DE DESBORDAMIENTO - RANGO 1-1000" + RESET);
                return;
            }
        } catch (NumberFormatException e) {
            System.out.println(R + "[!] ERROR: TIPO DE DATO NO COMPATIBLE" + RESET);
            return;
        }

        System.out.print(G + "\n[*] CALCULANDO SUMAS DE COMPROBACIÓN LUHN [");
        for (int i = 0; i < 10; i++) {
            pausa(150);
            System.out.print("#");
        }
        System.out.println("] 100%\n" + RESET);

        List<TarjetaCredito> tarjetas = generador.generarTarjetas(cantidad, tipo);

        System.out.println(G + ">> FLUJO DE DATOS DECODIFICADOS <<");
        System.out.println(G + "════════════════════════════════════════════════════════════════════" + RESET);

        for (int i = 0; i < tarjetas.size(); i++) {
            String raw = tarjetas.get(i).formatoEspecificado();
            System.out.printf(G + " [%03d] " + W + "=> " + G + "%s\n" + RESET, (i + 1), raw);
            if (cantidad < 100) pausa(30); // Solo hacer scroll visual si no son demasiadas
        }
        System.out.println(G + "════════════════════════════════════════════════════════════════════" + RESET);

        System.out.println(Y + "\n[?] SELECCIONE DESTINO DE ALMACENAMIENTO:");
        System.out.println(G + " [1] EXPORTAR_A_TXT");
        System.out.println(" [2] REGISTRAR_EN_BD");
        System.out.println(" [3] EJECUTAR_AMBOS");
        System.out.println(" [4] DESCARTAR_DATOS");
        System.out.print(BG + "\nOPERADOR@ALMACENAMIENTO:~$ " + RESET);

        int opcionGuardado = leerOpcion();

        switch (opcionGuardado) {
            case 1 -> {
                String archivo = fileService.guardarEnArchivo(tarjetas);
                System.out.println(G + "[+] ARCHIVO_CREADO: " + archivo + RESET);
            }
            case 2 -> {
                System.out.println(C + "[*] INICIANDO PROTOCOLO SQL_HANDSHAKE..." + RESET);
                databaseService.inicializarBaseDatos();
                databaseService.guardarTarjetas(tarjetas);
                System.out.println(G + "[+] TRANSACCIÓN_BD_EXITOSA" + RESET);
            }
            case 3 -> {
                fileService.guardarEnArchivo(tarjetas);
                databaseService.inicializarBaseDatos();
                databaseService.guardarTarjetas(tarjetas);
                System.out.println(G + "[+] REDUNDANCIA COMPLETADA: ARCHIVO Y BD SINCRONIZADOS" + RESET);
            }
            default -> System.out.println(Y + "[!] DATOS VOLATILIZADOS (NO GUARDADOS)" + RESET);
        }
    }

    private void pausa(int ms) {
        try { Thread.sleep(ms); } catch (InterruptedException ignored) {}
    }

    private void limpiarPantalla() {
        // Funciona en terminales modernas/Linux/Mac. En Windows CMD depende de la versión.
        System.out.print("\033[H\033[2J");
        System.out.flush();
    }
}