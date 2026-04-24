import requests
import json
from typing import Dict, Optional, List
from utils.logger import Logger

class APIClient:
    """
    Cliente para interactuar con la API de tarjetas.
    """

    def __init__(self, config):
        self.config = config
        self.logger = Logger("APIClient")
        self.base_url = config.API_BASE_URL
        self.session = requests.Session()

    def get_card_by_id(self, card_id: int) -> Optional[Dict]:
        """
        Obtiene una tarjeta por su ID desde la API.
        """
        try:
            url = f"{self.base_url}/{card_id}"
            response = self.session.get(url, timeout=10)

            if response.status_code == 200:
                card_data = response.json()

                # Formatear datos de la tarjeta
                formatted_card = {
                    "number": card_data.get("numero", ""),
                    "month": f"{card_data.get('mes', 0):02d}",
                    "year": str(card_data.get("anio", 0)),
                    "cvv": f"{card_data.get('ccv', 0):03d}"
                }

                self.logger.info(f"Tarjeta obtenida desde API: {formatted_card['number'][:6]}****")
                return formatted_card
            else:
                self.logger.error(f"Error al obtener tarjeta {card_id}: {response.status_code}")
                return None

        except Exception as e:
            self.logger.error(f"Excepción al obtener tarjeta {card_id}: {str(e)}")
            return None

    def get_all_cards(self) -> List[Dict]:
        """
        Obtiene todas las tarjetas desde la API.
        """
        try:
            url = f"{self.base_url}"
            response = self.session.get(url, timeout=15)

            if response.status_code == 200:
                cards_data = response.json()

                # Formatear todas las tarjetas
                formatted_cards = []
                for card in cards_data:
                    formatted_card = {
                        "number": card.get("numero", ""),
                        "month": f"{card.get('mes', 0):02d}",
                        "year": str(card.get("anio", 0)),
                        "cvv": f"{card.get('ccv', 0):03d}"
                    }
                    formatted_cards.append(formatted_card)

                self.logger.info(f"Obtenidas {len(formatted_cards)} tarjetas desde API")
                return formatted_cards
            else:
                self.logger.error(f"Error al obtener tarjetas: {response.status_code}")
                return []

        except Exception as e:
            self.logger.error(f"Excepción al obtener tarjetas: {str(e)}")
            return []

    def get_random_cards(self, count: int = 10) -> List[Dict]:
        """
        Obtiene un número aleatorio de tarjetas desde la API.
        """
        all_cards = self.get_all_cards()

        if len(all_cards) <= count:
            return all_cards

        import random
        return random.sample(all_cards, count)