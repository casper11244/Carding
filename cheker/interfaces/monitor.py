import time
import threading
from typing import Dict, List
from collections import deque
from datetime import datetime
from colorama import Fore, Style

class Monitor:
    """
    Monitor en tiempo real para el proceso de verificación de tarjetas.
    """

    def __init__(self, config):
        self.config = config
        self.results = deque(maxlen=100)  # Guardar los últimos 100 resultados
        self.stats = {
            "total": 0,
            "success": 0,
            "failed": 0,
            "start_time": time.time()
        }
        self.running = False
        self.thread = None

    def start(self):
        """Inicia el monitor en un hilo separado"""
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._run)
            self.thread.daemon = True
            self.thread.start()

    def stop(self):
        """Detiene el monitor"""
        self.running = False
        if self.thread:
            self.thread.join()

    def add_result(self, result: Dict):
        """Agrega un nuevo resultado al monitor"""
        self.results.append(result)

        # Actualizar estadísticas
        self.stats["total"] += 1
        if result["success"]:
            self.stats["success"] += 1
        else:
            self.stats["failed"] += 1

    def _run(self):
        """Función principal del monitor"""
        while self.running:
            self._display()
            time.sleep(self.config.REFRESH_RATE)

    def _display(self):
        """Muestra el estado actual del monitor"""
        # Limpiar pantalla y mover el cursor a la posición inicial
        print("\033[H\033[J", end="")

        # Título
        print(f"{Fore.CYAN}╔══════════════════════════════════════════════════════════════╗{Style.RESET_ALL}")
        print(f"{Fore.CYAN}║{Fore.YELLOW}                    MONITOR EN TIEMPO REAL                     {Fore.CYAN}║{Style.RESET_ALL}")
        print(f"{Fore.CYAN}╠══════════════════════════════════════════════════════════════╣{Style.RESET_ALL}")

        # Estadísticas
        elapsed_time = time.time() - self.stats["start_time"]
        success_rate = (self.stats["success"] / max(1, self.stats["total"])) * 100

        print(f"{Fore.CYAN}║{Fore.WHITE} Total: {self.stats['total']:<5} {Fore.GREEN}Éxito: {self.stats['success']:<5} {Fore.RED}Fallo: {self.stats['failed']:<5} {Fore.YELLOW}Tasa: {success_rate:.1f}%{Fore.CYAN}  ║{Style.RESET_ALL}")
        print(f"{Fore.CYAN}║{Fore.WHITE} Tiempo transcurrido: {elapsed_time:.2f}s                              {Fore.CYAN}║{Style.RESET_ALL}")
        print(f"{Fore.CYAN}╠══════════════════════════════════════════════════════════════╣{Style.RESET_ALL}")

        # Resultados recientes
        print(f"{Fore.CYAN}║{Fore.YELLOW}                        RESULTADOS RECIENTES                   {Fore.CYAN}║{Style.RESET_ALL}")
        print(f"{Fore.CYAN}╠══════════════════════════════════════════════════════════════╣{Style.RESET_ALL}")

        # Mostrar hasta 10 resultados recientes
        recent_results = list(self.results)[-10:]

        for result in recent_results:
            card = result["card"]
            masked_number = f"{card['number'][:6]}{'*' * (len(card['number']) - 10)}{card['number'][-4:]}"

            if result["success"]:
                status = f"{Fore.GREEN}✓{Style.RESET_ALL}"
            else:
                status = f"{Fore.RED}✗{Style.RESET_ALL}"

            print(f"{Fore.CYAN}║{Style.RESET_ALL} {status} {masked_number} | {result['gate']} | {result['response_time']:.2f}s {Fore.CYAN}║{Style.RESET_ALL}")

        # Rellenar espacio restante si hay menos de 10 resultados
        for _ in range(10 - len(recent_results)):
            print(f"{Fore.CYAN}║                                                              ║{Style.RESET_ALL}")

        print(f"{Fore.CYAN}╚══════════════════════════════════════════════════════════════╝{Style.RESET_ALL}")