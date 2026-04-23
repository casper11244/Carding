package tarjetagenerator.service;

public class AlgoritmoLuhn {

    public static boolean validar(String numero) {
        int suma = 0;
        boolean alternar = false;

        for (int i = numero.length() - 1; i >= 0; i--) {
            int n = Integer.parseInt(numero.substring(i, i + 1));
            if (alternar) {
                n *= 2;
                if (n > 9) {
                    n = (n % 10) + 1;
                }
            }
            suma += n;
            alternar = !alternar;
        }

        return (suma % 10 == 0);
    }

    public static String generarDigitoVerificador(String prefijo) {
        for (int i = 0; i <= 9; i++) {
            String numero = prefijo + i;
            if (validar(numero)) {
                return String.valueOf(i);
            }
        }
        return "0";
    }
}