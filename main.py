import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
import time

def fetch_etf_data():
    # 修正後的網址
    url = "https://www.wantgoo.com/etf/discount-premium"
    
    # 增加更像真人的 Headers
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7",
        "Referer": "https://www.wantgoo.com/",
        "Cache-Control": "max-age=0"
    }
    
    try:
        print("正在請求網頁資料...")
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code != 200:
            print(f"請求失敗！狀態碼：{response.status_code}")
            return None
        
        # 檢查是否被阻擋 (檢查關鍵字)
        if "機器人" in response.text or "Cloudflare" in response.text:
            print("警告：偵測到爬蟲阻擋機制！")
            return None

        # 使用 pandas 直接解析 HTML 表格
        # 玩股網的資料通常在 class 為 'table' 的標籤中
        dfs = pd.read_html(response.text)
        if not dfs:
            print("網頁中找不到任何表格")
            return None
            
        df = dfs[0]
        print(f"成功抓取表格，共有 {len(df)} 筆資料")

        # 資料清理 (請確保欄位名稱與你的 index.html 對應)
        # 欄位通常是：代號、名稱、市價、淨值、折溢價
        df = df.iloc[:, :5]
        df.columns = ['code', 'name', 'price', 'nav', 'ratio']
        
        # 轉成 JSON 格式
        return df.to_dict(orient="records")

    except Exception as e:
        print(f"爬取過程發生異常: {str(e)}")
        return None

if __name__ == "__main__":
    result = fetch_etf_data()
    
    if result:
        with open("etf_data.json", "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=4)
        print("etf_data.json 更新完成")
    else:
        print("本次抓取無資料，不更新檔案。")
        # 這裡可以選擇不寫入空資料，保留舊資料
