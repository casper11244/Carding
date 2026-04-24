import requests
import random
import time
import threading
from typing import List, Dict, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
from utils.logger import Logger

class ProxyManager:
    """
    Gestor avanzado de proxies con múltiples fuentes, verificación automática
    y rotación inteligente basada en rendimiento.
    """

    def __init__(self, config):
        self.config = config
        self.logger = Logger("ProxyManager")
        self.algorithms = None  # Se inyectará desde Checker
        self.proxies = []
        self.working_proxies = []
        self.proxy_lock = threading.Lock()
        self.last_update = 0
        self.update_interval = 3600  # 1 hora

    def set_algorithms(self, algorithms):
        """Inyecta la instancia de AdvancedAlgorithms"""
        self.algorithms = algorithms

    def fetch_proxies_from_sources(self) -> List[str]:
        """
        Obtiene proxies de múltiples fuentes configuradas.
        """
        all_proxies = []

        for source in self.config.PROXY_SOURCES:
            try:
                self.logger.info(f"Obteniendo proxies desde: {source}")
                response = requests.get(source, timeout=15)

                if response.status_code == 200:
                    # Procesar respuesta según el formato
                    if source.endswith(".txt"):
                        # Formato de texto plano
                        lines = response.text.strip().split('\n')
                        proxies = [line.strip() for line in lines if ':' in line]
                    else:
                        # Formato JSON (asumimos que es una lista de proxies)
                        try:
                            data = response.json()
                            proxies = data.get("proxies", [])
                        except ValueError:
                            proxies = []

                    all_proxies.extend(proxies)
                    self.logger.info(f"Obtenidos {len(proxies)} proxies desde {source}")
                else:
                    self.logger.warning(f"Error al obtener proxies desde {source}: {response.status_code}")

            except Exception as e:
                self.logger.error(f"Excepción al obtener proxies desde {source}: {str(e)}")

        # Eliminar duplicados
        unique_proxies = list(set(all_proxies))
        self.logger.info(f"Total de proxies únicos obtenidos: {len(unique_proxies)}")

        return unique_proxies

    def test_proxy(self, proxy: str) -> Tuple[bool, float]:
        """
        Verifica si un proxy funciona y mide su tiempo de respuesta.
        """
        try:
            proxy_dict = {
                "http": f"http://{proxy}",
                "https": f"http://{proxy}"
            }

            start_time = time.time()

            # Usar un endpoint de prueba rápido
            response = requests.get(
                "http://httpbin.org/ip",
                proxies=proxy_dict,
                timeout=self.config.TIMEOUT
            )

            response_time = time.time() - start_time

            if response.status_code == 200:
                return True, response_time
            else:
                return False, response_time

        except Exception:
            return False, float('inf')

    def verify_proxies(self, proxy_list: List[str], max_workers: int = 20) -> List[str]:
        """
        Verifica una lista de proxies en paralelo y devuelve los que funcionan.
        """
        self.logger.info(f"Verificando {len(proxy_list)} proxies...")

        working_proxies = []

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Enviar todas las tareas
            future_to_proxy = {
                executor.submit(self.test_proxy, proxy): proxy
                for proxy in proxy_list
            }

            # Recibir resultados a medida que completan
            for future in as_completed(future_to_proxy):
                proxy = future_to_proxy[future]
                try:
                    is_working, response_time = future.result()

                    if is_working:
                        with self.proxy_lock:
                            working_proxies.append(proxy)

                        # Actualizar rendimiento si tenemos algoritmos disponibles
                        if self.algorithms:
                            self.algorithms.update_proxy_performance(proxy, True, response_time)

                        self.logger.debug(f"Proxy funcional: {proxy} ({response_time:.2f}s)")
                    else:
                        # Actualizar rendimiento si tenemos algoritmos disponibles
                        if self.algorithms:
                            self.algorithms.update_proxy_performance(proxy, False, float('inf'))

                except Exception as e:
                    self.logger.error(f"Error al verificar proxy {proxy}: {str(e)}")

        self.logger.info(f"Proxies verificados: {len(working_proxies)}/{len(proxy_list)} funcionan")

        return working_proxies

    def update_proxy_list(self, force_update: bool = False) -> bool:
        """
        Actualiza la lista de proxies si es necesario o si se fuerza.
        """
        current_time = time.time()

        if not force_update and (current_time - self.last_update) < self.update_interval:
            self.logger.debug("La lista de proxies está actualizada")
            return True

        try:
            # Obtener proxies de las fuentes
            fresh_proxies = self.fetch_proxies_from_sources()

            if not fresh_proxies:
                self.logger.warning("No se pudieron obtener proxies frescos")
                return False

            # Verificar proxies
            verified_proxies = self.verify_proxies(fresh_proxies)

            if not verified_proxies:
                self.logger.warning("No se encontraron proxies funcionales")
                return False

            # Actualizar lista de proxies
            with self.proxy_lock:
                self.proxies = verified_proxies
                self.working_proxies = verified_proxies.copy()
                self.last_update = current_time

            self.logger.info(f"Lista de proxies actualizada: {len(self.working_proxies)} proxies funcionales")
            return True

        except Exception as e:
            self.logger.error(f"Error al actualizar la lista de proxies: {str(e)}")
            return False

    def get_proxy(self) -> Optional[str]:
        """
        Obtiene un proxy de la lista, optimizando el orden si hay algoritmos disponibles.
        """
        with self.proxy_lock:
            if not self.working_proxies:
                return None

            # Si tenemos algoritmos, usar orden optimizado
            if self.algorithms:
                optimized_proxies = self.algorithms.optimize_proxy_rotation(self.working_proxies)
                proxy = optimized_proxies[0]

                # Mover el proxy usado al final de la lista
                self.working_proxies.remove(proxy)
                self.working_proxies.append(proxy)

                return proxy
            else:
                # Selección aleatoria simple
                proxy = random.choice(self.working_proxies)
                self.working_proxies.remove(proxy)
                self.working_proxies.append(proxy)

                return proxy

    def mark_proxy_failed(self, proxy: str):
        """
        Marca un proxy como fallido y lo elimina de la lista de trabajo.
        """
        with self.proxy_lock:
            if proxy in self.working_proxies:
                self.working_proxies.remove(proxy)
                self.logger.warning(f"Proxy marcado como fallido: {proxy}")

                # Actualizar rendimiento si tenemos algoritmos disponibles
                if self.algorithms:
                    self.algorithms.update_proxy_performance(proxy, False, float('inf'))

    def get_proxy_count(self) -> int:
        """
        Devuelve el número de proxies disponibles.
        """
        with self.proxy_lock:
            return len(self.working_proxies)

    def initialize(self):
        """
        Inicializa el gestor de proxies obteniendo y verificando proxies.
        """
        self.logger.info("Inicializando gestor de proxies...")

        # Intentar cargar proxies cacheados si existen
        try:
            with open(self.config.PROXY_CACHE_FILE, 'r') as f:
                cached_proxies = [line.strip() for line in f if line.strip()]

            if cached_proxies:
                self.logger.info(f"Cargando {len(cached_proxies)} proxies desde caché")
                verified_proxies = self.verify_proxies(cached_proxies)

                with self.proxy_lock:
                    self.proxies = verified_proxies
                    self.working_proxies = verified_proxies.copy()

                if self.working_proxies:
                    self.logger.info(f"Usando {len(self.working_proxies)} proxies cacheados funcionales")
                    return True
        except Exception as e:
            self.logger.warning(f"No se pudieron cargar proxies cacheados: {str(e)}")

        # Si no hay proxies cacheados o no funcionan, obtener nuevos
        return self.update_proxy_list(force_update=True)

    def save_proxies_to_cache(self):
        """
        Guarda la lista de proxies en caché para uso futuro.
        """
        try:
            with self.proxy_lock:
                with open(self.config.PROXY_CACHE_FILE, 'w') as f:
                    for proxy in self.proxies:
                        f.write(f"{proxy}\n")

            self.logger.debug(f"Guardados {len(self.proxies)} proxies en caché")
        except Exception as e:
            self.logger.error(f"Error al guardar proxies en caché: {str(e)}")