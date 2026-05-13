import requests
from bs4 import BeautifulSoup

# LINE Channel Access Token
LINE_CHANNEL_ACCESS_TOKEN = "1RM094zVq4JrDgCEqAh45qACyADriLlIXLpFh46bPKp7rgFOjzaUEu2Mx8qzQYSe8NyjTCIZv8AK+hMiwd5FB2Kt9o4D5++wtYR+fSyAT5oZxEbqZhy3dKTlTEddKVcrBfyxXG+Mst/nOUcJ+j6LPQdB04t89/1O/w1cDnyilFU="

# 先暫時填 test
LINE_USER_ID = "test"

URL = "https://www.taiwanbuying.com.tw/Query_AreaAction.ASP"

def fetch_cases():

    response = requests.get(URL)
    response.encoding = "utf-8"

    soup = BeautifulSoup(response.text, "html.parser")

    text = soup.get_text("\n")

    design_cases = []
    supervision_cases = []
    both_cases = []

    for line in text.splitlines():

        line = line.strip()

        if not line:
            continue

        # 設計 + 監造
        if (
            "設計監造" in line
            or "設計及監造" in line
            or "設計與監造" in line
        ):
            both_cases.append(line)

        # 只有監造
        elif "監造" in line:
            supervision_cases.append(line)

        # 只有設計
        elif "設計" in line:
            design_cases.append(line)

    return design_cases[:10], supervision_cases[:10], both_cases[:10]


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
                "text": message
            }
        ]
    }

    response = requests.post(
        url,
        headers=headers,
        json=data
    )

    print(response.text)


def build_message(design, supervision, both):

    msg = "今日採購案分類通知\n\n"

    msg += "【設計】\n"

    if design:
        for item in design:
            msg += f"- {item}\n"
    else:
        msg += "無\n"

    msg += "\n【監造】\n"

    if supervision:
        for item in supervision:
            msg += f"- {item}\n"
    else:
        msg += "無\n"

    msg += "\n【設計加監造】\n"

    if both:
        for item in both:
            msg += f"- {item}\n"
    else:
        msg += "無\n"

    return msg


def main():

    design, supervision, both = fetch_cases()

    message = build_message(
        design,
        supervision,
        both
    )

    print(message)

    send_line_message(message)


if __name__ == "__main__":
    main()
