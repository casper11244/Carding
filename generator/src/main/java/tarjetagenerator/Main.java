package tarjetagenerator;

import tarjetagenerator.ui.MenuConsola;

public class Main {
    public static void main(String[] args) {
        System.out.print("\033[H\033[2J");
        System.out.flush();

        MenuConsola menu = new MenuConsola();
        menu.iniciar();
    }
}