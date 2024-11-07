from flask import Flask, request, jsonify, render_template, send_file
import requests as req
from bs4 import BeautifulSoup
import csv
import os

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')  # 確保 index.html 位於 templates 資料夾

@app.route('/fetch_book_data')
def fetch_book_data():
    url = request.args.get('url')
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36"
    }
    try:
        response = req.get(url, headers=headers)
        response.raise_for_status()  # 檢查請求是否成功
        html = response.text
        r = BeautifulSoup(html, 'html.parser')

        # 解析書籍資訊
        title = r.find("title").text if r.find("title") else "無資料"
        meta_data = r.find_all("meta")
        meta_text = str(meta_data[3]) if len(meta_data) > 3 else ""
        meta_parts = meta_text.split("，")
        author = next((s[3:] for s in meta_parts if "作者：" in s), "無資料")

        # 返回 JSON 格式的查詢結果
        data = {
            "title": title,
            "author": author,
            "publisher": "無資料",  # 若有其他網頁資料可以解析則可加入
            "isbn": "無資料",
            "price": "無資料"
        }
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)})

# 啟動應用程式
if __name__ == '__main__':
    app.run(debug=True)
