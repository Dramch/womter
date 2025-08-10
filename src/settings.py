import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    TOKEN_KEY = os.getenv("TOKEN_KEY")
    AMOUNT_TWEETS = os.getenv("AMOUNT_TWEETS")
    ONLY_VERIFIED = os.getenv("ONLY_VERIFIED", "True").lower() == "true"
    SLEEP_TIME = os.getenv("SLEEP_TIME")
    BASE_URL = os.getenv("BASE_URL")
    TWEET_FIELDS = os.getenv("TWEET_FIELDS", "id,text,created_at,author_id,lang,public_metrics")
    USER_FIELDS = os.getenv("USER_FIELDS", "username,verified,location,public_metrics")
    EXPANSION_FIELDS = os.getenv("EXPANSION_FIELDS", "author_id")
    MEDIA_FIELDS = os.getenv("MEDIA_FIELDS", "url,preview_image_url")
    PLACE_FIELDS = os.getenv("PLACE_FIELDS", "full_name,id,country,country_code")
    POLL_FIELDS = os.getenv("POLL_FIELDS", "id,state,created_at,updated_at")


    if not TOKEN_KEY:
        raise ValueError("TOKEN_KEY is not set")
    if not AMOUNT_TWEETS:
        raise ValueError("AMOUNT_TWEETS is not set")
    if not SLEEP_TIME:
        raise ValueError("SLEEP_TIME is not set")
    if not BASE_URL:
        raise ValueError("BASE_URL is not set")
    if not TWEET_FIELDS:
        raise ValueError("TWEET_FIELDS is not set")
    if not USER_FIELDS:
        raise ValueError("USER_FIELDS is not set")
    if not EXPANSION_FIELDS:
        raise ValueError("EXPANSIONS is not set")
    if not MEDIA_FIELDS:
        raise ValueError("MEDIA_FIELDS is not set")
    if not PLACE_FIELDS:
        raise ValueError("PLACE_FIELDS is not set")
    if not POLL_FIELDS:
        raise ValueError("POLL_FIELDS is not set")

    SPANISH_TERMS = os.getenv("SPANISH_TERMS", "").split(",")
    ENGLISH_TERMS = os.getenv("ENGLISH_TERMS", "").split(",")
    FRENCH_TERMS = os.getenv("FRENCH_TERMS", "").split(",")
    GERMAN_TERMS = os.getenv("GERMAN_TERMS", "").split(",")
    ARABIC_TERMS = os.getenv("ARABIC_TERMS", "").split(",")

    TERMS = {
        "es": SPANISH_TERMS,
        "en": ENGLISH_TERMS,
        "fr": FRENCH_TERMS,
        "de": GERMAN_TERMS,
        "ar": ARABIC_TERMS
    }

    BACKUP_DIR = os.getenv("BACKUP_DIR", "./data/backup")
    OUTPUT_DIR = os.getenv("OUTPUT_DIR", "./data/output")
    #TODO: add strict mode and anchords if necessary


settings = Settings()