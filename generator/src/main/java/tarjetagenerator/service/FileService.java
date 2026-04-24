package tarjetagenerator.service;

import tarjetagenerator.model.TarjetaCredito;
import java.io.*;
import java.nio.file.*;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.List;

public class FileService {
    private static final String OUTPUT_DIR = System.getProperty("user.home") + "/Carding/Trajets";

    static {
        try {
            Files.createDirectories(Paths.get(OUTPUT_DIR));
        } catch (IOException e) {
            System.err.println("[!] Error creating output directory: " + e.getMessage());
        }
    }

    public String guardarEnArchivo(List<TarjetaCredito> tarjetas) {
        String timestamp = LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyyMMdd_HHmmss"));
        String filename = OUTPUT_DIR + "/cards_" + timestamp + ".txt";

        try (PrintWriter writer = new PrintWriter(new FileWriter(filename))) {
            // Solo los datos, sin encabezados ni decoración
            for (TarjetaCredito tarjeta : tarjetas) {
                writer.println(tarjeta.formatoEspecificado());
            }

        } catch (IOException e) {
            System.err.println("[!] Error saving file: " + e.getMessage());
            return null;
        }

        return filename;
    }
}