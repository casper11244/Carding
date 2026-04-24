from typing import Dict
from utils.logger import Logger

class CardValidator:
    """
    Validador de datos de tarjetas.
    """

    def __init__(self):
        self.logger = Logger("CardValidator")

    def validate(self, card_data: Dict) -> bool:
        """
        Valida los datos de una tarjeta.
        """
        try:
            # Verificar que todos los campos existan
            required_fields = ["number", "month", "year", "cvv"]
            for field in required_fields:
                if field not in card_data:
                    self.logger.warning(f"Campo faltante: {field}")
                    return False

            # Validar número de tarjeta
            number = card_data["number"]
            if len(number) < 13 or len(number) > 19 or not number.isdigit():
                self.logger.warning("Número de tarjeta inválido")
                return False

            # Validar mes
            month = card_data["month"]
            month_int = int(month)
            if month_int < 1 or month_int > 12:
                self.logger.warning("Mes de vencimiento inválido")
                return False

            # Validar año
            year = card_data["year"]
            if len(year) != 4 or not year.isdigit():
                self.logger.warning("Año de vencimiento inválido")
                return False

            # Validar CVV
            cvv = card_data["cvv"]
            if len(cvv) < 3 or len(cvv) > 4 or not cvv.isdigit():
                self.logger.warning("CVV inválido")
                return False

            return True

        except Exception as e:
            self.logger.error(f"Error al validar tarjeta: {str(e)}")
            return False