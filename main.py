const LINE_CHANNEL_ACCESS_TOKEN = "1RM094zVq4JrDgCEqAh45qACyADriLlIXLpFh46bPKp7rgFOjzaUEu2Mx8qzQYSe8NyjTCIZv8AK+hMiwd5FB2Kt9o4D5++wtYR+fSyAT5oZxEbqZhy3dKTlTEddKVcrBfyxXG+Mst/nOUcJ+j6LPQdB04t89/1O/w1cDnyilFU=";
const TAIWANBUYING_URL = "https://www.taiwanbuying.com.tw/Query_AreaAction.ASP";

function doPost(e) {
  const body = JSON.parse(e.postData.contents);
  const event = body.events[0];

  if (!event || event.type !== "message" || event.message.type !== "text") {
    return ContentService.createTextOutput("OK");
  }

  const replyToken = event.replyToken;
  const userText = event.message.text.trim();

  let message = "";

  if (userText === "設計") {
    message = buildCategoryMessage("設計");
  } else if (userText === "監造") {
    message = buildCategoryMessage("監造");
  } else if (userText === "設計監造" || userText === "設計加監造") {
    message = buildCategoryMessage("設計監造");
  } else if (userText === "今日採購" || userText === "查詢") {
    message = buildAllMessage();
  } else {
    message = "請輸入：\n設計\n監造\n設計監造\n今日採購";
  }

  replyMessage(replyToken, message);
  return ContentService.createTextOutput("OK");
}

function buildCategoryMessage(category) {
  const cases = fetchCases();
  let list = [];

  if (category === "設計") {
    list = cases.design;
  } else if (category === "監造") {
    list = cases.supervision;
  } else if (category === "設計監造") {
    list = cases.both;
  }

  let message = "今日【" + category + "】標案\n\n";

  if (list.length === 0) {
    message += "目前沒有找到符合的標案。";
  } else {
    list.slice(0, 10).forEach(function(item, index) {
      message += (index + 1) + ". " + item + "\n\n";
    });
  }

  return message;
}

function buildAllMessage() {
  const cases = fetchCases();

  let message = "今日採購案分類通知\n\n";

  message += "【設計】\n";
  message += cases.design.length ? cases.design.slice(0, 5).join("\n") : "無";

  message += "\n\n【監造】\n";
  message += cases.supervision.length ? cases.supervision.slice(0, 5).join("\n") : "無";

  message += "\n\n【設計監造】\n";
  message += cases.both.length ? cases.both.slice(0, 5).join("\n") : "無";

  return message;
}

function fetchCases() {
  const response = UrlFetchApp.fetch(TAIWANBUYING_URL, {
    method: "get",
    muteHttpExceptions: true,
    headers: {
      "User-Agent": "Mozilla/5.0"
    }
  });

  const html = response.getContentText("UTF-8");
  const text = html
    .replace(/<br\s*\/?>/gi, "\n")
    .replace(/<\/tr>/gi, "\n")
    .replace(/<\/td>/gi, " ")
    .replace(/<[^>]+>/g, "\n")
    .replace(/&nbsp;/g, " ")
    .replace(/&quot;/g, "\"")
    .replace(/&amp;/g, "&");

  const lines = text.split("\n").map(function(line) {
    return line.trim();
  }).filter(function(line) {
    return line.length > 0;
  });

  const design = [];
  const supervision = [];
  const both = [];

  lines.forEach(function(line) {
    if (!/^\d+\./.test(line)) return;
    if (line.indexOf(":") === -1 && line.indexOf("：") === -1) return;

    if (line.indexOf("設計") !== -1 && line.indexOf("監造") !== -1) {
      both.push(line);
    } else if (line.indexOf("監造") !== -1) {
      supervision.push(line);
    } else if (line.indexOf("設計") !== -1) {
      design.push(line);
    }
  });

  return {
    design: design,
    supervision: supervision,
    both: both
  };
}

function replyMessage(replyToken, text) {
  const url = "https://api.line.me/v2/bot/message/reply";

  const payload = {
    replyToken: replyToken,
    messages: [
      {
        type: "text",
        text: text.substring(0, 4900)
      }
    ]
  };

  UrlFetchApp.fetch(url, {
    method: "post",
    contentType: "application/json",
    headers: {
      Authorization: "Bearer " + LINE_CHANNEL_ACCESS_TOKEN
    },
    payload: JSON.stringify(payload),
    muteHttpExceptions: true
  });
}
