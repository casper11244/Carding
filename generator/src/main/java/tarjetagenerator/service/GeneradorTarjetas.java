package tarjetagenerator.service;

import tarjetagenerator.model.*;
import java.security.SecureRandom;
import java.time.LocalDate;
import java.util.*;

public class GeneradorTarjetas {
    private final SecureRandom random = new SecureRandom();

    public List<TarjetaCredito> generarTarjetas(int cantidad, TipoTarjeta tipo) {
        List<TarjetaCredito> tarjetas = new ArrayList<>();

        for (int i = 0; i < cantidad; i++) {
            String numero = generarNumeroTarjeta(tipo);
            int año = generarAñoExpiracion();
            int mes = generarMesExpiracion();
            String cvv = generarCVV(tipo);

            tarjetas.add(new TarjetaCredito(numero, año, mes, cvv, tipo));
        }

        return tarjetas;
    }

    private String generarNumeroTarjeta(TipoTarjeta tipo) {
        String prefijo = tipo.getPrefijo();
        int longitudRestante = tipo.getLongitud() - prefijo.length() - 1;

        StringBuilder sb = new StringBuilder(prefijo);
        for (int i = 0; i < longitudRestante; i++) {
            sb.append(random.nextInt(10));
        }

        String digitoVerificador = AlgoritmoLuhn.generarDigitoVerificador(sb.toString());
        sb.append(digitoVerificador);

        return sb.toString();
    }

    private int generarAñoExpiracion() {
        int añoActual = LocalDate.now().getYear();
        return añoActual + random.nextInt(5) + 2; // 2-6 años de validez
    }

    private int generarMesExpiracion() {
        return random.nextInt(12) + 1;
    }

    private String generarCVV(TipoTarjeta tipo) {
        int longitud = (tipo == TipoTarjeta.AMEX) ? 4 : 3;
        StringBuilder cvv = new StringBuilder();
        for (int i = 0; i < longitud; i++) {
            cvv.append(random.nextInt(10));
        }
        return cvv.toString();
    }
}