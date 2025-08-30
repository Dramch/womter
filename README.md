Womter es una tubería de datos en Python para investigación académica que:
1.Recolecta tuits desde X API v2 (múltiples idiomas)
2.Unifica y depura los Excel generados
3.Aplica patrones (texto/números/fechas/booleanos) y exporta resultados listos para análisis

1. ESTRUCTURA DE WOMTER:
womter/
├── api/                  # Recolección desde X API v2
│   ├── data/
│   │   ├── backup/       # Copias JSON por lote
│   │   └── output/       # XLSX por sesión (tabs por idioma)
│   ├── src/
│   │   ├── controller.py # Queries, rate-limit, paginación, backup
│   │   ├── main.py       # Entry point
│   │   ├── mocks.py      # Datos simulados offline
│   │   ├── settings.py   # Config .env
│   │   └── writter.py    # Excel estilizado + Gender API
│   ├── .env              # Variables de entorno
│   ├── Makefile
│   └── requirements.txt
│
├── merger/               # Unificación de salidas
│   ├── data/
│   │   ├── input/        # Recibe archivos desde api/data/output
│   │   └── output/       # merged_data_*.xlsx
│   ├── src/
│   │   ├── reader.py     # Lectura, combinación, dedupe
│   │   └── writter.py    # Escritura XLSX (tabs por idioma + "all")
│   ├── Makefile
│   └── requirements.txt
│
└── analyzer/             # (tu Pattern Analyzer)
    ├── data/
    │   ├── input/        # XLSX unificados (desde merger)
    │   ├── patterns/     # JSON de patrones
    │   └── output/       # Resultados por patrón/idioma
    ├── src/
    │   ├── analyzer.py   # Motor de patrones
    │   ├── data_reader.py
    │   └── pattern_reader.py
    ├── main.py / tests
    └── requirements.txt

2.INSTALACIÓN RÁPIDA:
2.1. Crear venv (en la raíz del monorepo)
python -m venv venv

2.2 Activar
source venv/bin/activate      # Linux/macOS
venv\Scripts\activate         # Windows

INSTALA DEPENDENCIAS POR MODULO:
pip install -r api/requirements.txt
pip install -r merger/requirements.txt
pip install -r analyzer/requirements.txt

3.CONFIGURACIÓN (.env del módulo API)
api/.env
3.1 X API v2
TOKEN_KEY=TU_BEARER_TOKEN
BASE_URL=https://api.twitter.com/2/tweets/search/recent

3.2 Rate limit
AMOUNT_TWEETS=100          # por request (máx según plan)
SLEEP_TIME=5               # segundos entre páginas
ONLY_VERIFIED=True         # filtra cuentas verificadas

3.3 Gender API (opcional)
GENDER_API_KEY=xxxx
GENDER_URL=https://gender-api.com/get

3.4 Campos solicitados
TWEET_FIELDS=id,text,created_at,author_id,lang,public_metrics
USER_FIELDS=username,verified,location,public_metrics
EXPANSION_FIELDS=author_id
MEDIA_FIELDS=url,preview_image_url
PLACE_FIELDS=full_name,id,country,country_code
POLL_FIELDS=id,state,created_at,updated_at

3.5 Términos por idioma (coma)
SPANISH_TERMS=(introduce términos en español, listas cortas y precisas para reducir ruido y evitar límites de longitud en queries)
ENGLISH_TERMS=(introduce términos en inglés, listas cortas y precisas para reducir ruido y evitar límites de longitud en queries)
FRENCH_TERMS=(introduce términos en francés, listas cortas y precisas para reducir ruido y evitar límites de longitud en queries)
GERMAN_TERMS=(introduce términos en alemán, listas cortas y precisas para reducir ruido y evitar límites de longitud en queries)
ARABIC_TERMS=(introduce términos en árabe, listas cortas y precisas para reducir ruido y evitar límites de longitud en queries)

4. FLUJO DE TRABAJO (end to end)
PASO 1: recolectar API
cd api
make start          # Windows/macOS/Linux (usa ../venv)
#Salidas: data/output/tweets_YYYYMMDD_HHMMSS.xlsx (pestañas por idioma)
#Backup JSON automático en data/backup/

Opcional: probar offline
from src.mocks import dummy_collect_tweets
dummy_collect_tweets().json()

PASO 2: unificar (Merger)
cd ../merger
make start-merger          #ejecuta
#Salida: data/output/merged_data_YYYYMMDD_HHMMSS.xlsx
#Incluye pestañas por idioma y 'all'

PASO 3: analizar (Analyzer)
Copiar el merged_data_*.xlsx a analyzer/data/input/
Definir patrones en analyzer/data/patterns/*.json

EJEMPLO:
{
  "name": "Alta_actividad_es",
  "pattern": {
    "texto": ["palabra1", "palabra2"],
    "seguidores": [">1000"],
    "fecha": [">2024-01-01", "<2024-12-31"],
    "verificado": [true]
  }
}

EJECUTAR:
cd ../analyzer
python src/main.py
#Salida: data/output/PatternName_YYYYMMDD_HHMMSS/es_results.xlsx (etc.)

6. BUENAS PRÁCTICAS

Ajusta AMOUNT_TWEETS y SLEEP_TIME según tu plan para evitar 429 (rate limit).
Mantén términos por idioma coherentes y no demasiado largos (el controlador corta a ~900 chars).
Versiona analyzer/data/patterns/ para trazabilidad.
No subas .env a Git público.
Usa merger para normalizar siempre antes de patrones.

7. SOLUCIÓN DE PROBLEMAS

ValueError: TOKEN_KEY is not set → revisa api/.env.
Excel sin pestañas → verifica que el API generó data/output/*.xlsx.
Hoja vacía en un idioma → puede no haber tuits/terminología demasiado estricta.
Carácteres raros en CSV → reader.py prueba utf-8, latin-1, cp1252.
Sheet name inválido → el writer sanea nombres (≤31 chars, sin \ / * ? : [ ]).

8. LICENCIA
Este proyecto forma parte del sistema de análisis Womter con fines académicos.
