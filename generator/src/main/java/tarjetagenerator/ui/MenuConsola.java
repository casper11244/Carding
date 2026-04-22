package tarjetagenerator.ui;

import tarjetagenerator.model.*;
import tarjetagenerator.service.*;
import java.util.*;

public class MenuConsola {
    private final Scanner scanner;
    private final GeneradorTarjetas generador;
    private final FileService fileService;
    private final DatabaseService databaseService;

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
                case 2 -> mostrarTiposTarjeta();
                case 3 -> {
                    System.out.println("\n¡Hasta luego!");
                    return;
                }
                default -> System.out.println("\n✗ Opción no válida");
            }
        }
    }

    private void mostrarBanner() {
        System.out.println("=".repeat(60));
        System.out.println("    GENERADOR DE TARJETAS DE CRÉDITO - ALGORITMO LUHN");
        System.out.println("=".repeat(60));
    }

    private void mostrarMenuPrincipal() {
        System.out.println("\n╔════════════════════════════════════════════════════════╗");
        System.out.println("║                    MENÚ PRINCIPAL                      ║");
        System.out.println("╠════════════════════════════════════════════════════════╣");
        System.out.println("║  1. Generar tarjetas                                   ║");
        System.out.println("║  2. Ver tipos de tarjeta disponibles                   ║");
        System.out.println("║  3. Salir                                              ║");
        System.out.println("╚════════════════════════════════════════════════════════╝");
        System.out.print("Seleccione una opción: ");
    }

    private int leerOpcion() {
        try {
            return Integer.parseInt(scanner.nextLine().trim());
        } catch (NumberFormatException e) {
            return -1;
        }
    }

    private void mostrarTiposTarjeta() {
        System.out.println("\n╔════════════════════════════════════════════════════════╗");
        System.out.println("║            TIPOS DE TARJETA DISPONIBLES                ║");
        System.out.println("╠════════════════════════════════════════════════════════╣");

        for (TipoTarjeta tipo : TipoTarjeta.values()) {
            System.out.printf("║  • %-20s (Prefijo: %-6s, Longitud: %d)%n",
                    tipo.getNombre(), tipo.getPrefijo(), tipo.getLongitud());
        }

        System.out.println("╚════════════════════════════════════════════════════════╝");
    }

    private void generarTarjetas() {
        System.out.println("\n╔════════════════════════════════════════════════════════╗");
        System.out.println("║              GENERACIÓN DE TARJETAS                    ║");
        System.out.println("╚════════════════════════════════════════════════════════╝");

        // Seleccionar tipo de tarjeta
        System.out.println("\nTipos disponibles: VISA, MASTERCARD, AMEX, DISCOVER, DINERS, JCB");
        System.out.print("Ingrese el tipo de tarjeta: ");
        String tipoStr = scanner.nextLine().trim().toUpperCase();

        TipoTarjeta tipo = TipoTarjeta.fromString(tipoStr);
        if (tipo == null) {
            System.out.println("✗ Tipo de tarjeta no válido");
            return;
        }

        // Cantidad a generar
        System.out.print("Cantidad de tarjetas a generar: ");
        int cantidad;
        try {
            cantidad = Integer.parseInt(scanner.nextLine().trim());
            if (cantidad <= 0) {
                System.out.println("✗ La cantidad debe ser mayor a 0");
                return;
            }
            if (cantidad > 1000) {
                System.out.println("✗ Máximo 1000 tarjetas por generación");
                return;
            }
        } catch (NumberFormatException e) {
            System.out.println("✗ Cantidad no válida");
            return;
        }

        // Generar tarjetas
        System.out.println("\n⏳ Generando " + cantidad + " tarjetas " + tipo.getNombre() + "...");
        List<TarjetaCredito> tarjetas = generador.generarTarjetas(cantidad, tipo);

        // Mostrar resultado
        System.out.println("\n✓ Tarjetas generadas exitosamente!");
        System.out.println("\n" + "=".repeat(60));
        System.out.println("PREVISUALIZACIÓN (primeras 5 tarjetas):");
        System.out.println("Formato: numero|año|mes|ccv");
        System.out.println("-".repeat(60));

        tarjetas.stream().limit(5).forEach(t ->
                System.out.println(t.formatoEspecificado())
        );

        if (tarjetas.size() > 5) {
            System.out.println("... y " + (tarjetas.size() - 5) + " más");
        }

        // Opciones de guardado
        System.out.println("\n╔════════════════════════════════════════════════════════╗");
        System.out.println("║              OPCIONES DE GUARDADO                      ║");
        System.out.println("╠════════════════════════════════════════════════════════╣");
        System.out.println("║  1. Guardar en archivo de texto                        ║");
        System.out.println("║  2. Guardar en base de datos H2                        ║");
        System.out.println("║  3. Ambos                                              ║");
        System.out.println("║  4. No guardar                                         ║");
        System.out.println("╚════════════════════════════════════════════════════════╝");
        System.out.print("Seleccione una opción: ");

        int opcionGuardado = leerOpcion();

        switch (opcionGuardado) {
            case 1 -> {
                String archivo = fileService.guardarEnArchivo(tarjetas);
                System.out.println("✓ Tarjetas guardadas en: " + archivo);
            }
            case 2 -> {
                databaseService.inicializarBaseDatos();
                databaseService.guardarTarjetas(tarjetas);
            }
            case 3 -> {
                String archivo = fileService.guardarEnArchivo(tarjetas);
                System.out.println("✓ Tarjetas guardadas en: " + archivo);
                databaseService.inicializarBaseDatos();
                databaseService.guardarTarjetas(tarjetas);
            }
            case 4 -> System.out.println("ℹ Tarjetas no guardadas");
            default -> System.out.println("✗ Opción no válida, tarjetas no guardadas");
        }
    }
}