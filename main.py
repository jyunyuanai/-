import requests
from bs4 import BeautifulSoup
import time

LINE_CHANNEL_ACCESS_TOKEN = "1RM094zVq4JrDgCEqAh45qACyADriLlIXLpFh46bPKp7rgFOjzaUEu2Mx8qzQYSe8NyjTCIZv8AK+hMiwd5FB2Kt9o4D5++wtYR+fSyAT5oZxEbqZhy3dKTlTEddKVcrBfyxXG+Mst/nOUcJ+j6LPQdB04t89/1O/w1cDnyilFU="

LINE_USER_ID = "Ubbc1a4ef1b30349904e30e3376f30eff"

URLS = [
    "https://www.taiwanbuying.com.tw/Query_AreaAction.ASP",
    "http://www.taiwanbuying.com.tw/Query_AreaAction.ASP",
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

    response = requests.post(
        url,
        headers=headers,
        json=data
    )

    print(response.status_code)
    print(response.text)


def fetch_cases():

    for url in URLS:

        try:

            response = requests.get(
                url,
                timeout=30,
                headers={
                    "User-Agent": "Mozilla/5.0"
                }
            )

            response.encoding = "utf-8"

            soup = BeautifulSoup(
                response.text,
                "html.parser"
            )

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

            return (
                design_cases[:10],
                supervision_cases[:10],
                both_cases[:10]
            )

        except Exception as e:

            print(e)

            time.sleep(5)

    return [], [], []


def build_message(
    design_cases,
    supervision_cases,
    both_cases
):

    message = "今日採購案分類通知\n\n"

    message += "【設計】\n"

    if design_cases:
        message += "\n".join(design_cases)
    else:
        message += "無"

    message += "\n\n【監造】\n"

    if supervision_cases:
        message += "\n".join(supervision_cases)
    else:
        message += "無"

    message += "\n\n【設計加監造】\n"

    if both_cases:
        message += "\n".join(both_cases)
    else:
        message += "無"

    return message


def main():

    design_cases, supervision_cases, both_cases = fetch_cases()

    message = build_message(
        design_cases,
        supervision_cases,
        both_cases
    )

    print(message)

    send_line_message(message)


if __name__ == "__main__":
    main()
