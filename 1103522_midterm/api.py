import requests
import time
import base64
import nacl.signing
from datetime import datetime
import pytz
import csv
import json

# 🔐 請替換為你的 Base64 編碼的公鑰與私鑰（請妥善保管私鑰）
API_KEY = "G1AQkTUGmNLS/1fllTMgi9KC/kb1KT8ZCEb5fHCNN3E="
API_SECRET = "BYGeJrNk8KFx8dk9xXku45tZU6ntiV0Ryguc9TqyQ8A="

BASE_URL = "https://api.backpack.exchange"

def generate_signature(instruction, params):
    timestamp = str(int(time.time() * 1000))
    window = "5000"

    param_str = "&".join(f"{key}={params[key]}" for key in sorted(params.keys()))
    prehash = f"instruction={instruction}&{param_str}&timestamp={timestamp}&window={window}"
    print(f"🔐 prehash: {prehash}")

    private_key = base64.b64decode(API_SECRET)
    signing_key = nacl.signing.SigningKey(private_key)
    signed = signing_key.sign(prehash.encode("utf-8"))
    signature = base64.b64encode(signed.signature).decode("utf-8")

    print(f"🖋️ signature: {signature}")
    return timestamp, window, signature
def place_market_order():
    path = "/api/v1/order"
    url = BASE_URL + path
    instruction = "orderExecute"

    # 💰 下單參數（市價買入 $5 USDC 的 BTC）
    order_body = {
        "symbol": "BTC_USDC",
        "side": "Bid",
        "orderType": "Market",
        "quoteQuantity": "6"
    }

    # 生成簽名
    timestamp, window, signature = generate_signature(instruction, order_body)

    # 請求 Header
    headers = {
        "X-API-Key": API_KEY,
        "X-Timestamp": timestamp,
        "X-Window": window,
        "X-Signature": signature,
        "Content-Type": "application/json"
    }

    # 發送 POST 請求
    response = requests.post(url, headers=headers, data=json.dumps(order_body))

    # 顯示回應
    print(f"📬 狀態碼: {response.status_code}")
    print(f"📨 回應內容＊＊＊＊＊＊＊＊＊＊＊＊＊＊: {response.text}")

def get_fill_history():
    url = BASE_URL + "/wapi/v1/history/fills"
    params = {
        "symbol": "BTC_USDC",
        "limit": 3,
        "timestamp": str(int(time.time() * 1000)),
        "window": "5000"
    }

    timestamp, window, signature = generate_signature("fillHistoryQueryAll", params)

    headers = {
        "X-API-Key": API_KEY,
        "X-Timestamp": timestamp,
        "X-Window": window,
        "X-Signature": signature
    }

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        fills = response.json()
        print("📋 BTC 成交紀錄：")

        # 開啟 CSV 檔案並寫入欄位名稱
        with open("api.csv", mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["交易時間", "成交價格", "成交數量", "手續費", "幣別", "方向"])

            for fill in fills:
                utc_time = datetime.strptime(fill["timestamp"], "%Y-%m-%dT%H:%M:%S.%f")
                utc_time = utc_time.replace(tzinfo=pytz.utc)
                local_time = utc_time.astimezone(pytz.timezone("Asia/Taipei"))

                print(f"交易時間: {local_time}")
                print(f"交易手續費: {fill['fee']} {fill['feeSymbol']}")
                print(f"買入/賣出: {fill['side']}")
                print(f"成交數量: {fill['quantity']}")
                print(f"成交價格: {fill['price']}")
                print("-" * 50)

                # 寫入 CSV 一列資料
                writer.writerow([
                    local_time,
                    fill["price"],
                    fill["quantity"],
                    fill["fee"],
                    fill["feeSymbol"],
                    fill["side"]
                ])
        print("✅ 資料已成功寫入 api.csv")
    else:
        print(f"⚠️ 查詢失敗: {response.text}")

if __name__ == "__main__":
    place_market_order()
    get_fill_history()
