# ====================== CONFIGURACIÓN DEL SISTEMA DE VERIFICACIÓN DE TARJETAS ======================

API_BASE_URL = "http://localhost:8080/api/v1/tarjetas"

# ====================== PROXIES ======================

# Fuentes de proxies SOCKS5 públicas (las más actualizadas y confiables en 2026)
PROXY_SOURCES = [
    # === Top tier (actualización muy frecuente + buena verificación) ===
    "https://cdn.jsdelivr.net/gh/proxifly/free-proxy-list@main/proxies/protocols/socks5/data.txt",   # Actualizado cada 5 min
    "https://raw.githubusercontent.com/proxygenerator1/ProxyGenerator/main/MostStable/socks5.txt", # Muy estable
    "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks5.txt",
    "https://raw.githubusercontent.com/wiki/gfpcom/free-proxy-list/lists/socks5.txt",             # Gran volumen

    # Fuentes complementarias sólidas
    "https://raw.githubusercontent.com/VPSLabCloud/VPSLab-Free-Proxy-List/main/socks5_all.txt",
    "https://raw.githubusercontent.com/mmpx12/proxy-list/master/socks5.txt",
    "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/socks5.txt",
    "https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies-socks5.txt",
    "https://raw.githubusercontent.com/hookzof/socks5_list/master/proxy.txt",
]

# Tor como fallback siempre disponible (muy útil para anonimato extra)
TOR_PROXY = "socks5://127.0.0.1:9050"

# ====================== PARÁMETROS DE VERIFICACIÓN ======================

MAX_RETRIES = 4                    # Aumentado un poco
TIMEOUT = 12                       # Reducido ligeramente (Tor necesita más, pero proxies públicos menos)
CONNECT_TIMEOUT = 8                # Timeout solo para conectar (importante)
READ_TIMEOUT = 15

CONCURRENT_CHECKS = 8              # Ajustable según tu máquina y riesgo
PROXY_VERIFY_WORKERS = 80          # Workers para chequear proxies
MAX_PROXY_SAMPLE = 300             # Muestra máxima de proxies a usar por ronda

# Rotación y uso de proxies
PROXY_ROTATION_STRATEGY = "random"          # Opciones: random, round_robin, least_used
PROXY_FAIL_THRESHOLD = 3                    # Veces que falla antes de banearlo temporalmente
PROXY_COOLDOWN_MINUTES = 15                 # Tiempo de cooldown tras fallos

# ====================== ARCHIVOS Y RUTAS ======================

DEFAULT_CARD_PATH = "casper@192:~/Carding/Trajets"
PROXY_CACHE_FILE = "proxies_cache.json"     # Cambiado a JSON para guardar más info (país, latencia, etc.)
RESULTS_FILE = "results.json"
FAILED_CARDS_FILE = "failed_cards.txt"
SUCCESS_CARDS_FILE = "success_cards.txt"

# ====================== UI / ANIMACIÓN ======================

REFRESH_RATE = 0.4
ANIMATION_SPEED = 0.08
SHOW_PROGRESS_BAR = True
VERBOSE_LOGGING = True                      # Muestra más detalles en consola

# ====================== SEGURIDAD Y ANTI-DETECCIÓN ======================

# Headers aleatorios o fijos (recomiendo usar rotating user-agents)
USER_AGENT_ROTATION = True

# Delays anti-detección
MIN_DELAY_BETWEEN_CHECKS = 0.8      # Segundos mínimo entre checks
MAX_DELAY_BETWEEN_CHECKS = 3.5

# Usar Tor preferentemente en ciertos casos
PREFER_TOR_FOR_SENSITIVE = True     # Ej: BINs raros o alto riesgo

# ====================== CACHE Y ACTUALIZACIÓN ======================

CACHE_EXPIRY_HOURS = 2              # Cuánto tiempo confiar en el caché de proxies
FORCE_REFRESH_PROXIES = False       # Forzar refresco al iniciar