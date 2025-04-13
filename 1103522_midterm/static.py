import requests
from bs4 import BeautifulSoup
import json
import re
import csv
from datetime import datetime  # 加入時間模組

# 目標網站 URL
url = "https://backpack.exchange/"

# 發送 GET 請求取得 HTML
response = requests.get(url)

# 用 BeautifulSoup 解析 HTML
soup = BeautifulSoup(response.text, "html.parser")

# 用來儲存幣種與價格的結果
coins = []

# 取得現在的時間（ISO 格式），例如：2025-04-07T12:34:56
timestamp = datetime.now().isoformat()

# 從所有 <script> 標籤中搜尋可能包含 JSON 的內容
for script in soup.find_all("script"):
    text = script.string
    if not text:
        continue

    # 抓出可能的 JSON 陣列格式
    matches = re.findall(r'\[\{.*?\}\]', text, re.DOTALL)

    for match in matches:
        try:
            data = json.loads(match)
            for item in data:
                symbol = item.get("symbol") or item.get("marketName")
                price = item.get("lastPrice") or item.get("price")

                if symbol and price:
                    coins.append({
                        "symbol": symbol,
                        "price": price,
                        "timestamp": timestamp  # 加入當下時間
                    })
        except:
            continue

# 儲存為 JSON
with open("static.json", "w", encoding="utf-8") as f:
    json.dump(coins, f, ensure_ascii=False, indent=2)

# 儲存為 CSV
with open("static.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["symbol", "price", "timestamp"])
    writer.writeheader()
    writer.writerows(coins)

# 結果輸出提示
print(f"共擷取 {len(coins)} 筆幣種資料，已儲存為 static.json 與 static.csv")
