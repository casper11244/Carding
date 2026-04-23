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
    private static final String G = "\u001B[32m";    // Green (Matrix)
    private static final String BG = "\u001B[1;32m"; // Bold Green
    private static final String R = "\u001B[31m";    // Red (Alert)
    private static final String Y = "\u001B[33m";    // Yellow (Warning)
    private static final String B = "\u001B[34m";    // Blue
    private static final String C = "\u001B[36m";    // Cyan (Info)
    private static final String W = "\u001B[37m";    // White
    private static final String RESET = "\u001B[0m";
    private static final String BLINK = "\u001B[5m";

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
                    System.out.println(R + "\n[!] TERMINATING CONNECTION..." + RESET);
                    pausa(500);
                    System.out.println(G + "[+] SYSTEM SHUTDOWN COMPLETE. GOODBYE, OPERATOR." + RESET);
                    return;
                }
                default -> System.out.println(R + "\n[!] ACCESS DENIED: INVALID COMMAND" + RESET);
            }
        }
    }

    private void mostrarBootSequence() {
        String[] logs = {
                "[*] INITIALIZING KERNEL...",
                "[*] LOADING LUHN_ALGO_V2.1...",
                "[*] ESTABLISHING H2 DATABASE LINK...",
                "[*] BYPASSING ENCRYPTION LAYERS...",
                "[*] CONNECTION SECURE."
        };
        for (String log : logs) {
            System.out.println(G + log + RESET);
            pausa(300);
        }
        System.out.println("\n");
    }

    private void mostrarBanner() {
        System.out.println(G + "####################################################################");
        System.out.println(BG + "   ______             __      ______                           ");
        System.out.println("  / ____/___ ________/ /     / ____/__  ____  ___  _________ _/ /_____  _____");
        System.out.println(" / /   / __ `/ ___/ __  /     / / __/ _ \\/ __ \\/ _ \\/ ___/ __ `/ __/ __ \\/ ___/");
        System.out.println("/ /___/ /_/ / /  / /_/ /     / /_/ /  __/ / / /  __/ /  / /_/ / /_/ /_/ / /    ");
        System.out.println("\\____/\\__,_/_/   \\__,_/      \\____/\\___/_/ /_/\\___/_/   \\__,_/\\__/\\____/_/     ");
        System.out.println(G + "\n              >> NETWORK ENCRYPTION & DATA GENERATOR <<             ");
        System.out.println("####################################################################" + RESET);
    }

    private void mostrarMenuPrincipal() {
        System.out.println(G + "\n┌─── " + W + "CORE INTERFACE" + G + " ───────────────────────────────────────────────┐");
        System.out.println("│ " + BG + "[1]" + G + " INJECT_DATA (Generate Cards)                               │");
        System.out.println("│ " + BG + "[2]" + G + " SYS_STATUS  (Information)                                  │");
        System.out.println("│ " + BG + "[3]" + G + " DISCONNECT  (Exit)                                         │");
        System.out.println("└──────────────────────────────────────────────────────────────────┘");
        System.out.print(BG + "OPERATOR@TERMINAL:~$ " + RESET);
    }

    private int leerOpcion() {
        try {
            return Integer.parseInt(scanner.nextLine().trim());
        } catch (NumberFormatException e) {
            return -1;
        }
    }

    private void mostrarInfo() {
        System.out.println(C + "\n[SYSTEM REPORT]");
        System.out.println(G + "--------------------------------------------------------------------");
        System.out.println(W + "MOD_10_STATUS: " + G + "ACTIVE");
        System.out.println(W + "DB_LINK:       " + G + "LOCAL_H2_SQL");
        System.out.println(W + "FILE_OUTPUT:   " + G + "DIRECTORY: /output/");
        System.out.println(W + "CARD_SCHEMES:  ");
        TipoTarjeta.mostrarOpciones();
        System.out.println(G + "--------------------------------------------------------------------" + RESET);
    }

    private void generarTarjetas() {
        System.out.println(Y + "\n[!] TARGETING PROTOCOLS..." + RESET);
        TipoTarjeta.mostrarOpciones();
        System.out.print(BG + "\n[?] SELECT SCHEME ID: " + RESET);

        int tipoOpcion = leerOpcion();
        TipoTarjeta tipo = TipoTarjeta.fromOpcion(tipoOpcion);

        if (tipo == null) {
            System.out.println(R + "[!] ERROR: NULL_POINTER_EXCEPTION - INVALID SCHEME" + RESET);
            return;
        }

        System.out.print(BG + "[?] PAYLOAD QUANTITY (1-1000): " + RESET);
        int cantidad;
        try {
            cantidad = Integer.parseInt(scanner.nextLine().trim());
            if (cantidad <= 0 || cantidad > 1000) {
                System.out.println(R + "[!] ERROR: BUFFER_OVERFLOW_PREVENTION - RANGE 1-1000 ONLY" + RESET);
                return;
            }
        } catch (NumberFormatException e) {
            System.out.println(R + "[!] ERROR: DATA_MISMATCH" + RESET);
            return;
        }

        System.out.print(G + "\n[*] CALCULATING LUHN CHECKSUMS");
        for (int i = 0; i < 5; i++) {
            pausa(200);
            System.out.print(" #");
        }
        System.out.println(" 100%\n" + RESET);

        List<TarjetaCredito> tarjetas = generador.generarTarjetas(cantidad, tipo);

        System.out.println(G + ">> DECODED DATA STREAM <<");
        System.out.println(G + "====================================================================" + RESET);

        for (int i = 0; i < tarjetas.size(); i++) {
            String raw = tarjetas.get(i).formatoEspecificado();
            System.out.printf(G + " [%03d] " + W + ">> " + G + "%s\n" + RESET, (i + 1), raw);
            pausa(50); // Efecto visual de "scroll"
        }
        System.out.println(G + "====================================================================" + RESET);

        System.out.println(Y + "\n[?] SELECT STORAGE DESTINATION:");
        System.out.println(G + " [1] EXPORT_TO_TXT");
        System.out.println(" [2] COMMIT_TO_DB");
        System.out.println(" [3] EXECUTE_BOTH");
        System.out.println(" [4] DISCARD_PAYLOAD");
        System.out.print(BG + "\nOPERATOR@STORAGE:~$ " + RESET);

        int opcionGuardado = leerOpcion();

        switch (opcionGuardado) {
            case 1 -> {
                String archivo = fileService.guardarEnArchivo(tarjetas);
                System.out.println(G + "[+] FILE_CREATED: " + archivo + RESET);
            }
            case 2 -> {
                System.out.println(C + "[*] INITIALIZING SQL_HANDSHAKE..." + RESET);
                databaseService.inicializarBaseDatos();
                databaseService.guardarTarjetas(tarjetas);
                System.out.println(G + "[+] DB_TRANSACTION_SUCCESS" + RESET);
            }
            case 3 -> {
                fileService.guardarEnArchivo(tarjetas);
                databaseService.inicializarBaseDatos();
                databaseService.guardarTarjetas(tarjetas);
                System.out.println(G + "[+] REDUNDANCY_SAVED: FILE & DB SYNCED" + RESET);
            }
            default -> System.out.println(Y + "[!] DATA VOLATILIZED (NOT SAVED)" + RESET);
        }
    }

    private void pausa(int ms) {
        try { Thread.sleep(ms); } catch (InterruptedException ignored) {}
    }

    private void limpiarPantalla() {
        System.out.print("\033[H\033[2J");
        System.out.flush();
    }
}