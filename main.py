import requests
import yfinance as yf
import feedparser
#from bs4 import BeautifulSoup


def get_thai_gold_price():
    url = 'https://api.chnwt.dev/thai-gold-api/latest' 
    
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        
        if data.get('status') == 'success':
            res = data.get('response', {})
            # โครงสร้างปัจจุบันใช้ 'gold_bar' สำหรับทองคำแท่ง
            price_list = res.get('price', {})
            gold_data = price_list.get('gold_bar', {})
            # print(res)
            # ดึงราคาขาย (sell)
            raw_sell = gold_data.get('sell')
            
            # ตรวจสอบว่ามีค่าส่งมาหรือไม่
            if raw_sell is None:
                print("DEBUG: ไม่พบคีย์ 'sell' ในข้อมูล")
                return None

            # กำจัดเครื่องหมายคอมม่า (,) และแปลงเป็นตัวเลข
            if isinstance(raw_sell, str):
                raw_sell = raw_sell.replace(',', '')
            
            try:
                sell_int = int(float(raw_sell))
            except (ValueError, TypeError):
                print(f"DEBUG: แปลงราคาไม่ได้จากค่า: {raw_sell}")
                sell_int = 0 
            
            date_val = res.get('update_date', '')
            time_val = res.get('update_time', 'Unknown')
            update_str = f"{date_val} {time_val}".strip()

            return {
                "buy": gold_data.get('buy', '0'),
                "sell": sell_int,
                "update": update_str
            }
        else:
            print(f"DEBUG: API status not success -> {data.get('status')}")
            return None
            
    except Exception as e:
        print(f"DEBUG: API Error -> {e}")
        return None

def get_global_market_data():
    tickers = ["GC=F", "THB=X"]
    data = yf.download(tickers, period="1d", interval="1m")
    latest_spot = data['Close']['GC=F'].iloc[-1]
    latest_thb = data['Close']['THB=X'].iloc[-1]
    return latest_spot, latest_thb

def get_gold_news():
    # RSS Feed ข่าวเศรษฐกิจภาษาไทยจาก Google News
    rss_url = 'https://news.google.com/rss/search?q=ราคาทองคำ+เศรษฐกิจ&hl=th&gl=TH&ceid=TH:th'
    feed = feedparser.parse(rss_url)
    news_list = []
    
    # ดึงมา 5 หัวข้อข่าวล่าสุด
    for entry in feed.entries[:5]:
        news_list.append(entry.title)
    return news_list

def analyze_sentiment(news_list):
    score = 0
    # เพิ่มคำเฉพาะเจาะจงของปี 2026 เช่น ภาษีนำเข้า (Tariff), นิวเคลียร์อิหร่าน
    positive_words = [
        'ขึ้น', 'พุ่ง', 'สูงสุด', 'หนุน', 'สงคราม', 'กังวล', 
        'ภาษีนำเข้า', 'อิหร่าน', 'ตึงเครียด', 'ความไม่แน่นอน'
    ]
    negative_words = [
        'ร่วง', 'ดิ่ง', 'ลดลง', 'ต่ำสุด', 'แข็งค่า', 'เทขาย', 
        'ทำกำไร', 'ดอลลาร์แข็ง', 'ลดดอกเบี้ยช้าลง'
    ]

    for news in news_list:
        for word in positive_words:
            if word in news: score += 1
        for word in negative_words:
            if word in news: score -= 1
    return score

def show_summary(price, news, score):
    #print(price)
    print("\n" + "="*50)
    print(f"🌟 สรุปวิเคราะห์การลงทุนทองคำประจำวันที่: {price.get('update')}")
    print("="*50)
    print(f"💰 ราคาทองแท่ง (ขายออก): {price.get('sell')} บาท")
    print("-" * 50)
    print("📰 หัวข้อข่าวที่ส่งผลต่อตลาด:")
    for i, title in enumerate(news, 1):
        print(f"{i}. {title}")
    
    print("-" * 50)
    print(f"ผลวิเคราะห์ทางเทคนิค (Sentiment Score: {score})")
    
    if score > 0:
        print("มุมมอง: [บวก] ข่าวส่วนใหญ่หนุนราคาทอง")
        print("คำแนะนำ: ทยอยสะสม (DCA) หรือถือครองเพื่อเก็งกำไร")
    elif score < 0:
        print("มุมมอง: [ลบ] ข่าวส่งสัญญาณกดดันราคา")
        print("คำแนะนำ: ชะลอการซื้อ รอจังหวะราคาย่อตัวลงมาอีก")
    else:
        print("มุมมอง: [กลาง] ตลาดทรงตัว")
        print("คำแนะนำ: ซื้อสะสมตามแผนปกติ (ถัวเฉลี่ย)")
    print("="*50 + "\n")

