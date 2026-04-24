package tarjetagenerator.service;

import tarjetagenerator.model.TarjetaCredito;
import java.net.URI;
import java.net.http.*;
import java.util.List;

public class DatabaseService {
    private static final String API_URL = "http://localhost:8080/api/v1/tarjetas";
    private final HttpClient httpClient;

    public DatabaseService() {
        this.httpClient = HttpClient.newHttpClient();
    }

    public void inicializarBaseDatos() {
        // Verificar que la API está disponible
        try {
            HttpRequest request = HttpRequest.newBuilder()
                    .uri(URI.create(API_URL))
                    .GET()
                    .build();

            HttpResponse<String> response = httpClient.send(request,
                    HttpResponse.BodyHandlers.ofString());

            if (response.statusCode() == 200) {
                System.out.println("[+] API connection established");
            } else {
                System.out.println("[!] API responded with status: " + response.statusCode());
            }
        } catch (Exception e) {
            System.err.println("[!] API connection error: " + e.getMessage());
            System.err.println("[!] Make sure the API is running on " + API_URL);
        }
    }

    public void guardarTarjetas(List<TarjetaCredito> tarjetas) {
        int successCount = 0;
        int errorCount = 0;

        for (TarjetaCredito tarjeta : tarjetas) {
            try {
                // Crear JSON manualmente (sin dependencias externas)
                String json = String.format(
                        "{\"numero\":\"%s\",\"mes\":%d,\"anio\":%d,\"ccv\":%s}",
                        tarjeta.getNumero(),
                        tarjeta.getMes(),
                        tarjeta.getAño(),
                        tarjeta.getCvv()
                );

                HttpRequest request = HttpRequest.newBuilder()
                        .uri(URI.create(API_URL))
                        .header("Content-Type", "application/json")
                        .POST(HttpRequest.BodyPublishers.ofString(json))
                        .build();

                HttpResponse<String> response = httpClient.send(request,
                        HttpResponse.BodyHandlers.ofString());

                if (response.statusCode() == 200 || response.statusCode() == 201) {
                    successCount++;
                } else {
                    errorCount++;
                }

            } catch (Exception e) {
                errorCount++;
                System.err.println("[!] Error sending card: " + e.getMessage());
            }
        }

        System.out.println("[+] Cards sent to API: " + successCount + " success, " + errorCount + " errors");
    }
}