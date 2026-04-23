package tarjetagenerator.ui;

import tarjetagenerator.model.*;
import tarjetagenerator.service.*;
import java.util.*;

public class MenuConsola {
    private final Scanner scanner;
    private final GeneradorTarjetas generador;
    private final FileService fileService;
    private final DatabaseService databaseService;
    private static final String GREEN = "\u001B[32m";
    private static final String CYAN = "\u001B[36m";
    private static final String RED = "\u001B[31m";
    private static final String YELLOW = "\u001B[33m";
    private static final String RESET = "\u001B[0m";
    private static final String BOLD = "\u001B[1m";

    public MenuConsola() {
        this.scanner = new Scanner(System.in);
        this.generador = new GeneradorTarjetas();
        this.fileService = new FileService();
        this.databaseService = new DatabaseService();
    }

    public void iniciar() {
        mostrarBanner();

        while (true) {
            mostrarMenuPrincipal();
            int opcion = leerOpcion();

            switch (opcion) {
                case 1 -> generarTarjetas();
                case 2 -> mostrarInfo();
                case 3 -> {
                    System.out.println(CYAN + "\n[*] Shutting down..." + RESET);
                    return;
                }
                default -> System.out.println(RED + "\n[!] Invalid option" + RESET);
            }
        }
    }

    private void mostrarBanner() {
        System.out.println(CYAN + BOLD);
        System.out.println("╔══════════════════════════════════════════════════════════════════╗");
        System.out.println("║                                                                  ║");
        System.out.println("║     ██████╗ █████╗ ██████╗ ██████╗ ██╗███╗   ██╗ ██████╗         ║");
        System.out.println("║    ██╔════╝██╔══██╗██╔══██╗██╔══██╗██║████╗  ██║██╔════╝         ║");
        System.out.println("║    ██║     ███████║██████╔╝██║  ██║██║██╔██╗ ██║██║  ███╗        ║");
        System.out.println("║    ██║     ██╔══██║██╔══██╗██║  ██║██║██║╚██╗██║██║   ██║        ║");
        System.out.println("║    ╚██████╗██║  ██║██║  ██║██████╔╝██║██║ ╚████║╚██████╔╝        ║");
        System.out.println("║     ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝ ╚═╝╚═╝  ╚═══╝ ╚═════╝         ║");
        System.out.println("║                                                                  ║");
        System.out.println("║              » LUHN ALGORITHM CARD GENERATOR v2.1 «              ║");
        System.out.println("║                    » JAVA 21 | MAVEN BUILD «                     ║");
        System.out.println("╚══════════════════════════════════════════════════════════════════╝");
        System.out.println(RESET);
    }

    private void mostrarMenuPrincipal() {
        System.out.println(CYAN + "\n┌────────────────────────────────────────────────────────────────┐");
        System.out.println("│                         MAIN MENU                               │");
        System.out.println("├────────────────────────────────────────────────────────────────┤");
        System.out.println("│  [1] Generate Cards                                             │");
        System.out.println("│  [2] System Information                                         │");
        System.out.println("│  [3] Exit                                                       │");
        System.out.println("└────────────────────────────────────────────────────────────────┘");
        System.out.print(RESET + "\n[?] Select option > ");
    }

    private int leerOpcion() {
        try {
            return Integer.parseInt(scanner.nextLine().trim());
        } catch (NumberFormatException e) {
            return -1;
        }
    }

    private void mostrarInfo() {
        System.out.println(CYAN + "\n┌────────────────────────────────────────────────────────────────┐");
        System.out.println("│                     SYSTEM INFORMATION                          │");
        System.out.println("├────────────────────────────────────────────────────────────────┤");
        System.out.println("│  Available Card Types:                                          │");
        System.out.println("│                                                                  │");
        TipoTarjeta.mostrarOpciones();
        System.out.println("│                                                                  │");
        System.out.println("│  Output Format: number|year|month|cvv                           │");
        System.out.println("│  Algorithm: Luhn (Mod 10)                                       │");
        System.out.println("│  Storage: File (output/) & H2 Database                          │");
        System.out.println("└────────────────────────────────────────────────────────────────┘" + RESET);
    }

