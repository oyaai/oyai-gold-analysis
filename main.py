import requests
import yfinance as yf
import feedparser
#import datetime
import feedparser
#from bs4 import BeautifulSoup

def get_thai_gold_price():
    url = 'https://api.chnwt.dev/thai-gold-api/latest' 
    
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        
        if data.get('status') == 'success':
            res = data.get('response', {})
            
            price_list = res.get('price', {})
            gold_data = price_list.get('gold_bar', {})
            # print(res)
            
            raw_sell = gold_data.get('sell')
            
            if raw_sell is None:
                print("DEBUG: ไม่พบคีย์ 'sell' ในข้อมูล")
                return None

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

def get_realtime_news():
    url = "https://www.investing.com/rss/news_95.rss" # ตัวอย่าง Feed ข่าวทองคำ
    feed = feedparser.parse(url)
    
    news_items = []
    # เอาแค่ 5 ข่าวล่าสุดที่สดใหม่จริงๆ
    for entry in feed.entries[:5]:
        news_items.append(entry.title)
    
    return news_items

def get_short_trade_plan(spot_price, pivots):
    if not pivots: return "รอยืนยันสัญญาณ"
    
    p = pivots['p']
    r1 = pivots['r1']
    s1 = pivots['s1']
    
    # วิเคราะห์หน้าเทรดสั้น (Short Trade Plan)
    if spot_price > p:
        plan = "📈 **หน้า Buy ได้เปรียบ**: เน้นย่อซื้อที่แนวรับแรก เพื่อไปขายที่แนวต้าน"
    elif spot_price < p:
        plan = "📉 **หน้า Sell ได้เปรียบ**: ราคายังอยู่ใต้จุดหมุน เน้นขายเมื่อเด้งทดสอบแนวต้าน"
    else:
        plan = "⏳ **Wait & See**: ราคาอยู่ที่จุดหมุน (Pivot) รอเลือกทาง"
        
    return plan

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

def get_pivot_levels():
    try:
        gold = yf.Ticker("GC=F")
        hist = gold.history(period="5d") # ดึงเผื่อไว้กรณีติดวันหยุด
        
        if len(hist) < 2:
            return None

        # ดึงค่า High, Low, Close ของเมื่อวาน (แถวก่อนหน้าล่าสุด)
        # ใช้ .item() เพื่อดึงเอาเฉพาะค่าตัวเลขออกมาจาก Series
        high = float(hist['High'].iloc[-2])
        low = float(hist['Low'].iloc[-2])
        close = float(hist['Close'].iloc[-2])
        
        # สูตร Pivot Point Standard
        pivot = (high + low + close) / 3
        r1 = (2 * pivot) - low
        r2 = pivot + (high - low)
        s1 = (2 * pivot) - high
        s2 = pivot - (high - low)
        
        return {
            "p": pivot, "r1": r1, "r2": r2, "s1": s1, "s2": s2
        }
    except Exception as e:
        print(f"DEBUG Pivot Error: {e}")
        return None

def save_to_html(price_info, news, score, recommendation, est_range):
    # 1. เตรียมข้อมูลพื้นฐาน
    spot_price, thb_rate = get_global_market_data()
    pivots = get_pivot_levels()
    current_sell = price_info['sell']

    # ฟังก์ชันแปลงราคา: คำนวณส่วนต่างจาก Pivot Point เทียบกับ Spot ปัจจุบัน
    # แล้วนำส่วนต่างนั้นมาบวก/ลบจากราคาทองไทยปัจจุบัน
    def to_thai_rel(target_spot):
        if not target_spot or not spot_price or spot_price == 0:
            return current_sell
        
        # คำนวณว่า target_spot ต่างจาก spot ปัจจุบันกี่ %
        diff_percent = (target_spot - spot_price) / spot_price
        # นำ % นั้นมาปรับกับราคาทองไทย
        thai_price = current_sell * (1 + diff_percent)
        # ปัดเศษให้ลงท้ายด้วย 10 หรือ 50 ตามสไตล์ราคาสมาคมฯ
        return int(round(thai_price / 50) * 50)

    if pivots:
        res2_val = f"{to_thai_rel(pivots['r2']):,}"
        res1_val = f"{to_thai_rel(pivots['r1']):,}"
        sup1_val = f"{to_thai_rel(pivots['s1']):,}"
        sup2_val = f"{to_thai_rel(pivots['s2']):,}"
    else:
        # กรณีไม่มีข้อมูล ให้ใช้ค่าประมาณการจากราคาปัจจุบัน
        res2_val, res1_val = f"{current_sell+500:,}", f"{current_sell+200:,}"
        sup1_val, sup2_val = f"{current_sell-150:,}", f"{current_sell-450:,}"
    
    # 2. Logic ช่วงเวลา (now_hour)
    import datetime
    now_utc = datetime.datetime.now(datetime.timezone.utc)
    now_hour = (now_utc.hour + 7) % 24
    
    condition_price = 5180 if 9 <= now_hour < 12 else 5170
    time_tag = "ช่วงเช้า ($5,180)" if 9 <= now_hour < 12 else "กลยุทธ์ปัจจุบัน ($5,170)"
    
    # 3. เตรียมตัวแปรสำหรับแสดงผล
    is_buy = spot_price >= condition_price
    buy_status = "✅ พร้อมเข้าซื้อ" if is_buy else "⚠️ ชะลอการซื้อ"
    badge_class = "" if is_buy else "warning"

    short_plan = get_short_trade_plan(spot_price, pivots)
    real_news = get_realtime_news()
    
    # 4. อ่านไฟล์ Template
    with open("template.html", "r", encoding="utf-8") as f:
        html_content = f.read()

    # 5. แทนที่ตัวแปรใน HTML (ใช้ชื่อที่เราตั้งไว้ในปีกกา { })
    # ข้อควรระวัง: หากใน HTML มีปีกกาปกติของ CSS ให้ใช้ {{ }} เพื่อไม่ให้ Python งง
    final_html = html_content.replace("{SPOT_PRICE}", f"{spot_price:,.2f}")\
                             .replace("{THB_RATE}", f"{thb_rate:,.2f}")\
                             .replace("{PRICE_SELL}", f"{price_info['sell']:,}")\
                             .replace("{RES2}", res2_val)\
                             .replace("{RES1}", res1_val)\
                             .replace("{SUP1}", sup1_val)\
                             .replace("{SUP2}", sup2_val)\
                             .replace("{TIME_TAG}", time_tag)\
                             .replace("{BUY_STATUS}", buy_status)\
                             .replace("{BADGE_CLASS}", badge_class)\
                             .replace("{UPDATE_TIME}", price_info['update'])\
                             .replace("{SHORT_PLAN}", short_plan)\
                             .replace("{NEWS_LIST}", "".join([f"<li>{n}</li>" for n in news]))

    # 6. บันทึกเป็น index.html
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(final_html)

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