# Configuración del sistema de verificación de tarjetas

# Configuración de la API de tarjetas
API_BASE_URL = "http://localhost:8080/api/v1/tarjetas"

# Configuración de proxies
PROXY_SOURCES = [
    "https://api.proxyscrape.com/v2/?request=get&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all",
    "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/http.txt",
    "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/https.txt",
    "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/socks4.txt",
    "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/socks5.txt",
    "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/http.txt",
    "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/socks4.txt",
    "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/socks5.txt",
    "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt",
    "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies_anonymous/http.txt",
    "https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies-http.txt",
    "https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies-https.txt",
]

# Configuración de verificación
MAX_RETRIES = 2           # Reducido para más velocidad
TIMEOUT = 5               # Timeout más corto
CONCURRENT_CHECKS = 50    # Mucho más paralelismo
PROXY_VERIFY_WORKERS = 100  # Workers para verificar proxies
MAX_PROXY_SAMPLE = 1000   # Máximo de proxies a verificar por lote

# Configuración de archivos
DEFAULT_CARD_PATH = "casper@192:~/Carding/Trajets"
PROXY_CACHE_FILE = "proxies_cache.txt"
RESULTS_FILE = "results.json"

# Configuración de la interfaz
REFRESH_RATE = 0.5
ANIMATION_SPEED = 0.1