def save_to_html(price_info, news, score, recommendation, est_range):
    html_content = f"""
    <!DOCTYPE html>
    <html lang="th">
    <head>
        <meta charset="UTF-8">
        <title>Gold Investment Analysis</title>
        <style>
            body {{ font-family: sans-serif; line-height: 1.6; max-width: 800px; margin: auto; padding: 20px; background: #f4f4f4; }}
            .card {{ background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
            h1 {{ color: #d4af37; }}
            .price {{ font-size: 24px; font-weight: bold; color: #2c3e50; }}
            .recommendation {{ font-size: 20px; padding: 10px; border-radius: 5px; background: #e1f5fe; }}
            li {{ margin-bottom: 10px; }}
        </style>
    </head>
    <body>
        <div class="card">
            <h1>วิเคราะห์ราคาทองคำวันนี้</h1>
            <p class="price">ราคาสมาคมฯ: {price_info['sell']:,} บาท</p>
            <p>อัปเดตเมื่อ: {price_info['update']}</p>
            <hr>
            <h3>📰 ข่าวที่เกี่ยวข้อง</h3>
            <ul>
                {" ".join([f"<li>{n}</li>" for n in news])}
            </ul>
            <hr>
            <div class="recommendation">
                <strong>{recommendation}</strong><br>
                🎯 ช่วงราคาประมาณการ: {est_range} บาท
            </div>
            <p><small>สร้างโดยระบบอัตโนมัติเมื่อ: {price_info['update']}</small></p>
        </div>
    </body>
    </html>
    """
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)

def main():
    print("ระบบกำลังรวบรวมข้อมูลและวิเคราะห์ข่าว... กรุณารอครู่เดียว")
    
    # 1. ดึงข้อมูลราคามาเก็บไว้ก่อน
    price_info = get_thai_gold_price()
    # print(price_info.get('buy'))
    
    # ตรวจสอบว่าดึงข้อมูลสำเร็จและราคาเป็นตัวเลขหรือไม่
    if not price_info or not isinstance(price_info.get('sell'), int):
        print("ไม่สามารถดึงข้อมูลราคาทองมาวิเคราะห์ได้ !!!!!!")
        return

    # --- ประกาศตัวแปรหลักไว้ที่นี่ เพื่อป้องกัน UnboundLocalError ---
    current_sell = price_info.get('sell')
    news = get_gold_news()
    score = analyze_sentiment(news)
    
    # 2. คำนวณคำแนะนำและช่วงราคา
    if score > 0:
        recommendation = "แนะนำ: ทยอยซื้อสะสม (ข่าวหนุนราคา)"
        est_range = f"{current_sell - 100:,} - {current_sell + 300:,}"
    elif score < 0:
        recommendation = "แนะนำ: ชะลอการซื้อ (ข่าวเป็นลบ !!!!!)"
        est_range = f"{current_sell - 300:,} - {current_sell + 100:,}"
    else:
        recommendation = "แนะนำ: ถือครอง/ซื้อถัวเฉลี่ย (ตลาดนิ่ง)"
        est_range = f"{current_sell - 100:,} - {current_sell + 100:,}"

    # 3. แสดงผลและบันทึก HTML
    # ส่งค่าไปแสดงผลที่หน้าจอ Terminal
    show_summary(price_info, news, score)
    
    # ส่งค่าไปบันทึกเป็นไฟล์ index.html
    save_to_html(price_info, news, score, recommendation, est_range)

if __name__ == "__main__":
    main()