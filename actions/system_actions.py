import os
import subprocess
import webbrowser
import requests
from datetime import datetime
from core.config import Config
from core.logger import logger

def open_url(url, browser_path=None):
    """Abre una URL en el navegador especificado o el predeterminado."""
    try:
        if browser_path and os.path.exists(browser_path):
            logger.info(f"Abriendo {url} con {browser_path}")
            subprocess.Popen([browser_path, url])
            return True
        else:
            logger.info(f"Abriendo {url} con el navegador predeterminado.")
            webbrowser.open(url)
            return True
    except Exception as e:
        logger.error(f"Error abriendo URL {url}: {e}")
        return False

def open_perplexity():
    """Acción: Abre Perplexity AI."""
    return open_url(Config.PERPLEXITY_URL, Config.OPERA_PATH)

def open_youtube():
    """Acción: Abre YouTube."""
    return open_url(Config.YOUTUBE_URL, Config.OPERA_PATH)

def get_current_time():
    """Retorna la hora actual formateada."""
    now = datetime.now()
    return f"Son las {now.hour} y {now.minute:02d}, señor."

def get_current_date():
    """Retorna la fecha actual formateada."""
    now = datetime.now()
    meses = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
    return f"Hoy es {now.day} de {meses[now.month-1]} de {now.year}, señor."

def get_weather(city="Manises"):
    """Consulta el clima usando OpenWeatherMap."""
    if not Config.OPENWEATHER_API_KEY:
        return "Lo siento señor, no tengo configurada la clave de API para el clima."
    
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={Config.OPENWEATHER_API_KEY}&units=metric&lang=es"
        response = requests.get(url)
        data = response.json()
        
        if response.status_code == 200:
            temp = data['main']['temp']
            desc = data['weather'][0]['description']
            return f"En {city} hace {temp:.1f} grados con {desc}, señor."
        else:
            return f"No he podido encontrar información del clima para {city}, señor."
    except Exception as e:
        logger.error(f"Error consultando el clima: {e}")
        return "Ha ocurrido un error al conectar con el servicio meteorológico."

def play_spotify(query):
    """Abre Spotify y busca/reproduce una canción."""
    logger.info(f"Buscando en Spotify: {query}")
    # Usamos el esquema de búsqueda de Spotify
    url = f"spotify:search:{query}"
    try:
        subprocess.Popen(["start", url], shell=True)
        return f"Reproduciendo {query} en Spotify, señor."
    except Exception as e:
        logger.error(f"Error lanzando Spotify: {e}")
        return "Hubo un problema al intentar abrir Spotify."

def launch_steam(game_name=None):
    """Abre Steam o un juego específico si se proporciona el nombre."""
    if not game_name or game_name.lower() == "steam":
        subprocess.Popen(["start", "steam://open/main"], shell=True)
        return "Abriendo Steam, señor."
    
    logger.info(f"Buscando juego en Steam: {game_name}")
    appid = find_steam_appid(game_name)
    
    if appid:
        subprocess.Popen(["start", f"steam://rungameid/{appid}"], shell=True)
        return f"Iniciando {game_name} en Steam, señor. Disfrute."
    else:
        # Si no lo encontramos instalado, intentamos abrir la búsqueda en la tienda
        subprocess.Popen(["start", f"steam://openurl/https://store.steampowered.com/search/?term={game_name}"], shell=True)
        return f"No he encontrado {game_name} instalado, abriendo la tienda de Steam, señor."

def find_steam_appid(game_name):
    """Busca el AppID de un juego instalado localmente."""
    import re
    steamapps_path = Config.STEAM_APPS_PATH
    if not os.path.exists(steamapps_path):
        return None
    
    game_name_clean = game_name.lower().strip()
    
    try:
        for file in os.listdir(steamapps_path):
            if file.endswith(".acf"):
                with open(os.path.join(steamapps_path, file), "r", encoding="utf-8") as f:
                    content = f.read()
                    name_match = re.search(r'"name"\s+"(.*?)"', content)
                    if name_match:
                        installed_name = name_match.group(1).lower()
                        if game_name_clean in installed_name:
                            appid_match = re.search(r'"appid"\s+"(\d+)"', content)
                            if appid_match:
                                return appid_match.group(1)
    except Exception as e:
        logger.error(f"Error escaneando juegos de Steam: {e}")
    
    return None

def say_hello():
    """Acción: Responde con un saludo."""
    return "Hola señor, ¿en qué puedo ayudarle hoy?"

def no_command_response():
    """Acción: Respuesta cuando no se entiende la orden."""
    return "No he podido entender ninguna orden clara, señor."

