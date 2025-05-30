import requests
from bs4 import BeautifulSoup

def get_finviz_stats(ticker):
    url = f"https://finviz.com/quote.ashx?t={ticker}"
    headers = {"User-Agent": "Mozilla/5.0"}
    soup = BeautifulSoup(requests.get(url, headers=headers).text, "lxml")
    data = {}

    for row in soup.find_all("table", class_="snapshot-table2"):
        for i in range(0, len(row.find_all("td")), 2):
            key = row.find_all("td")[i].text
            val = row.find_all("td")[i+1].text
            data[key] = val

    return {
        "Short Float": data.get("Short Float", "N/A"),
        "Insider Own": data.get("Insider Own", "N/A"),
        "Inst Own": data.get("Inst Own", "N/A"),
        "Optionable": data.get("Optionable", "N/A")
    }
