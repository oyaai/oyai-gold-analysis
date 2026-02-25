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
    
    spot_series = data['Close']['GC=F'].dropna()
    if not spot_series.empty:
        latest_spot = spot_series.iloc[-1]
    else:
        backup_data = yf.Ticker("GC=F").history(period="1d")
        latest_spot = backup_data['Close'].iloc[-1]

    thb_series = data['Close']['THB=X'].dropna()
    if not thb_series.empty:
        latest_thb = thb_series.iloc[-1]
    else:
        backup_thb = yf.Ticker("THB=X").history(period="1d")
        latest_thb = backup_thb['Close'].iloc[-1]
        
    return float(latest_spot), float(latest_thb)

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
    # ดึงข้อมูล Spot และ THB มาโชว์ประกอบการตัดสินใจ
    try:
        spot_price, thb_rate = get_global_market_data()
        spot_str = f"{spot_price:,.2f}"
        thb_str = f"{thb_rate:,.2f}"
    except:
        spot_str, thb_str = "N/A", "N/A"

    current_sell = price_info['sell']
    
    # คำนวณจุดชี้วัด
    is_buy_zone = "✅ พร้อมเข้าซื้อ" if (spot_price >= 5170 if isinstance(spot_price, float) else False) else "⚠️ ชะลอการซื้อ"

    html_content = f"""
    <!DOCTYPE html>
    <html lang="th">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Gold Day Trading Cockpit</title>
        <style>
            body {{ font-family: 'Inter', sans-serif; background: #0f172a; color: #f8fafc; max-width: 1000px; margin: auto; padding: 20px; }}
            .container {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }}
            .card {{ background: #1e293b; padding: 20px; border-radius: 12px; border: 1px solid #334155; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1); }}
            .full-width {{ grid-column: span 2; }}
            h1, h2, h3 {{ color: #fbbf24; margin-top: 0; }}
            .price-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin-bottom: 20px; }}
            .price-item {{ background: #334155; padding: 15px; border-radius: 8px; text-align: center; }}
            .label {{ font-size: 12px; color: #94a3b8; text-transform: uppercase; }}
            .value {{ font-size: 24px; font-weight: bold; color: #f1f5f9; }}
            .session-box {{ border-left: 4px solid #fbbf24; padding-left: 15px; margin-bottom: 15px; }}
            .session-time {{ font-weight: bold; color: #fbbf24; }}
            .status-badge {{ display: inline-block; padding: 5px 15px; border-radius: 20px; background: #065f46; color: #34d399; font-weight: bold; }}
            .warning {{ background: #7f1d1d; color: #fca5a5; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
            th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #334155; }}
            @media (max-width: 768px) {{ .container {{ grid-template-columns: 1fr; }} .full-width {{ grid-column: span 1; }} }}
        </style>
    </head>
    <body>
        <h1> Gold Day Trading Dashboard</h1>
        
        <div class="container">
            <div class="card full-width">
                <div class="price-grid">
                    <div class="price-item">
                        <div class="label">Gold Spot ($)</div>
                        <div class="value">${spot_str}</div>
                    </div>
                    <div class="price-item">
                        <div class="label">ค่าเงินบาท (USD/THB)</div>
                        <div class="value">{thb_str}</div>
                    </div>
                    <div class="price-item">
                        <div class="label">ทองแท่งสมาคม (บาท)</div>
                        <div class="value">{current_sell:,}</div>
                    </div>
                </div>
                <div style="text-align: center;">
                    <span class="status-badge {'warning' if 'ชะลอ' in is_buy_zone else ''}">
                        สถานะปัจจุบัน: {is_buy_zone} (เงื่อนไข $5,170)
                    </span>
                </div>
            </div>

            <div class="card">
                <h2>ตารางเทรดรายวัน</h2>
                <div class="session-box">
                    <div class="session-time">ช่วงเช้า (09:00 - 10:00)</div>
                    <div>เฝ้าราคาเปิดสมาคมฯ หาก Spot < $5,180 <b>"ชะลอการซื้อ"</b></div>
                </div>
                <div class="session-box">
                    <div class="session-time">ช่วงบ่าย (14:00 - 16:00)</div>
                    <div>ติดตามข่าวฝั่งยุโรป หากดอลลาร์ (DXY) แข็งค่า ทองจะถูกกดดัน</div>
                </div>
                <div class="session-box" style="border-left-color: #ef4444;">
                    <div class="session-time">ช่วงค่ำ (20:30 เป็นต้นไป) </div>
                    <div><b>ตลาดสหรัฐฯ เปิด:</b> ช่วงวิ่งแรงที่สุด ติดตามข่าว Kevin Warsh และภาษีนำเข้าทรัมป์</div>
                </div>
            </div>

            <div class="card">
                <h2> สรุปกลยุทธ์วันนี้</h2>
                <p><b>มุมมอง:</b> {recommendation}</p>
                <p><b>เป้าหมาย:</b> {est_range} บาท</p>
                <hr style="border: 0; border-top: 1px solid #334155;">
                <h3> จุดเข้า-ออก สำคัญ</h3>
                <table>
                    <tr style="color: #f87171;"><td>แนวต้านสำคัญ</td><td>{current_sell + 300:,}</td></tr>
                    <tr style="color: #fbbf24;"><td>ราคาปัจจุบัน</td><td>{current_sell:,}</td></tr>
                    <tr style="color: #4ade80;"><td>แนวรับไม้ที่ 1</td><td>{current_sell - 150:,}</td></tr>
                    <tr style="color: #4ade80;"><td>แนวรับไม้ที่ 2</td><td>{current_sell - 400:,}</td></tr>
                </table>
            </div>

            <div class="card full-width">
                <h3> หัวข้อข่าวเด่นที่มีผลต่อราคา</h3>
                <ul>
                    {" ".join([f"<li>{n}</li>" for n in news])}
                </ul>
                <p style="font-size: 11px; color: #64748b; text-align: right;">อัปเดตอัตโนมัติเมื่อ: {price_info['update']}</p>
            </div>
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