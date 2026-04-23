package tarjetagenerator.model;

public class TarjetaCredito {
    private final String numero;
    private final int año;
    private final int mes;
    private final String cvv;
    private final TipoTarjeta tipo;

    public TarjetaCredito(String numero, int año, int mes, String cvv, TipoTarjeta tipo) {
        this.numero = numero;
        this.año = año;
        this.mes = mes;
        this.cvv = cvv;
        this.tipo = tipo;
    }

    public String getNumero() { return numero; }
    public int getAño() { return año; }
    public int getMes() { return mes; }
    public String getCvv() { return cvv; }
    public TipoTarjeta getTipo() { return tipo; }

    public String formatoEspecificado() {
        return String.format("%s|%d|%02d|%s", numero, año, mes, cvv);
    }
}