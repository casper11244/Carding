import requests
import random
import time
import threading
from typing import List, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from utils.logger import Logger


class ProxyManager:
    """
    Gestor avanzado de proxies con verificación, caché y rotación.
    """

    def __init__(self, config):
        self.config = config
        self.logger = Logger("ProxyManager")
        self.algorithms = None
        self.proxies = []
        self.working_proxies = []
        self.proxy_lock = threading.Lock()
        self.last_update = 0
        self.update_interval = 3600  # 1 hora

    def set_algorithms(self, algorithms):
        self.algorithms = algorithms

    def fetch_proxies_from_sources(self) -> List[str]:
        """Obtiene proxies desde todas las fuentes configuradas."""
        all_proxies = []

        for source in getattr(self.config, 'PROXY_SOURCES', []):
            try:
                self.logger.info(f"Obteniendo proxies desde: {source}")
                response = requests.get(source, timeout=15)

                if response.status_code == 200:
                    lines = response.text.strip().split('\n')
                    proxies = [line.strip() for line in lines if ':' in line and line.strip()]
                    all_proxies.extend(proxies)
                    self.logger.info(f"Obtenidos {len(proxies)} proxies desde {source}")
                else:
                    self.logger.warning(f"Error {response.status_code} en {source}")

            except Exception as e:
                self.logger.error(f"Error al obtener {source}: {e}")

        # Eliminar duplicados
        unique_proxies = list(dict.fromkeys(all_proxies))  # mantiene orden
        self.logger.success(f"Total proxies únicos: {len(unique_proxies)}")
        return unique_proxies

    def test_proxy_https(self, proxy: str) -> Tuple[bool, float]:
        try:
            if proxy.startswith('socks5://'):
                clean = proxy.replace('socks5://', '')
                proxy_dict = {"http": f"socks5h://{clean}", "https": f"socks5h://{clean}"}
            elif proxy.startswith('socks4://'):
                clean = proxy.replace('socks4://', '')
                proxy_dict = {"http": f"socks4://{clean}", "https": f"socks4://{clean}"}
            else:
                if not proxy.startswith(('http://', 'https://')):
                    proxy = f"http://{proxy}"
                proxy_dict = {"http": proxy, "https": proxy}

            start_time = time.time()

            # Prueba más suave
            response = requests.get(
                "https://httpbin.org/ip",
                proxies=proxy_dict,
                timeout=7,      # aumentado
                verify=False
            )

            response_time = time.time() - start_time
            return response.status_code in (200, 301, 302), response_time   # acepta redirecciones

        except Exception:
            return False, float('inf')

    def verify_proxies(self, proxy_list: List[str], max_workers: int = None) -> List[str]:
        """Verifica una lista de proxies en paralelo."""
        if max_workers is None:
            max_workers = getattr(self.config, 'PROXY_VERIFY_WORKERS', 80)

        max_sample = getattr(self.config, 'MAX_PROXY_SAMPLE', 300)
        if len(proxy_list) > max_sample:
            proxy_list = random.sample(proxy_list, max_sample)

        self.logger.info(f"Verificando {len(proxy_list)} proxies...")

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
                        working_proxies.append(proxy)
                        if self.algorithms:
                            self.algorithms.update_proxy_performance(proxy, True, response_time)
                except Exception:
                    pass

        self.logger.success(f"{len(working_proxies)} proxies funcionales encontrados")
        return working_proxies

    def initialize(self):
        """
        Inicializa el ProxyManager (carga caché o fuentes remotas + Tor).
        """
        self.logger.info("Inicializando gestor de proxies...")

        # Agregar Tor siempre primero
        tor_proxy = getattr(self.config, 'TOR_PROXY', 'socks5://127.0.0.1:9050')
        with self.proxy_lock:
            if tor_proxy not in self.working_proxies:
                self.working_proxies.insert(0, tor_proxy)
                self.logger.success(f"Tor agregado como proxy principal")

        # Intentar cargar desde caché
        try:
            with open(self.config.PROXY_CACHE_FILE, 'r') as f:
                cached = [line.strip() for line in f if line.strip()]

            if cached:
                self.logger.info(f"Cargando {len(cached)} proxies desde caché...")
                verified = self.verify_proxies(cached)

                with self.proxy_lock:
                    self.working_proxies.extend([p for p in verified if p not in self.working_proxies])
                    self.proxies = self.working_proxies.copy()

                if self.working_proxies:
                    self.logger.success(f"Inicializado con {len(self.working_proxies)} proxies (caché + Tor)")
                    return True
        except FileNotFoundError:
            self.logger.warning("Archivo de caché no encontrado")
        except Exception as e:
            self.logger.warning(f"Error al cargar caché: {e}")

        # Si no hay caché → cargar desde fuentes
        self.logger.info("Cargando proxies desde fuentes remotas...")
        fresh_proxies = self.fetch_proxies_from_sources()

        if fresh_proxies:
            verified = self.verify_proxies(fresh_proxies)
            with self.proxy_lock:
                self.working_proxies.extend([p for p in verified if p not in self.working_proxies])
                self.proxies = self.working_proxies.copy()

        if self.working_proxies:
            self.logger.success(f"ProxyManager inicializado con {len(self.working_proxies)} proxies")
            return True
        else:
            self.logger.error("No se pudo inicializar ningún proxy funcional")
            return False

    # ====================== Métodos restantes ======================

    def update_proxy_list(self, force_update: bool = False) -> bool:
        """Actualiza la lista completa de proxies."""
        # (puedes expandir esto después)
        return self.initialize()

    def get_proxy(self) -> Optional[str]:
        with self.proxy_lock:
            if not self.working_proxies:
                return None
            proxy = random.choice(self.working_proxies)
            # Rotación simple: mover al final
            self.working_proxies.remove(proxy)
            self.working_proxies.append(proxy)
            return proxy

    def mark_proxy_failed(self, proxy: str):
        with self.proxy_lock:
            if proxy in self.working_proxies:
                self.working_proxies.remove(proxy)
                self.logger.warning(f"Proxy fallido removido: {proxy}")

    def get_proxy_count(self) -> int:
        with self.proxy_lock:
            return len(self.working_proxies)

    def save_proxies_to_cache(self):
        try:
            with self.proxy_lock:
                with open(self.config.PROXY_CACHE_FILE, 'w') as f:
                    for p in self.proxies:
                        f.write(f"{p}\n")
            self.logger.debug(f"Guardados {len(self.proxies)} proxies en caché")
        except Exception as e:
            self.logger.error(f"Error guardando caché: {e}")