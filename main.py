import requests
import pandas as pd
import json

def fetch_etf_data():
    # Yahoo 奇摩股市的 ETF 折溢價頁面
    url = "https://tw.stock.yahoo.com/rank/etf-premium-discount"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    }
    
    try:
        print("正在從 Yahoo 獲取資料...")
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code != 200:
            print(f"請求失敗！狀態碼：{response.status_code}")
            return None
        
        # Yahoo 的網頁表格通常可以用 pandas 直接讀取
        # 如果 read_html 被擋，我們就改用更底層的解析
        dfs = pd.read_html(response.text)
        
        if not dfs:
            print("找不到表格資料")
            return None
            
        df = dfs[0]
        print(f"成功抓取！共有 {len(df)} 筆資料")

        # Yahoo 表格欄位清理 (依據目前網頁結構：排名, 股票名稱/代號, 市價, 淨值, 折溢價...)
        # 我們提取關鍵欄位
        # 注意：Yahoo 的代號通常跟名稱連在一起，例如 "0050 元大台灣50"
        
        cleaned_data = []
        for index, row in df.iterrows():
            raw_name = str(row.get('名稱', row.iloc[1]))
            # 嘗試拆分代號與名稱 (例如 "0050 元大台灣50")
            parts = raw_name.split(' ')
            code = parts[0] if len(parts) > 0 else "N/A"
            name = parts[1] if len(parts) > 1 else raw_name
            
            cleaned_data.append({
                "code": code,
                "name": name,
                "price": str(row.get('市價', row.iloc[2])),
                "nav": str(row.get('淨值', row.iloc[3])),
                "ratio": str(row.get('折溢價(%)', row.iloc[4]))
            })
            
        return cleaned_data

    except Exception as e:
        print(f"發生異常: {str(e)}")
        return None

if __name__ == "__main__":
    result = fetch_etf_data()
    if result and len(result) > 0:
        with open("etf_data.json", "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=4)
        print("etf_data.json 更新成功！")
    else:
        print("抓取結果為空，請檢查網頁結構是否改變。")
