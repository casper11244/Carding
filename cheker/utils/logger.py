import logging
import os
from datetime import datetime
from colorama import Fore, Style, init

init(autoreset=True)

class Logger:
    """
    Sistema de logging personalizado con colores y niveles.
    """

    def __init__(self, name: str, log_file: str = None):
        self.name = name
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)

        # Evitar duplicar handlers
        if not self.logger.handlers:
            # Crear directorio de logs si no existe
            log_dir = "logs"
            if not os.path.exists(log_dir):
                os.makedirs(log_dir)

            # Nombre del archivo de log
            if log_file is None:
                log_file = f"{log_dir}/{name}_{datetime.now().strftime('%Y%m%d')}.log"

            # Configurar handler para archivo (sin colores)
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(logging.INFO)
            file_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            file_handler.setFormatter(file_formatter)

            # Configurar handler para consola (sin formato para evitar duplicar colores)
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            console_formatter = logging.Formatter('%(message)s')
            console_handler.setFormatter(console_formatter)

            # Agregar handlers
            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)

    def debug(self, message: str):
        """Registra un mensaje de depuración"""
        self.logger.debug(f"{Fore.MAGENTA}→ {message}{Style.RESET_ALL}")

    def info(self, message: str):
        """Registra un mensaje informativo"""
        self.logger.info(f"{Fore.CYAN}ℹ {message}{Style.RESET_ALL}")

    def warning(self, message: str):
        """Registra una advertencia"""
        self.logger.warning(f"{Fore.YELLOW}⚠ {message}{Style.RESET_ALL}")

    def error(self, message: str):
        """Registra un error"""
        self.logger.error(f"{Fore.RED}✖ ERROR: {message}{Style.RESET_ALL}")

    def success(self, message: str):
        """Registra un mensaje de éxito"""
        self.logger.info(f"{Fore.GREEN}✓ {message}{Style.RESET_ALL}")