    private void generarTarjetas() {
        System.out.println(CYAN + "\n┌────────────────────────────────────────────────────────────────┐");
        System.out.println("│                      CARD GENERATION                            │");
        System.out.println("└────────────────────────────────────────────────────────────────┘" + RESET);

        System.out.println(YELLOW + "\n[?] Select card type:" + RESET);
        TipoTarjeta.mostrarOpciones();
        System.out.print(GREEN + "\n[>] Enter option (1-6): " + RESET);

        int tipoOpcion = leerOpcion();
        TipoTarjeta tipo = TipoTarjeta.fromOpcion(tipoOpcion);

        if (tipo == null) {
            System.out.println(RED + "[!] Invalid card type" + RESET);
            return;
        }

        System.out.print(GREEN + "[>] Number of cards to generate: " + RESET);
        int cantidad;
        try {
            cantidad = Integer.parseInt(scanner.nextLine().trim());
            if (cantidad <= 0 || cantidad > 1000) {
                System.out.println(RED + "[!] Quantity must be between 1 and 1000" + RESET);
                return;
            }
        } catch (NumberFormatException e) {
            System.out.println(RED + "[!] Invalid quantity" + RESET);
            return;
        }

        System.out.print(CYAN + "\n[*] Generating " + cantidad + " " + tipo.getNombre() + " cards");
        for (int i = 0; i < 3; i++) {
            try { Thread.sleep(300); System.out.print("."); } catch (InterruptedException e) {}
        }
        System.out.println(RESET);

        List<TarjetaCredito> tarjetas = generador.generarTarjetas(cantidad, tipo);

        System.out.println(GREEN + "\n[✓] Generation complete! " + tarjetas.size() + " cards generated\n" + RESET);
        System.out.println(CYAN + "┌─────────────────────────────────────────────────────────────────────────────┐");
        System.out.println("│                         GENERATED CARDS                                       │");
        System.out.println("├─────────────────────────────────────────────────────────────────────────────┤");
        System.out.println("│  Format: NUMBER|YEAR|MONTH|CVV                                                │");
        System.out.println("├─────────────────────────────────────────────────────────────────────────────┤" + RESET);

        int contador = 1;
        for (TarjetaCredito tarjeta : tarjetas) {
            if (contador % 2 == 0) {
                System.out.printf(CYAN + "│  [%03d] " + RESET + "%s" + CYAN + "  │\n" + RESET,
                        contador, tarjeta.formatoEspecificado());
            } else {
                System.out.printf("│  [%03d] %s  │\n", contador, tarjeta.formatoEspecificado());
            }
            contador++;
        }

        System.out.println(CYAN + "└─────────────────────────────────────────────────────────────────────────────┘" + RESET);

        System.out.println(CYAN + "\n┌────────────────────────────────────────────────────────────────┐");
        System.out.println("│                      SAVE OPTIONS                               │");
        System.out.println("├────────────────────────────────────────────────────────────────┤");
        System.out.println("│  [1] Save to text file                                          │");
        System.out.println("│  [2] Save to H2 database                                        │");
        System.out.println("│  [3] Save to both                                               │");
        System.out.println("│  [4] Don't save                                                 │");
        System.out.println("└────────────────────────────────────────────────────────────────┘");
        System.out.print(RESET + "\n[?] Select option > ");

        int opcionGuardado = leerOpcion();

        switch (opcionGuardado) {
            case 1 -> {
                String archivo = fileService.guardarEnArchivo(tarjetas);
                System.out.println(GREEN + "[+] Cards saved to: " + archivo + RESET);
            }
            case 2 -> {
                databaseService.inicializarBaseDatos();
                databaseService.guardarTarjetas(tarjetas);
            }
            case 3 -> {
                String archivo = fileService.guardarEnArchivo(tarjetas);
                System.out.println(GREEN + "[+] Cards saved to: " + archivo + RESET);
                databaseService.inicializarBaseDatos();
                databaseService.guardarTarjetas(tarjetas);
            }
            case 4 -> System.out.println(YELLOW + "[*] Cards not saved" + RESET);
            default -> System.out.println(RED + "[!] Invalid option, cards not saved" + RESET);
        }

        System.out.println(CYAN + "\n[+] Operation completed successfully!" + RESET);
        System.out.println("    • Type: " + tipo.getNombre());
        System.out.println("    • Generated: " + tarjetas.size() + " cards");
        System.out.println("    • Format: number|year|month|cvv");
    }
}