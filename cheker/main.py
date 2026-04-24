import sys
import config.settings          # Ahora tenemos el módulo completo
from interfaces.console_ui import ConsoleUI
from utils.logger import Logger

def main():
    logger = Logger("Main")
    try:
        ui = ConsoleUI(config.settings)   # Pasamos el módulo como objeto config
        ui.run()
    except KeyboardInterrupt:
        logger.info("Programa interrumpido por el usuario")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Error no controlado: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()