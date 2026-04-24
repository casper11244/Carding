import os
from typing import List, Dict
from utils.logger import Logger

class FileHandler:
    """
    Manejo de archivos para el sistema de verificación de tarjetas.
    """

    def __init__(self):
        self.logger = Logger("FileHandler")

    def read_cards_from_file(self, file_path: str) -> List[Dict]:
        """
        Lee tarjetas desde un archivo de texto.
        Formato esperado: numero|mes|año|cvv
        """
        cards = []

        try:
            # Verificar si el archivo existe
            if not os.path.exists(file_path):
                self.logger.error(f"El archivo no existe: {file_path}")
                return []

            with open(file_path, 'r') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()

                    # Omitir líneas vacías
                    if not line:
                        continue

                    # Procesar línea
                    parts = line.split('|')

                    if len(parts) != 4:
                        self.logger.warning(f"Línea {line_num} con formato inválido: {line}")
                        continue

                    number, month, year, cvv = parts

                    # Validar datos
                    if not (number.isdigit() and month.isdigit() and year.isdigit() and cvv.isdigit()):
                        self.logger.warning(f"Línea {line_num} con datos inválidos: {line}")
                        continue

                    # Formatear año si es necesario
                    if len(year) == 2:
                        year = f"20{year}"

                    # Formatear mes y cvv si es necesario
                    month = f"{int(month):02d}"
                    cvv = f"{int(cvv):03d}" if len(cvv) == 3 else f"{int(cvv):04d}"

                    cards.append({
                        "number": number,
                        "month": month,
                        "year": year,
                        "cvv": cvv
                    })

            self.logger.info(f"Leídas {len(cards)} tarjetas desde {file_path}")
            return cards

        except Exception as e:
            self.logger.error(f"Error al leer archivo {file_path}: {str(e)}")
            return []

    def save_results_to_file(self, results: List[Dict], file_path: str):
        """
        Guarda los resultados en un archivo de texto.
        """
        try:
            with open(file_path, 'w') as f:
                for result in results:
                    card = result["card"]
                    status = "SUCCESS" if result["success"] else "FAILED"

                    line = f"{card['number']}|{card['month']}|{card['year']}|{card['cvv']}|{status}|{result['message']}|{result['response_time']}\n"
                    f.write(line)

            self.logger.info(f"Resultados guardados en {file_path}")
            return True

        except Exception as e:
            self.logger.error(f"Error al guardar resultados en {file_path}: {str(e)}")
            return False