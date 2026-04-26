
import os
import datetime
import time
import requests
import google.generativeai as genai

# 用戶的 Amazon 聯盟 ID
AMAZON_STORE_ID = "issac03-20"

# Gemini API 配置
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

# APIFreeLLM 配置
APIFREELLM_KEY = "apf_jiktsnyiqk8p83e6qqez9ovn"
APIFREELLM_URL = "https://apifreellm.com/api/v1/chat"

def get_gemini_completion(prompt):
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Gemini API error: {e}")
        return None

def get_apifreellm_completion(prompt):
    print("正在嘗試使用 APIFreeLLM 作為備援...")
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {APIFREELLM_KEY}"
    }
    data = {
        "message": prompt
    }
    try:
        response = requests.post(APIFREELLM_URL, headers=headers, json=data, timeout=30)
        if response.status_code == 200:
            result = response.json()
            return result.get("response", "").strip()
        elif response.status_code == 429:
            print("APIFreeLLM 速率限制 (40秒一次)，等待中...")
            return None
        else:
            print(f"APIFreeLLM error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"APIFreeLLM connection error: {e}")
        return None

def fetch_trending_deals_v4():
    print("正在採集產品數據並生成智慧文案 (V4 - 雙 API 備援)...")
    base_deals = [
        {
            "title": "Sony WH-1000XM5 Wireless Headphones",
            "url": "https://www.amazon.com/dp/B09HP99W1C",
            "description": "Industry-leading noise cancellation, crystal-clear calls, and exceptional sound quality.",
            "category": "電子產品",
            "discount_percent": 30
        },
        {
            "title": "Instant Pot Duo 7-in-1 Pressure Cooker",
            "url": "https://www.amazon.com/dp/B00FLYWNYQ",
            "description": "Pressure cooker, slow cooker, rice cooker, steamer, sauté, yogurt maker, and warmer.",
            "category": "廚房用品",
            "discount_percent": 30
        },
        {
            "title": "Kindle Paperwhite (16 GB)",
            "url": "https://www.amazon.com/dp/B09TMN58KL",
            "description": "6.8\" display and adjustable warm light, waterproof for reading anywhere.",
            "category": "數位閱讀",
            "discount_percent": 25
        },
        {
            "title": "Apple Watch Series 9 [GPS 41mm]",
            "url": "https://www.amazon.com/dp/B0CHX46Q2Q",
            "description": "Advanced health features, always-on Retina display, and innovative interaction.",
            "category": "穿戴裝置",
            "discount_percent": 18
        },
        {
            "title": "LEGO Star Wars: The Mandalorian Microfighter",
            "url": "https://www.amazon.com/dp/B0BBS3313P",
            "description": "A quick-build LEGO Star Wars Microfighter for kids aged 6 and up.",
            "category": "玩具遊戲",
            "discount_percent": 33
        },
        {
            "title": "Echo Dot (5th Gen, 2022 release)",
            "url": "https://www.amazon.com/dp/B09B8V1BM3",
            "description": "Our best-sounding Echo Dot yet, with Alexa and improved audio experience.",
            "category": "智慧家居",
            "discount_percent": 40
        },
        {
            "title": "Ninja AF101 Air Fryer",
            "url": "https://www.amazon.com/dp/B07FDJMC9Q",
            "description": "4-quart capacity, high gloss finish, programmable for crispier results with less oil.",
            "category": "廚房用品",
            "discount_percent": 35
        },
        {
            "title": "Logitech MX Master 3S Wireless Mouse",
            "url": "https://www.amazon.com/dp/B09HMKMM9G",
            "description": "8K DPI any-surface tracking, quiet clicks, and ergonomic design for productivity.",
            "category": "電腦周邊",
            "discount_percent": 15
        }
    ]

    processed_deals = []
    for deal in base_deals:
        prompt = f"你是一位電商專家。為此 Amazon 產品寫一段中文促銷語句（40字內，含 Emoji）：\n產品：{deal['title']}\n描述：{deal['description']}\n折扣：{deal['discount_percent']}% OFF"
        
        # 嘗試首選 API: Gemini
        smart_desc = get_gemini_completion(prompt)
        
        # 若 Gemini 失敗，嘗試備援 API: APIFreeLLM
        if not smart_desc:
            smart_desc = get_apifreellm_completion(prompt)
            if smart_desc:
                print(f"成功使用 APIFreeLLM 生成文案：{deal['title']}")
                # APIFreeLLM 有 40 秒限制，若成功則稍微等待
                time.sleep(2) 
        
        # 若兩者都失敗，使用預設文案
        if not smart_desc:
            smart_desc = f"🔥 限時爆款！{deal['title']} 現正 {deal['discount_percent']}% OFF！頂級品質，手慢無！🚀"

        deal['smart_description'] = smart_desc

        # 添加聯盟標籤
        separator = "&" if "?" in deal["url"] else "?"
        deal["link"] = f"{deal['url']}{separator}tag={AMAZON_STORE_ID}"
        processed_deals.append(deal)

    return processed_deals

def generate_html(deals):
    print(f"正在生成您的專屬獲利網頁...")
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    html_template = f"""
    <!DOCTYPE html>
    <html lang="zh-Hant">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Issac's Smart Deals - AI 自動化獲利系統</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            body {{ background-color: #f8f9fa; font-family: 'PingFang TC', 'Microsoft JhengHei', sans-serif; }}
            .hero {{ background: linear-gradient(135deg, #1a2a6c, #b21f1f, #fdbb2d); color: white; padding: 100px 0; margin-bottom: 40px; box-shadow: 0 4px 15px rgba(0,0,0,0.2); }}
            .card {{ border: none; border-radius: 20px; transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275); box-shadow: 0 10px 30px rgba(0,0,0,0.05); height: 100%; background: white; }}
            .card:hover {{ transform: translateY(-12px); box-shadow: 0 20px 40px rgba(0,0,0,0.12); }}
            .badge-discount {{ background: #ff4b2b; background: linear-gradient(to right, #ff416c, #ff4b2b); font-size: 0.9rem; padding: 8px 16px; border-radius: 50px; font-weight: bold; }}
            .category-tag {{ color: #6c757d; font-weight: 700; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 1px; }}
            .btn-amazon {{ background: linear-gradient(to right, #f8b500, #fceabb); border: none; color: #0f1111; font-weight: 800; border-radius: 50px; padding: 12px 25px; width: 100%; transition: 0.3s; }}
            .btn-amazon:hover {{ transform: scale(1.05); box-shadow: 0 5px 15px rgba(248, 181, 0, 0.4); }}
            .last-update {{ font-size: 0.85rem; background: rgba(0,0,0,0.2); display: inline-block; padding: 5px 15px; border-radius: 20px; margin-top: 15px; }}
        </style>
    </head>
    <body>
        <div class="hero text-center">
            <div class="container">
                <h1 class="display-3 fw-bold mb-3">💎 Issac's Premium Deals</h1>
                <p class="lead fs-4">Gemini + APIFreeLLM 雙 AI 驅動，為您精選全網最具價值的 Amazon 爆款。</p>
                <div class="last-update">系統即時同步中 | 最後更新: {now}</div>
            </div>
        </div>
        <div class="container mb-5">
            <div class="row g-4">
    """
    
    for deal in deals:
        html_template += f"""
                <div class="col-lg-4 col-md-6">
                    <div class="card p-4">
                        <div class="d-flex justify-content-between align-items-center mb-3">
                            <span class="category-tag">{deal['category']}</span>
                            <span class="badge badge-discount">省 {deal['discount_percent']}%</span>
                        </div>
                        <h3 class="h5 fw-bold mb-3" style="color: #2c3e50;">{deal['title']}</h3>
                        <p class="text-secondary mb-4" style="line-height: 1.6;">{deal['smart_description']}</p>
                        <div class="mt-auto">
                            <a href="{deal['link']}" class="btn btn-amazon" target="_blank">立即獲取折扣 →</a>
                        </div>
                    </div>
                </div>
        """
        
    html_template += """
            </div>
            <div class="text-center mt-5 py-5">
                <p class="text-muted small">© 2026 Issac's AI Income System. <br>作為 Amazon 聯盟夥伴，我們從符合條件的購買中獲取佣金。所有價格以 Amazon 官網為準。</p>
            </div>
        </div>
    </body>
    </html>
    """
    return html_template

if __name__ == "__main__":
    deals = fetch_trending_deals_v4()
    html_content = generate_html(deals)
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    print("成功更新獲利網頁內容 (V4 - 雙 API 備援系統)")
