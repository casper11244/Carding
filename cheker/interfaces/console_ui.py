import os
import sys
import time
import threading
from typing import Dict, List, Optional
from tabulate import tabulate
from colorama import init, Fore, Back, Style
from core.checker import CardChecker
from interfaces.monitor import Monitor
from utils.logger import Logger
from config.settings import DEFAULT_CARD_PATH

# Inicializar colorama
init()

class ConsoleUI:
    """
    Interfaz de consola con estilo hacker para el sistema de verificación de tarjetas.
    """

    def __init__(self, config):
        self.config = config
        self.logger = Logger("ConsoleUI")
        self.checker = CardChecker(config)
        self.monitor = Monitor(config)
        self.checker.set_monitor(self.monitor)
        self.running = False

    def clear_screen(self):
        """Limpia la pantalla de la consola"""
        os.system('cls' if os.name == 'nt' else 'clear')

    def print_banner(self):
        """Imprime el banner de la aplicación"""
        banner = f"""
{Fore.CYAN}╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║  {Fore.GREEN}██╗    ██╗██╗  ██╗ █████╗ ████████╗██╗ ██████╗██╗  ██╗███████╗██████╗ {Fore.CYAN}║
║  {Fore.GREEN}██║    ██║██║  ██║██╔══██╗╚══██╔══╝██║██╔════╝██║ ██╔╝██╔════╝██╔══██╗{Fore.CYAN}║
║  {Fore.GREEN}██║ █╗ ██║███████║███████║   ██║   ██║██║     █████╔╝ █████╗  ██████╔╝{Fore.CYAN}║
║  {Fore.GREEN}██║███╗██║██╔══██║██╔══██║   ██║   ██║██║     ██╔═██╗ ██╔══╝  ██╔══██╗{Fore.CYAN}║
║  {Fore.GREEN}╚███╔███╔╝██║  ██║██║  ██║   ██║   ██║╚██████╗██║  ██╗███████╗██║  ██║{Fore.CYAN}║
║   {Fore.GREEN}╚══╝╚══╝ ╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝   ╚═╝ ╚═════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝{Fore.CYAN}║
║                                                              ║
║  {Fore.YELLOW}Sistema Avanzado de Verificación de Tarjetas v1.0{Fore.CYAN}            ║
║  {Fore.MAGENTA}Desarrollado con algoritmos de optimización avanzados{Fore.CYAN}          ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝{Style.RESET_ALL}
"""
        print(banner)

    def print_menu(self):
        """Imprime el menú principal"""
        menu = f"""
{Fore.CYAN}┌─────────────────────────────────────────────────────────────────┐
│{Fore.YELLOW}                         MENÚ PRINCIPAL                          {Fore.CYAN}│
├─────────────────────────────────────────────────────────────────┤
│{Fore.WHITE}  1. Verificar tarjetas desde archivo .txt                          {Fore.CYAN}│
│{Fore.WHITE}  2. Verificar tarjetas desde base de datos (API)                   {Fore.CYAN}│
│{Fore.WHITE}  3. Ingresar tarjeta manualmente                                   {Fore.CYAN}│
│{Fore.WHITE}  4. Probar y actualizar proxies                                    {Fore.CYAN}│
│{Fore.WHITE}  5. Ver estadísticas de verificaciones                            {Fore.CYAN}│
│{Fore.WHITE}  6. Salir                                                         {Fore.CYAN}│
├─────────────────────────────────────────────────────────────────┤
│{Fore.GREEN}Proxies disponibles: {self.checker.proxy_manager.get_proxy_count():<20}                     {Fore.CYAN}│
└─────────────────────────────────────────────────────────────────┘{Style.RESET_ALL}
"""
        print(menu)

    def get_user_choice(self) -> int:
        """Obtiene la elección del usuario"""
        while True:
            try:
                choice = input(f"{Fore.CYAN}Seleccione una opción [1-6]: {Style.RESET_ALL}")
                choice = int(choice)

                if 1 <= choice <= 6:
                    return choice
                else:
                    print(f"{Fore.RED}Opción inválida. Por favor, seleccione una opción del 1 al 6.{Style.RESET_ALL}")

            except ValueError:
                print(f"{Fore.RED}Entrada inválida. Por favor, ingrese un número.{Style.RESET_ALL}")

    def get_file_path(self) -> str:
        """Obtiene la ruta del archivo de tarjetas"""
        default_path = DEFAULT_CARD_PATH

        print(f"\n{Fore.YELLOW}Ruta predeterminada: {default_path}{Style.RESET_ALL}")
        use_default = input(f"{Fore.CYAN}¿Usar ruta predeterminada? (s/n): {Style.RESET_ALL}").lower()

        if use_default == 's':
            return default_path
        else:
            file_path = input(f"{Fore.CYAN}Ingrese la ruta del archivo: {Style.RESET_ALL}")
            return file_path

    def get_card_data(self) -> Dict:
        """Obiene datos de una tarjeta manualmente"""
        print(f"\n{Fore.YELLOW}Ingrese los datos de la tarjeta:{Style.RESET_ALL}")

        while True:
            card_number = input(f"{Fore.CYAN}Número de tarjeta: {Style.RESET_ALL}")

            # Validar longitud
            if len(card_number) < 13 or len(card_number) > 19:
                print(f"{Fore.RED}El número de tarjeta debe tener entre 13 y 19 dígitos.{Style.RESET_ALL}")
                continue

            # Validar que sean solo dígitos
            if not card_number.isdigit():
                print(f"{Fore.RED}El número de tarjeta solo debe contener dígitos.{Style.RESET_ALL}")
                continue

            break

        while True:
            try:
                month = input(f"{Fore.CYAN}Mes de vencimiento (MM): {Style.RESET_ALL}")
                month = int(month)

                if month < 1 or month > 12:
                    print(f"{Fore.RED}El mes debe estar entre 01 y 12.{Style.RESET_ALL}")
                    continue

                month = f"{month:02d}"
                break

            except ValueError:
                print(f"{Fore.RED}Entrada inválida. Por favor, ingrese un número.{Style.RESET_ALL}")

        while True:
            try:
                year = input(f"{Fore.CYAN}Año de vencimiento (AA): {Style.RESET_ALL}")
                year = int(year)

                if year < 22 or year > 35:
                    print(f"{Fore.RED}El año debe estar entre 22 y 35.{Style.RESET_ALL}")
                    continue

                year = f"20{year}"
                break

            except ValueError:
                print(f"{Fore.RED}Entrada inválida. Por favor, ingrese un número.{Style.RESET_ALL}")

        while True:
            cvv = input(f"{Fore.CYAN}CVV: {Style.RESET_ALL}")

            # Validar longitud
            if len(cvv) < 3 or len(cvv) > 4:
                print(f"{Fore.RED}El CVV debe tener 3 o 4 dígitos.{Style.RESET_ALL}")
                continue

            # Validar que sean solo dígitos
            if not cvv.isdigit():
                print(f"{Fore.RED}El CVV solo debe contener dígitos.{Style.RESET_ALL}")
                continue

            break

        return {
            "number": card_number,
            "month": month,
            "year": year,
            "cvv": cvv
        }

    def show_loading(self, message: str):
        """Muestra una animación de carga"""
        animation = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]

        for _ in range(20):
            for frame in animation:
                sys.stdout.write(f"\r{Fore.CYAN}{message} {frame}{Style.RESET_ALL}")
                time.sleep(0.1)
                sys.stdout.flush()

        sys.stdout.write(f"\r{Fore.GREEN}{message} ✓{Style.RESET_ALL}\n")

    def show_results(self, results: List[Dict]):
        """Muestra los resultados de la verificación"""
        if not results:
            print(f"\n{Fore.YELLOW}No hay resultados para mostrar.{Style.RESET_ALL}")
            return

        # Preparar datos para la tabla
        table_data = []
        for result in results:
            card = result["card"]
            status = f"{Fore.GREEN}✓ ÉXITO{Style.RESET_ALL}" if result["success"] else f"{Fore.RED}✗ FALLO{Style.RESET_ALL}"

            # Ocultar todos los dígitos excepto los primeros 6 y últimos 4
            masked_number = f"{card['number'][:6]}{'*' * (len(card['number']) - 10)}{card['number'][-4:]}"

            table_data.append([
                masked_number,
                f"{card['month']}/{card['year']}",
                result["gate"],
                status,
                f"{result['response_time']:.2f}s",
                result.get("message", "")
            ])

        # Imprimir tabla
        headers = ["Tarjeta", "Vencimiento", "Gate", "Estado", "Tiempo", "Mensaje"]
        print(f"\n{Fore.CYAN}Resultados de la verificación:{Style.RESET_ALL}")
        print(tabulate(table_data, headers=headers, tablefmt="grid"))

        # Estadísticas
        total = len(results)
        success = sum(1 for r in results if r["success"])
        failed = total - success
        success_rate = (success / total) * 100 if total > 0 else 0

        print(f"\n{Fore.YELLOW}Estadísticas:{Style.RESET_ALL}")
        print(f"{Fore.WHITE}Total: {total} | Éxito: {success} | Fallo: {failed} | Tasa de éxito: {success_rate:.2f}%{Style.RESET_ALL}")

    def show_stats(self):
        """Muestra estadísticas de verificaciones"""
        stats = self.checker.get_stats()

        print(f"\n{Fore.CYAN}Estadísticas de verificaciones:{Style.RESET_ALL}")
        print(f"{Fore.WHITE}Total de verificaciones: {stats['total']}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}Verificaciones exitosas: {stats['success']}{Style.RESET_ALL}")
        print(f"{Fore.RED}Verificaciones fallidas: {stats['failed']}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Tasa de éxito: {stats['success_rate']:.2f}%{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Tiempo de respuesta promedio: {stats['avg_response_time']:.2f}s{Style.RESET_ALL}")

    def test_proxies(self):
        """Prueba y actualiza los proxies"""
        print(f"\n{Fore.YELLOW}Probando y actualizando proxies...{Style.RESET_ALL}")

        def update_thread():
            success = self.checker.proxy_manager.update_proxy_list(force_update=True)

            if success:
                print(f"\n{Fore.GREEN}Proxies actualizados correctamente.{Style.RESET_ALL}")
                print(f"{Fore.WHITE}Proxies funcionales: {self.checker.proxy_manager.get_proxy_count()}{Style.RESET_ALL}")
            else:
                print(f"\n{Fore.RED}Error al actualizar proxies.{Style.RESET_ALL}")

        # Ejecutar en un hilo separado para no bloquear la UI
        thread = threading.Thread(target=update_thread)
        thread.start()

        # Mostrar animación de carga
        self.show_loading("Actualizando proxies")
        thread.join()

    def run(self):
        """Ejecuta la interfaz de consola"""
        # Inicializar el sistema
        if not self.checker.initialize():
            print(f"{Fore.RED}Error al inicializar el sistema. Saliendo...{Style.RESET_ALL}")
            return

        self.running = True

        while self.running:
            self.clear_screen()
            self.print_banner()
            self.print_menu()

            choice = self.get_user_choice()

            if choice == 1:
                # Verificar desde archivo
                file_path = self.get_file_path()

                print(f"\n{Fore.YELLOW}Verificando tarjetas desde archivo...{Style.RESET_ALL}")
                self.show_loading("Procesando archivo")

                results = self.checker.check_cards_from_file(file_path)
                self.show_results(results)

                input(f"\n{Fore.CYAN}Presione Enter para continuar...{Style.RESET_ALL}")

            elif choice == 2:
                # Verificar desde API
                print(f"\n{Fore.YELLOW}Obteniendo tarjetas desde la API...{Style.RESET_ALL}")
                self.show_loading("Conectando con la API")

                results = self.checker.check_cards_from_api()
                self.show_results(results)

                input(f"\n{Fore.CYAN}Presione Enter para continuar...{Style.RESET_ALL}")

            elif choice == 3:
                # Ingresar tarjeta manualmente
                card_data = self.get_card_data()

                print(f"\n{Fore.YELLOW}Verificando tarjeta...{Style.RESET_ALL}")
                self.show_loading("Verificando tarjeta")

                result = self.checker.check_single_card(card_data)
                self.show_results([result])

                input(f"\n{Fore.CYAN}Presione Enter para continuar...{Style.RESET_ALL}")

            elif choice == 4:
                # Probar proxies
                self.test_proxies()
                input(f"\n{Fore.CYAN}Presione Enter para continuar...{Style.RESET_ALL}")

            elif choice == 5:
                # Ver estadísticas
                self.show_stats()
                input(f"\n{Fore.CYAN}Presione Enter para continuar...{Style.RESET_ALL}")

            elif choice == 6:
                # Salir
                print(f"\n{Fore.YELLOW}Guardando resultados...{Style.RESET_ALL}")
                self.checker.save_results()

                print(f"{Fore.GREEN}¡Gracias por usar el sistema de verificación de tarjetas!{Style.RESET_ALL}")
                self.running = False