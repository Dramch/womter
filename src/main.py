from controller import collect_tweets
from settings import settings
from writter import write_rows_to_xlmns

def main():
    rows, counts = collect_tweets(int(settings.AMOUNT_TWEETS))
    write_rows_to_xlmns(rows)


if __name__ == "__main__":
    main()







