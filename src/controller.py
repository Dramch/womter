import os
import pandas as pd
import requests
import time
import math
from dotenv import load_dotenv
from settings import settings
from writter import write_row_to_backup

def build_chunks(terms: list[str]) -> list[str]:
    max_len = 900
    chunks, length = [], 0
    for term in terms:
        length += len(term) + 4 #account for OR in query
        if length < max_len and len(term) > 0:
            chunks.append(term)
        else:
            break
    return chunks


def make_query(lang, terms):
    queries = []
    chunks = build_chunks(terms)
    query = "("
    for chunk in chunks:
        query += f'"{chunk}" OR '
    query = query[:-4]
    if query == "":
        return []
    query += ")"
    query += f" lang:{lang} -is:retweet"
    if settings.ONLY_VERIFIED:
        query += " is:verified"
    queries.append(query)
    return queries


def get_tweets(query, next_token=None):
    headers = {
        "Authorization": f"Bearer {settings.TOKEN_KEY}"
    }
    params = {
        "query": query,
        "tweet.fields": settings.TWEET_FIELDS,
        "user.fields": settings.USER_FIELDS,
        "expansions": settings.EXPANSION_FIELDS,
        "media.fields": settings.MEDIA_FIELDS,
        "place.fields": settings.PLACE_FIELDS,
        "poll.fields": settings.POLL_FIELDS,
        "max_results": settings.AMOUNT_TWEETS,
    }
    if next_token:
        params["next_token"] = next_token

    try:
        response = requests.get(settings.BASE_URL, headers=headers, params=params, timeout=20)
    except Exception as e:
        print(f"Error: {e}")
        return None
    
    # from mocks import dummy_collect_tweets
    # response = dummy_collect_tweets()

    if response.status_code != 200:
        raise Exception(f"Error: {response.status_code} {response.text}")

    return response.json()


def collect_tweets(max_tweets):
    if not settings.TOKEN_KEY:
        raise ValueError("TOKEN_KEY is not set")

    rows = []
    seen_ids = set()
    count = {lang: 0 for lang in settings.TERMS}

    for lang, terms in settings.TERMS.items():
        queries = make_query(lang, terms)
        amount_tweets = math.ceil(max_tweets / len(settings.TERMS))
        for query in queries:
            next_token = None
            while count[lang] < amount_tweets:
                data = get_tweets(query, next_token)
                write_row_to_backup(data)

                if not data.get("data"):
                    break

                user_lookup = {u["id"]: u for u in data.get("includes", {}).get("users", [])}
                media_lookup = {m["media_key"]: m for m in data.get("includes", {}).get("media", [])}

                for tweet in data["data"]:
                    if tweet["id"] in seen_ids:
                        continue
                    seen_ids.add(tweet["id"])
                    tweet["includes"] = {
                        "users": [user_lookup[tweet["author_id"]]],
                        "media": [media_lookup[mk] for mk in tweet.get("attachments", {}).get("media_keys", [])],
                    }
                    rows.append(tweet)
                    count[lang] += 1

                if "next_token" not in data["meta"]:
                    break
                next_token = data["meta"]["next_token"]
                time.sleep(int(settings.SLEEP_TIME))

               
    return rows, count

