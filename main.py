import requests
from bs4 import BeautifulSoup
import pandas as pd
import json

def fetch_etf_data():
    # 修正後的 URL
    url = "https://www.wantgoo.com/etf/discount-premium"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://www.wantgoo.com/"
    }
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"請求失敗，狀態碼：{response.status_code}")
            return None
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 尋找表格，玩股網通常將資料放在 <table> 標籤內
        table = soup.find('table') 
        if not table:
            print("找不到資料表格，可能網站結構已更改")
            return None
            
        # 使用 pandas 讀取該表格 HTML
        df = pd.read_html(str(table))[0]
        
        # 進行基本的資料清理
        # 假設欄位是：['代號', '名稱', '市價', '淨值', '折溢價', ...]
        # 我們只取前五欄
        df = df.iloc[:, :5] 
        df.columns = ['code', 'name', 'price', 'nav', 'ratio']
        
        # 清理 ratio 欄位的 % 符號並轉為數字，方便網頁做顏色判斷
        df['ratio_val'] = df['ratio'].str.replace('%', '').str.replace('+', '').astype(float)
        
        return df

    except Exception as e:
        print(f"發生錯誤: {e}")
        return None

# 執行並儲存
df_result = fetch_etf_data()
if df_result is not None:
    # 轉成 JSON 格式儲存
    result_json = df_result.to_json(orient="records", force_ascii=False)
    with open("etf_data.json", "w", encoding="utf-8") as f:
        f.write(result_json)
    print("資料更新成功！")
