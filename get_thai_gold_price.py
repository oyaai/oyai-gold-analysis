import requests
import requests
import yfinance as yf

from bs4 import BeautifulSoup


def get_thai_gold_price():
    url = 'https://www.goldtraders.or.th/'
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    
    response = requests.get(url, headers=headers)
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, 'html.parser')

    # ค้นหา Element ที่เก็บราคาทองคำแท่ง (อ้างอิงจาก ID ของเว็บสมาคมฯ)
    gold_bar_buy = soup.find(id='DetailPlace_uc_goldprices1_lblBLBuy').text
    gold_bar_sell = soup.find(id='DetailPlace_uc_goldprices1_lblBLSell').text
    update_time = soup.find(id='DetailPlace_uc_goldprices1_lblAsTime').text

    return {
        "buy": gold_bar_buy,
        "sell": gold_bar_sell,
        "update": update_time
    }

thai_gold = get_thai_gold_price()
print(f"ราคาทองคำแท่งไทย (รับซื้อ): {thai_gold['buy']} บาท")
print(f"ราคาทองคำแท่งไทย (ขายออก): {thai_gold['sell']} บาท")
print(f"อัปเดตเมื่อ: {thai_gold['update']}")