package tarjetagenerator.model;

public enum TipoTarjeta {
    VISA("4", "Visa", 16),
    MASTERCARD("5", "MasterCard", 16),
    AMEX("34", "American Express", 15),
    DISCOVER("6011", "Discover", 16),
    DINERS("300", "Diners Club", 14),
    JCB("35", "JCB", 16);

    private final String prefijo;
    private final String nombre;
    private final int longitud;

    TipoTarjeta(String prefijo, String nombre, int longitud) {
        this.prefijo = prefijo;
        this.nombre = nombre;
        this.longitud = longitud;
    }

    public String getPrefijo() { return prefijo; }
    public String getNombre() { return nombre; }
    public int getLongitud() { return longitud; }

    public static TipoTarjeta fromString(String tipo) {
        try {
            return valueOf(tipo.toUpperCase());
        } catch (IllegalArgumentException e) {
            return null;
        }
    }
}