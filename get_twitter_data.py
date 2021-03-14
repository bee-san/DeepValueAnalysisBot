import twint

c = twint.Config()


def get_ticker_verfieid(tickr="$AAPL"):
    c.Search = tickr
    c.Verified = True
    c.Native_retweets = True
    c.Lang = "en"
    c.Limit = 100
    c.Store_json = True
    twint.run.Search(c)

    tweets_as_objects = twint.output.tweets_list
    print(tweets_as_objects)


get_ticker_verfieid()
