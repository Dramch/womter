import types
import uuid

def dummy_collect_tweets():
    # Define the mock response data
    i1 = str(uuid.uuid4())
    i2 = str(uuid.uuid4())
    
    # User data for includes
    user1_id = "user1_id"
    user2_id = "user2_id"
    user3_id = "689a2658cf9289d89f3d2fff"  # Specific user ID requested
    
    # Media data for includes
    media1_key = "media1_key"
    media2_key = "media2_key"
    
    response_data = {
        "data": [
            {
                "id": f'{i1}',
                "text": "¡Hola amigos! ¿Cómo están hoy? #SpanishVibes",
                "created_at": "2025-08-10T18:30:00.000Z",
                "author_id": user1_id,
                "lang": "es",
                "public_metrics": {
                    "retweet_count": 25,
                    "reply_count": 10,
                    "like_count": 150,
                    "quote_count": 5
                },
                "attachments": {
                    "media_keys": [media1_key]
                }
            },
            {
                "id": f'{i2}',
                "text": "Adiós al verano, hola al otoño 🍂",
                "created_at": "2025-08-10T18:25:15.000Z",
                "author_id": user2_id,
                "lang": "es",
                "public_metrics": {
                    "retweet_count": 15,
                    "reply_count": 8,
                    "like_count": 89,
                    "quote_count": 3
                },
                "attachments": {
                    "media_keys": [media2_key]
                }
            }
        ],
        "includes": {
            "users": [
                {
                    "id": user1_id,
                    "name": "María",
                    "username": "usuario1",
                    "verified": True,
                    "location": "Madrid, España",
                    "public_metrics": {
                        "followers_count": 1500,
                        "following_count": 300,
                        "tweet_count": 2500
                    }
                },
                {
                    "id": user2_id,
                    "name": "Carlos",
                    "username": "usuario2",
                    "verified": False,
                    "location": "Barcelona, España",
                    "public_metrics": {
                        "followers_count": 800,
                        "following_count": 200,
                        "tweet_count": 1200
                    }
                },
                {
                    "id": user3_id,
                    "name": "Rodrigo",
                    "username": "rodrigo_user",
                    "verified": True,
                    "location": "Valencia, España",
                    "public_metrics": {
                        "followers_count": 2200,
                        "following_count": 450,
                        "tweet_count": 3200
                    }
                }
            ],
            "media": [
                {
                    "media_key": media1_key,
                    "type": "photo",
                    "url": "https://example.com/media1.jpg"
                },
                {
                    "media_key": media2_key,
                    "type": "photo",
                    "url": "https://example.com/media2.jpg"
                }
            ]
        },
        "meta": {
            "newest_id": i1,
            "oldest_id": i2,
            "result_count": 2,
            "next_token": "b26v89c19zqg8o3fqk9z2x1y7w3e4r5t6y7u8i9o0p"
        }
    }
    
    # Create a mock response object
    mock_response = types.SimpleNamespace()
    mock_response.status_code = 200
    mock_response.text = str(response_data)
    mock_response.json = lambda: response_data
    
    return mock_response