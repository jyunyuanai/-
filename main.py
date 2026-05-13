import requests
from bs4 import BeautifulSoup

LINE_CHANNEL_ACCESS_TOKEN = "貼你的 LINE Channel access token"
LINE_USER_ID = "Ubbc1a4ef1b30349904e30e3376f30eff"

URL = "https://www.taiwanbuying.com.tw/Query_AreaAction.ASP"

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
    try:
        response = requests.get(URL, timeout=30)
        response.encoding = "utf-8"
    except Exception as error:
        return None, None, None, str(error)

    soup = BeautifulSoup(response.text, "html.parser")
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

    return design_cases[:10], supervision_cases[:10], both_cases[:10], None


def build_message(design_cases, supervision_cases, both_cases):
    message = "今日採購案分類通知\n\n"

    message += "【1. 設計】\n"
    message += "\n".join(f"{i}. {case}" for i, case in enumerate(design_cases, 1)) if design_cases else "無"
    message += "\n\n【2. 監造】\n"
    message += "\n".join(f"{i}. {case}" for i, case in enumerate(supervision_cases, 1)) if supervision_cases else "無"
    message += "\n\n【3. 設計加監造】\n"
    message += "\n".join(f"{i}. {case}" for i, case in enumerate(both_cases, 1)) if both_cases else "無"

    return message


def main():
    design_cases, supervision_cases, both_cases, error = fetch_cases()

    if error:
        message = (
            "採購網爬蟲執行失敗\n\n"
            "原因：暫時連不上台灣採購公報網。\n\n"
            f"錯誤內容：{error}"
        )
    else:
        message = build_message(design_cases, supervision_cases, both_cases)

    print(message)
    send_line_message(message)


if __name__ == "__main__":
    main()
