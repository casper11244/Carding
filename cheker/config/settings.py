# Configuración del sistema de verificación de tarjetas

# Configuración de la API de tarjetas
API_BASE_URL = "http://localhost:8080/api/v1/tarjetas"

# Configuración de proxies
PROXY_SOURCES = [
    "https://api.proxyscrape.com/v2/?request=get&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all",
    "https://raw.githubusercontent.com/TheSpeedX/PROXY_LIST/master/http.txt",
    "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/http.txt"
]

# Configuración de verificación
MAX_RETRIES = 3
TIMEOUT = 10
CONCURRENT_CHECKS = 5

# Configuración de archivos
DEFAULT_CARD_PATH = "casper@192:~/Carding/Trajets"
PROXY_CACHE_FILE = "proxies_cache.txt"
RESULTS_FILE = "results.json"

# Configuración de la interfaz
REFRESH_RATE = 0.5  # segundos
ANIMATION_SPEED = 0.1  # segundos