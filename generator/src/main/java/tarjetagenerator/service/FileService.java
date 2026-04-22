package tarjetagenerator.service;

import tarjetagenerator.model.TarjetaCredito;
import java.io.*;
import java.nio.file.*;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.List;

public class FileService {
    private static final String OUTPUT_DIR = "output";

    static {
        try {
            Files.createDirectories(Paths.get(OUTPUT_DIR));
        } catch (IOException e) {
            System.err.println("Error creando directorio output: " + e.getMessage());
        }
    }

    public String guardarEnArchivo(List<TarjetaCredito> tarjetas) {
        String timestamp = LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyyMMdd_HHmmss"));
        String filename = OUTPUT_DIR + "/tarjetas_" + timestamp + ".txt";

        try (PrintWriter writer = new PrintWriter(new FileWriter(filename))) {
            writer.println("=== TARJETAS GENERADAS - " + LocalDateTime.now().format(DateTimeFormatter.ofPattern("dd/MM/yyyy HH:mm:ss")) + " ===");
            writer.println("Formato: numero|año|mes|ccv");
            writer.println("=".repeat(60));

            for (TarjetaCredito tarjeta : tarjetas) {
                writer.println(tarjeta.formatoEspecificado());
            }

            writer.println("=".repeat(60));
            writer.println("Total de tarjetas generadas: " + tarjetas.size());

        } catch (IOException e) {
            System.err.println("Error guardando archivo: " + e.getMessage());
            return null;
        }

        return filename;
    }
}