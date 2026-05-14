import requests
from bs4 import BeautifulSoup
from urllib.parse import quote
import time

LINE_CHANNEL_ACCESS_TOKEN = "1RM094zVq4JrDgCEqAh45qACyADriLlIXLpFh46bPKp7rgFOjzaUEu2Mx8qzQYSe8NyjTCIZv8AK+hMiwd5FB2Kt9o4D5++wtYR+fSyAT5oZxEbqZhy3dKTlTEddKVcrBfyxXG+Mst/nOUcJ+j6LPQdB04t89/1O/w1cDnyilFU="
LINE_USER_ID = "Ubbc1a4ef1b30349904e30e3376f30eff"

BASE_URL = "https://www.taiwanbuying.com.tw/Query_KeywordAction.ASP"

KEYWORDS = {
    "設計": "設計",
    "監造": "監造",
    "設計加監造": "設計監造"
}

def send_line_message(message):
    url = "https://api.line.me/v2/bot/message/push"

    headers = {
        "Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    data = {
        "to": LINE_USER_ID,
        "messages": [
            {
                "type": "text",
                "text": message[:4900]
            }
        ]
    }

    response = requests.post(url, headers=headers, json=data, timeout=20)
    print(response.status_code)
    print(response.text)


def get_html_by_keyword(keyword):
    encoded_keyword = quote(keyword)

    urls = [
        f"{BASE_URL}?keyword={encoded_keyword}",
        f"{BASE_URL}?KeyWord={encoded_keyword}",
        f"{BASE_URL}?KEYWORD={encoded_keyword}",
        f"{BASE_URL}?SearchKeyword={encoded_keyword}",
    ]

    last_error = ""

    for url in urls:
        try:
            print(f"查詢網址：{url}")

            response = requests.get(
                url,
                timeout=30,
                headers={
                    "User-Agent": "Mozilla/5.0"
                }
            )

            response.encoding = "utf-8"

            if response.status_code == 200:
                return response.text

            last_error = f"HTTP {response.status_code}"

        except Exception as e:
            last_error = str(e)
            print(last_error)
            time.sleep(3)

    print(f"{keyword} 查詢失敗：{last_error}")
    return ""


def parse_cases(html, keyword):
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text("\n")

    cases = []

    for line in text.splitlines():
        line = line.strip()

        if not line:
            continue

        if not line[0].isdigit():
            continue

        if ":" not in line and "：" not in line:
            continue

        if keyword in line:
            cases.append(line)

    return cases[:10]


def build_message(results):
    message = "今日採購案關鍵字查詢通知\n\n"

    for category, cases in results.items():
        message += f"【{category}】\n"

        if cases:
            for case in cases:
                message += f"{case}\n"
        else:
            message += "無\n"

        message += "\n"

    return message


def main():
    results = {}

    for category, keyword in KEYWORDS.items():
        html = get_html_by_keyword(keyword)

        if not html:
            results[category] = []
            continue

        cases = parse_cases(html, keyword)
        results[category] = cases

    message = build_message(results)

    print(message)
    send_line_message(message)


if __name__ == "__main__":
    main()
