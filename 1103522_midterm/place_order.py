import requests
import json
import base64
import time
import nacl.signing

# 🔐 請替換為你的 Base64 編碼的公鑰與私鑰（請妥善保管私鑰）
API_KEY = "G1AQkTUGmNLS/1fllTMgi9KC/kb1KT8ZCEb5fHCNN3E="
API_SECRET = os.getenv("API_SECRET")

BASE_URL = "https://api.backpack.exchange"

def generate_signature(instruction, params):
    # 取得目前毫秒時間戳
    timestamp = str(int(time.time() * 1000))
    window = "5000"

    # 1. 轉換參數為 key=value 形式並排序
    param_str = "&".join(f"{key}={params[key]}" for key in sorted(params.keys()))

    # 2. 構造 prehash 字串
    prehash = f"instruction={instruction}&{param_str}&timestamp={timestamp}&window={window}"
    print(f"🔐 prehash: {prehash}")

    # 3. 使用 ED25519 私鑰簽名 prehash
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
    print(f"📨 回應內容: {response.text}")

if __name__ == "__main__":
    place_market_order()
