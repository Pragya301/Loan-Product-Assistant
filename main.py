import pandas as pd
import requests
from bs4 import BeautifulSoup

url = "https://bankofmaharashtra.bank.in/gold-loan"

r = requests.get(url)
print(r)

soup = BeautifulSoup(r.text, "lxml")
print(soup.prettify().encode("utf-8", "ignore").decode())

