import requests
import random
import time
import threading
from typing import List, Dict, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
from utils.logger import Logger
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

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
        self.logger.success(f"Total de proxies únicos obtenidos: {len(unique_proxies)}")

        return unique_proxies

    def test_proxy(self, proxy: str) -> Tuple[bool, float]:
        """
        Verifica si un proxy funciona y mide su tiempo de respuesta.
        """
        try:
            # Detectar tipo de proxy
            if proxy.startswith('socks4://'):
                proxy_url = proxy.replace('socks4://', '')
                proxy_dict = {"http": f"socks4://{proxy_url}", "https": f"socks4://{proxy_url}"}
            elif proxy.startswith('socks5://'):
                proxy_url = proxy.replace('socks5://', '')
                proxy_dict = {"http": f"socks5://{proxy_url}", "https": f"socks5://{proxy_url}"}
            else:
                # Si no tiene prefijo, asumimos HTTP
                if '://' in proxy:
                    proxy_url = proxy.split('://')[1]
                else:
                    proxy_url = proxy
                proxy_dict = {"http": f"http://{proxy_url}", "https": f"http://{proxy_url}"}

            start_time = time.time()

            # Usar un endpoint de prueba rápido con timeout corto
            response = requests.get(
                "http://httpbin.org/ip",
                proxies=proxy_dict,
                timeout=3,  # Timeout corto para test
                verify=False
            )

            response_time = time.time() - start_time

            if response.status_code == 200:
                return True, response_time
            else:
                return False, response_time

        except Exception:
            return False, float('inf')

    def verify_proxies(self, proxy_list: List[str], max_workers: int = None) -> List[str]:
        if max_workers is None:
            max_workers = getattr(self.config, 'PROXY_VERIFY_WORKERS', 80)

        max_sample = getattr(self.config, 'MAX_PROXY_SAMPLE', 500)
        if len(proxy_list) > max_sample:
            self.logger.info(f"Tomando muestra de {max_sample} proxies")
            proxy_list = random.sample(proxy_list, max_sample)

        self.logger.info(f"Verificando {len(proxy_list)} proxies (soporte HTTPS)...")

        working_proxies = []

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_proxy = {
                executor.submit(self.test_proxy_https, proxy): proxy
                for proxy in proxy_list
            }

            for future in as_completed(future_to_proxy):
                proxy = future_to_proxy[future]
                try:
                    is_working, response_time = future.result()
                    if is_working:
                        with self.proxy_lock:
                            working_proxies.append(proxy)
                        if self.algorithms:
                            self.algorithms.update_proxy_performance(proxy, True, response_time)
                except Exception:
                    pass

        self.logger.success(f"Proxies con soporte HTTPS: {len(working_proxies)}/{len(proxy_list)}")
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
                # Guardar igual la lista completa para cache
                with self.proxy_lock:
                    self.proxies = fresh_proxies
                    self.working_proxies = []
                return False

            # Actualizar lista de proxies
            with self.proxy_lock:
                self.proxies = verified_proxies
                self.working_proxies = verified_proxies.copy()
                self.last_update = current_time

            self.logger.success(f"Lista de proxies actualizada: {len(self.working_proxies)} proxies funcionales")
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
                    self.logger.success(f"Usando {len(self.working_proxies)} proxies cacheados funcionales")
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

    def test_proxy_https(self, proxy: str) -> Tuple[bool, float]:
        """
        Verifica si un proxy soporta conexiones HTTPS (túnel SSL).
        """
        try:
            if proxy.startswith('socks5://'):
                url = proxy.replace('socks5://', '')
                proxy_dict = {"http": f"socks5://{url}", "https": f"socks5://{url}"}
            elif proxy.startswith('socks4://'):
                url = proxy.replace('socks4://', '')
                proxy_dict = {"http": f"socks4://{url}", "https": f"socks4://{url}"}
            elif proxy.startswith('https://'):
                url = proxy.replace('https://', '')
                proxy_dict = {"http": f"http://{url}", "https": f"https://{url}"}
            else:
                if '://' in proxy:
                    url = proxy.split('://')[1]
                else:
                    url = proxy
                proxy_dict = {"http": f"http://{url}", "https": f"http://{url}"}

            start_time = time.time()

            # Probar contra un sitio HTTPS real
            response = requests.get(
                "https://httpbin.org/ip",
                proxies=proxy_dict,
                timeout=5,
                verify=False
            )

            response_time = time.time() - start_time
            return response.status_code == 200, response_time

        except Exception:
            return False, float('inf')

    def initialize(self):
        """
        Inicializa el gestor de proxies obteniendo y verificando proxies.
        """
    self.logger.info("Inicializando gestor de proxies...")

    # Siempre agregar Tor como primer proxy
    tor_proxy = getattr(self.config, 'TOR_PROXY', 'socks5://127.0.0.1:9050')

    with self.proxy_lock:
        if tor_proxy not in self.working_proxies:
            self.working_proxies.insert(0, tor_proxy)
            self.logger.success(f"Tor agregado como proxy principal: {tor_proxy}")

    # Intentar cargar proxies cacheados
    try:
        with open(self.config.PROXY_CACHE_FILE, 'r') as f:
            cached_proxies = [line.strip() for line in f if line.strip()]

        if cached_proxies:
            self.logger.info(f"Cargando {len(cached_proxies)} proxies desde caché")
            verified_proxies = self.verify_proxies(cached_proxies)

            with self.proxy_lock:
                for p in verified_proxies:
                    if p not in self.working_proxies:
                        self.working_proxies.append(p)
                self.proxies = self.working_proxies.copy()

            self.logger.success(f"Total proxies: {len(self.working_proxies)} (incluye Tor)")
            return True
    except Exception as e:
        self.logger.warning(f"No se pudieron cargar proxies cacheados: {str(e)}")

    # Obtener proxies frescos como respaldo
    try:
        fresh = self.fetch_proxies_from_sources()
        if fresh:
            verified = self.verify_proxies(fresh)
            with self.proxy_lock:
                for p in verified:
                    if p not in self.working_proxies:
                        self.working_proxies.append(p)
    except:
        pass

    self.logger.success(f"Proxies disponibles: {len(self.working_proxies)} (Tor + respaldo)")
    return True
