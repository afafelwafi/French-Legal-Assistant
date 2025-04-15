# config.py
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Redis Configuration
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "")
REDIS_TTL = int(os.getenv("REDIS_TTL", 3600))  # 1 hour default TTL


# API Keys
SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

PISTE_API_CLIENT_ID = os.getenv("PISTE_API_CLIENT_ID")
PISTE_API_CLIENT_SECRET = os.getenv("PISTE_API_CLIENT_SECRET")

# LLM Configuration
DEFAULT_MODEL = "llama3-8b-8192"
DEFAULT_TEMPERATURE = 0.3
DEFAULT_MAX_TOKENS = 512

# Embeddings Configuration
EMBEDDING_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

# Retrieval Configuration
CHUNK_SIZE = 512
CHUNK_OVERLAP = 50

# Server Configuration
HOST = os.getenv("HOST")
PORT = int(os.getenv("PORT"))

# 📚 Liste des codes à récupérer (tu peux en rajouter d'autres)
CODES = [
    "Code civil",
    "Code de commerce",
    "Code des communes",
    "Code de déontologie des architectes",
    "Code de justice administrative",
    "Code de justice militaire (nouveau)",
    "Code de l'action sociale et des familles",
    "Code de l'énergie",
    "Code de l'entrée et du séjour des étrangers et du droit d'asile",
    "Code de l'expropriation pour cause d'utilité publique",
    "Code de l'organisation judiciaire",
    "Code de la commande publique",
    "Code de la consommation",
    "Code de la construction et de l'habitation",
    "Code de la défense",
    "Code de la famille et de l'aide sociale",
    "Code de la justice pénale des mineurs",
    "Code de la Légion d'honneur, de la Médaille militaire et de l'ordre national du Mérite",
    "Code de la mutualité",
    "Code de la propriété intellectuelle",
    "Code de la route",
    "Code de la santé publique",
    "Code de la sécurité intérieure",
    "Code de la sécurité sociale",
    "Code de la voirie routière",
    "Code des procédures civiles d'exécution",
    "Code de procédure pénale",
    "Code des assurances",
    "Code des communes de la Nouvelle-Calédonie",
    "Code des douanes",
    "Code des douanes de Mayotte",
    "Code des impositions sur les biens et services",
    "Code des instruments monétaires et des médailles",
    "Code des juridictions financières",
    "Code des pensions civiles et militaires de retraite",
    "Code des pensions de retraite des marins français du commerce, de pêche ou de plaisance",
    "Code des pensions militaires d'invalidité et des victimes de guerre",
    "Code des ports maritimes",
    "Code des postes et des communications électroniques",
    "Code des relations entre le public et l'administration",
    "Code du travail",
    "Code disciplinaire et pénal de la marine marchande",
    "Code du cinéma et de l'image animée",
    "Code du domaine de l'Etat",
    "Code du domaine de l'Etat et des collectivités publiques applicable à la collectivité territoriale de Mayotte",
    "Code du domaine public fluvial et de la navigation intérieure",
    "Code du patrimoine",
    "Code du service national",
    "Code du sport",
    "Code du travail maritime",
    "Code forestier (nouveau)",
    "Code général de la fonction publique",
    "Code général de la propriété des personnes publiques",
    "Code général des collectivités territoriales",
    "Code général des impôts",
    "Code général des impôts, annexe IV",
    "Code minier (nouveau)",
    "Code monétaire et financier",
    "Code pénitentiaire",
    "Code rural (ancien)",
    "Code rural et de la pêche maritime",
    "Code électoral",
    "Livre des procédures fiscales",
]

# Folder where to store files
FOLDER_NAME = "legifrance"

# Logging Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_FILE = os.getenv("LOG_FILE", "")  # Empty for stdout

# Monitoring
ENABLE_METRICS = os.getenv("ENABLE_METRICS", "True").lower() in ("true", "1", "t")
METRICS_PORT = int(os.getenv("METRICS_PORT", 9090))
