import requests
from bs4 import BeautifulSoup
import time

LINE_CHANNEL_ACCESS_TOKEN = "貼你的 LINE Channel access token"
LINE_USER_ID = "Ubbc1a4ef1b30349904e30e3376f30eff"

URLS = [
    "https://www.taiwanbuying.com.tw/Query_AreaAction.ASP",
    "http://www.taiwanbuying.com.tw/Query_AreaAction.ASP",
    "https://taiwanbuying.com.tw/Query_AreaAction.ASP",
    "http://taiwanbuying.com.tw/Query_AreaAction.ASP",
]

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


def fetch_cases():
    last_error = ""

    for url in URLS:
        for attempt in range(3):
            try:
                print(f"嘗試連線：{url}，第 {attempt + 1} 次")

                response = requests.get(
                    url,
                    timeout=30,
                    headers={
                        "User-Agent": "Mozilla/5.0"
                    }
                )

                response.encoding = "utf-8"

                if response.status_code == 200:
                    return parse_cases(response.text), None

                last_error = f"{url} 狀態碼：{response.status_code}"

            except Exception as error:
                last_error = str(error)
                print(last_error)
                time.sleep(5)

    return None, last_error


def parse_cases(html):
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text("\n")

    design_cases = []
    supervision_cases = []
    both_cases = []

    for line in text.splitlines():
        line = line.strip()

        if not line:
            continue

        if "設計" in line and "監造" in line:
            both_cases.append(line)
        elif "監造" in line:
            supervision_cases.append(line)
        elif "設計" in line:
            design_cases.append(line)

    return design_cases[:10], supervision_cases[:10], both_cases[:10]


def build_message(design_cases, supervision_cases, both_cases):
    message = "今日採購案分類通知\n\n"

    message += "【1. 設計】\n"
    if design_cases:
        for i, case in enumerate(design_cases, 1):
            message += f"{i}. {case}\n"
    else:
        message += "無\n"

    message += "\n【2. 監造】\n"
    if supervision_cases:
        for i, case in enumerate(supervision_cases, 1):
            message += f"{i}. {case}\n"
    else:
        message += "無\n"

    message += "\n【3. 設計加監造】\n"
    if both_cases:
        for i, case in enumerate(both_cases, 1):
            message += f"{i}. {case}\n"
    else:
        message += "無\n"

    return message


def main():
    cases, error = fetch_cases()

    if error:
        message = (
            "採購網爬蟲執行失敗\n\n"
            "原因：GitHub 暫時連不上台灣採購公報網。\n\n"
            f"錯誤內容：{error}"
        )
    else:
        design_cases, supervision_cases, both_cases = cases
        message = build_message(design_cases, supervision_cases, both_cases)

    print(message)
    send_line_message(message)


if __name__ == "__main__":
    main()
