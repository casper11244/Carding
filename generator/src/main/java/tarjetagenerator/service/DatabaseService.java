package tarjetagenerator.service;

import tarjetagenerator.model.TarjetaCredito;
import java.sql.*;
import java.util.List;

public class DatabaseService {
    private static final String DB_URL = "jdbc:h2:./cards_db";
    private static final String USER = "sa";
    private static final String PASSWORD = "";

    public void inicializarBaseDatos() {
        try (Connection conn = DriverManager.getConnection(DB_URL, USER, PASSWORD);
             Statement stmt = conn.createStatement()) {

            String sql = """
                CREATE TABLE IF NOT EXISTS cards (
                    id BIGINT AUTO_INCREMENT PRIMARY KEY,
                    number VARCHAR(20) NOT NULL,
                    year INTEGER NOT NULL,
                    month INTEGER NOT NULL,
                    cvv VARCHAR(4) NOT NULL,
                    type VARCHAR(20) NOT NULL,
                    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """;

            stmt.execute(sql);
            System.out.println("[+] Database initialized");

        } catch (SQLException e) {
            System.err.println("[!] Database init error: " + e.getMessage());
        }
    }

    public void guardarTarjetas(List<TarjetaCredito> tarjetas) {
        String sql = "INSERT INTO cards (number, year, month, cvv, type) VALUES (?, ?, ?, ?, ?)";

        try (Connection conn = DriverManager.getConnection(DB_URL, USER, PASSWORD);
             PreparedStatement pstmt = conn.prepareStatement(sql)) {

            conn.setAutoCommit(false);

            for (TarjetaCredito tarjeta : tarjetas) {
                pstmt.setString(1, tarjeta.getNumero());
                pstmt.setInt(2, tarjeta.getAño());
                pstmt.setInt(3, tarjeta.getMes());
                pstmt.setString(4, tarjeta.getCvv());
                pstmt.setString(5, tarjeta.getTipo().getNombre());
                pstmt.addBatch();
            }

            int[] resultados = pstmt.executeBatch();
            conn.commit();

            System.out.println("[+] " + resultados.length + " cards saved to database");

        } catch (SQLException e) {
            System.err.println("[!] Database save error: " + e.getMessage());
        }
    }
}