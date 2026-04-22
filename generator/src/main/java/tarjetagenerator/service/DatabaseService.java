package tarjetagenerator.service;

import tarjetagenerator.model.TarjetaCredito;
import java.sql.*;
import java.time.LocalDateTime;
import java.util.List;

public class DatabaseService {
    private static final String DB_URL = "jdbc:h2:./tarjetas_db";
    private static final String USER = "sa";
    private static final String PASSWORD = "";

    public void inicializarBaseDatos() {
        try (Connection conn = DriverManager.getConnection(DB_URL, USER, PASSWORD);
             Statement stmt = conn.createStatement()) {

            String sql = """
                CREATE TABLE IF NOT EXISTS tarjetas (
                    id BIGINT AUTO_INCREMENT PRIMARY KEY,
                    numero VARCHAR(20) NOT NULL,
                    año INTEGER NOT NULL,
                    mes INTEGER NOT NULL,
                    ccv VARCHAR(4) NOT NULL,
                    tipo VARCHAR(20) NOT NULL,
                    fecha_generacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """;

            stmt.execute(sql);

        } catch (SQLException e) {
            System.err.println("Error inicializando base de datos: " + e.getMessage());
        }
    }

    public void guardarTarjetas(List<TarjetaCredito> tarjetas) {
        String sql = "INSERT INTO tarjetas (numero, año, mes, ccv, tipo) VALUES (?, ?, ?, ?, ?)";

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

            System.out.println("✓ " + resultados.length + " tarjetas guardadas en la base de datos");

        } catch (SQLException e) {
            System.err.println("Error guardando en base de datos: " + e.getMessage());
        }
    }
}