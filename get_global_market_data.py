import yfinance as yf

def get_global_market_data():
    # GC=F คือ Ticker ของ Gold Futures (ใช้แทน Spot Gold ได้แม่นยำที่สุด)
    # THB=X คือ อัตราแลกเปลี่ยน USD/THB
    tickers = ["GC=F", "THB=X"]
    data = yf.download(tickers, period="1d", interval="1m") # ดึงข้อมูลล่าสุดแบบรายนาที
    
    latest_spot = data['Close']['GC=F'].iloc[-1]
    latest_thb = data['Close']['THB=X'].iloc[-1]
    
    return latest_spot, latest_thb

spot_price, thb_rate = get_global_market_data()
print(f"Spot Gold: {spot_price:.2f} USD/oz")
print(f"ค่าเงินบาท: {thb_rate:.2f} THB/USD")