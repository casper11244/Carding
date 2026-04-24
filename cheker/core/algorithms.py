import random
import hashlib
import time
import math
from typing import Dict, List, Tuple, Optional

class AdvancedAlgorithms:
    """
    Algoritmos avanzados para la verificación de tarjetas y gestión de proxies.
    Implementa técnicas sofisticadas para optimizar el proceso de verificación.
    """

    def __init__(self):
        self.proxy_performance = {}  # Registro de rendimiento de proxies
        self.card_patterns = {}      # Patrones de BIN detectados
        self.gate_responses = {}     # Patrones de respuesta de gates

    def luhn_algorithm(self, card_number: str) -> bool:
        """
        Algoritmo de Luhn mejorado para validación de tarjetas.
        Incluye optimizaciones para procesamiento rápido.
        """
        if not card_number.isdigit():
            return False

        total = 0
        reverse_digits = card_number[::-1]

        for i, digit in enumerate(reverse_digits):
            n = int(digit)
            if i % 2 == 1:
                n *= 2
                if n > 9:
                    n -= 9
            total += n

        return total % 10 == 0

    def generate_fingerprint(self, card_data: Dict) -> str:
        """
        Genera una huella digital única para cada tarjeta basada en múltiples factores.
        """
        card_str = f"{card_data['number']}{card_data['month']}{card_data['year']}{card_data['cvv']}"
        return hashlib.sha256(card_str.encode()).hexdigest()

    def calculate_bin_score(self, card_number: str) -> float:
        """
        Calcula una puntuación para el BIN basada en patrones históricos.
        """
        bin_number = card_number[:6]

        if bin_number in self.card_patterns:
            return self.card_patterns[bin_number]

        # Calcular puntuación inicial basada en heurísticas
        score = 0.5  # Base score

        # Ajustar según el emisor (primer dígito)
        first_digit = int(card_number[0])
        if first_digit == 4:  # Visa
            score += 0.1
        elif first_digit == 5:  # Mastercard
            score += 0.15
        elif first_digit == 3:  # American Express
            score += 0.05

        # Ajustar según el rango del BIN
        bin_int = int(bin_number)
        if 400000 <= bin_int <= 499999:  # Rango Visa
            score += 0.05
        elif 510000 <= bin_int <= 559999:  # Rango Mastercard
            score += 0.1

        self.card_patterns[bin_number] = score
        return score

    def optimize_proxy_rotation(self, available_proxies: List[str]) -> List[str]:
        """
        Optimiza el orden de rotación de proxies basándose en su rendimiento histórico.
        """
        if not self.proxy_performance:
            # Si no hay datos históricos, usar un orden aleatorio
            return random.sample(available_proxies, len(available_proxies))

        # Ordenar proxies por rendimiento
        sorted_proxies = sorted(
            available_proxies,
            key=lambda p: self.proxy_performance.get(p, {"score": 0})["score"],
            reverse=True
        )

        return sorted_proxies

    def update_proxy_performance(self, proxy: str, success: bool, response_time: float):
        """
        Actualiza el registro de rendimiento de un proxy.
        """
        if proxy not in self.proxy_performance:
            self.proxy_performance[proxy] = {
                "score": 0.5,
                "success_count": 0,
                "failure_count": 0,
                "avg_response_time": response_time,
                "last_used": time.time()
            }

        perf = self.proxy_performance[proxy]

        if success:
            perf["success_count"] += 1
            # Incrementar puntuación basada en tiempo de respuesta
            time_factor = max(0.1, 1.0 - (response_time / 10.0))
            perf["score"] = min(1.0, perf["score"] + (0.1 * time_factor))
        else:
            perf["failure_count"] += 1
            perf["score"] = max(0.1, perf["score"] - 0.2)

        # Actualizar tiempo de respuesta promedio
        total_requests = perf["success_count"] + perf["failure_count"]
        perf["avg_response_time"] = (
                (perf["avg_response_time"] * (total_requests - 1) + response_time) /
                total_requests
        )

        perf["last_used"] = time.time()

    def adaptive_timeout(self, proxy: str, base_timeout: int) -> int:
        """
        Calcula un timeout adaptativo basado en el rendimiento histórico del proxy.
        """
        if proxy not in self.proxy_performance:
            return base_timeout

        perf = self.proxy_performance[proxy]

        # Ajustar timeout según el tiempo de respuesta promedio
        adaptive_timeout = max(5, min(30, int(perf["avg_response_time"] * 2)))

        # Ajustar según la tasa de éxito
        success_rate = perf["success_count"] / max(1, perf["success_count"] + perf["failure_count"])
        if success_rate < 0.5:
            adaptive_timeout = int(adaptive_timeout * 0.8)

        return adaptive_timeout

    def calculate_check_probability(self, card_data: Dict) -> float:
        """
        Calcula la probabilidad de éxito de una verificación basada en múltiples factores.
        """
        # Validar con algoritmo de Luhn
        if not self.luhn_algorithm(card_data["number"]):
            return 0.0

        # Calcular puntuación del BIN
        bin_score = self.calculate_bin_score(card_data["number"])

        # Calcular puntuación basada en la fecha de vencimiento
        current_year = time.localtime().tm_year
        current_month = time.localtime().tm_mon

        exp_year = int(card_data["year"])
        exp_month = int(card_data["month"])

        if exp_year < current_year or (exp_year == current_year and exp_month < current_month):
            return 0.0  # Tarjeta expirada

        # Calcular factor de tiempo hasta expiración
        months_to_expire = (exp_year - current_year) * 12 + (exp_month - current_month)
        time_factor = min(1.0, months_to_expire / 36)  # Normalizar a 3 años

        # Combinar factores
        probability = bin_score * 0.6 + time_factor * 0.4

        return min(1.0, probability)

    def analyze_gate_response(self, response: str, gate: str) -> Dict:
        """
        Analiza la respuesta de un gate para extraer información útil.
        """
        if gate not in self.gate_responses:
            self.gate_responses[gate] = {
                "patterns": {},
                "success_indicators": [],
                "failure_indicators": []
            }

        gate_data = self.gate_responses[gate]

        # Análisis simple de respuesta (esto se puede mejorar con ML)
        response_lower = response.lower()

        # Indicadores comunes de éxito
        success_indicators = ["approved", "success", "thank you", "confirmation", "complete"]
        failure_indicators = ["declined", "failed", "error", "invalid", "rejected"]

        is_success = any(indicator in response_lower for indicator in success_indicators)
        is_failure = any(indicator in response_lower for indicator in failure_indicators)

        return {
            "is_success": is_success,
            "is_failure": is_failure,
            "confidence": 0.7  # Esto se puede mejorar con análisis más sofisticado
        }

    def optimize_check_sequence(self, cards: List[Dict]) -> List[Dict]:
        """
        Optimiza el orden de verificación de tarjetas para maximizar el éxito.
        """
        # Calcular probabilidad de éxito para cada tarjeta
        for card in cards:
            card["success_probability"] = self.calculate_check_probability(card)

        # Ordenar por probabilidad de éxito (descendente)
        return sorted(cards, key=lambda c: c["success_probability"], reverse=True)