package tarjetagenerator.model;

public enum TipoTarjeta {
    VISA("4", "VISA", 16),
    MASTERCARD("5", "MASTERCARD", 16),
    AMEX("34", "AMERICAN EXPRESS", 15),
    DISCOVER("6011", "DISCOVER", 16),
    DINERS("300", "DINERS CLUB", 14),
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

    public static TipoTarjeta fromOpcion(int opcion) {
        return switch(opcion) {
            case 1 -> VISA;
            case 2 -> MASTERCARD;
            case 3 -> AMEX;
            case 4 -> DISCOVER;
            case 5 -> DINERS;
            case 6 -> JCB;
            default -> null;
        };
    }

    public static void mostrarOpciones() {
        TipoTarjeta[] tipos = values();
        for (int i = 0; i < tipos.length; i++) {
            System.out.printf("  [%d] %s%n", i + 1, tipos[i].getNombre());
        }
    }
}