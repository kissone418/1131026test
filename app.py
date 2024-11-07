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
        # 抓取網頁資料
        response = req.get(url, headers=headers)
        response.raise_for_status()  # 檢查請求是否成功
        html = response.text
        r = BeautifulSoup(html, 'html.parser')

        # 解析書籍資訊
        title = r.find("title").text
        meta_data = r.find_all("meta")
        meta_text = str(meta_data[3]) if len(meta_data) > 3 else ""
        meta_parts = meta_text.split("，")
        author = next((s[3:] for s in meta_parts if "作者：" in s), "無資料")
        publisher = next((s[4:] for s in meta_parts if "出版社：" in s), "無資料")
        isbn = next((s[5:] for s in meta_parts if "ISBN：" in s), "無資料")
        price = r.find("em").string or "無資料"

        # 準備寫入 CSV 的資料
        csv_filename = "book_data.csv"
        write_header = not os.path.exists(csv_filename)  # 檢查是否需要寫入表頭

        # 計算流水號（如果 CSV 已存在，根據行數計算）
        serial_number = 1
        if os.path.exists(csv_filename):
            with open(csv_filename, mode='r', encoding='utf-8-sig') as csvfile:
                reader = csv.reader(csvfile)
                serial_number = sum(1 for row in reader)  # 包含表頭行

        # 寫入 CSV 檔案，使用帶有 BOM 的 UTF-8 編碼
        with open(csv_filename, mode='a', encoding='utf-8-sig', newline='') as csvfile:
            writer = csv.writer(csvfile)
            # 如果檔案是新建的，則寫入表頭
            if write_header:
                writer.writerow(["流水號", "書名", "作者", "出版社", "", "ISBN", "", "定價"])
            # 寫入查詢結果，符合指定格式
            writer.writerow([serial_number, title, author, publisher, "", isbn, "", price])

        return jsonify({
            "title": title,
            "author": author,
            "publisher": publisher,
            "isbn": isbn,
            "price": price
        })
    except Exception as e:
        return jsonify({"error": "查詢失敗", "details": str(e)})

@app.route('/download_csv')
def download_csv():
    # 提供 CSV 檔案下載
    csv_filename = "book_data.csv"
    if os.path.exists(csv_filename):
        return send_file(csv_filename, as_attachment=True, mimetype='text/csv', download_name="book_data.csv")
    else:
        return "CSV 檔案不存在", 404

if __name__ == '__main__':
    app.run(debug=True)
