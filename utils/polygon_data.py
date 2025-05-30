from polygon import RESTClient

def get_polygon_price(ticker, api_key):
    try:
        client = RESTClient(api_key)
        aggs = client.get_previous_close(ticker)
        return aggs.results[0]['c']
    except:
        return "N/A"
