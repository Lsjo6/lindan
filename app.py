import os
import json
import requests
from flask import Flask, render_template, request, jsonify, send_from_directory

app = Flask(__name__)

# DeepSeek API (国内可直接访问，推荐)
DEEPSEEK_API = "https://api.deepseek.com/v1/chat/completions"
DEEPSEEK_MODEL = "deepseek-chat"

# Anthropic API (需要代理/VPN)
ANTHROPIC_API = "https://api.anthropic.com/v1/messages"
ANTHROPIC_MODEL = "claude-sonnet-4-6-20250514"

DEFAULT_SYSTEM = "你是霖蛋，用户的好朋友和全能助手。用中文回复，语气友好温暖，像朋友聊天一样。回复简洁有用。"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/static/<path:path>")
def static_files(path):
    return send_from_directory("static", path)

@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json()
    api_key = data.get("api_key", "")
    provider = data.get("provider", "deepseek")  # deepseek 或 anthropic
    messages = data.get("messages", [])
    system_prompt = data.get("system", "")

    if not api_key:
        return jsonify({"error": "请先设置 API 密钥"}), 400

    system_text = system_prompt if system_prompt else DEFAULT_SYSTEM

    if provider == "anthropic":
        return _call_anthropic(api_key, messages, system_text)
    else:
        return _call_deepseek(api_key, messages, system_text)


def _call_deepseek(api_key, messages, system_text):
    """调用 DeepSeek API（OpenAI 兼容格式）"""
    # DeepSeek 格式：把 system prompt 作为第一条消息
    ds_messages = [{"role": "system", "content": system_text}]
    for m in messages:
        ds_messages.append({"role": m["role"], "content": m["content"]})

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    body = {
        "model": DEEPSEEK_MODEL,
        "messages": ds_messages,
        "max_tokens": 4096,
        "temperature": 0.7,
    }

    try:
        resp = requests.post(DEEPSEEK_API, headers=headers, json=body, timeout=120)
        if resp.status_code != 200:
            err = resp.json() if resp.text else {"error": {"message": "未知错误"}}
            msg = err.get("error", {}).get("message", str(err))
            return jsonify({"error": f"API 错误 ({resp.status_code}): {msg}"}), resp.status_code

        result = resp.json()
        reply = result["choices"][0]["message"]["content"]
        return jsonify({"reply": reply})

    except requests.exceptions.Timeout:
        return jsonify({"error": "请求超时，请重试"}), 504
    except requests.exceptions.ConnectionError:
        return jsonify({"error": "无法连接 DeepSeek 服务器，请检查网络"}), 502
    except Exception as e:
        return jsonify({"error": f"出错了: {str(e)}"}), 500


def _call_anthropic(api_key, messages, system_text):
    """调用 Anthropic API"""
    anthropic_messages = []
    for m in messages:
        anthropic_messages.append({"role": m["role"], "content": m["content"]})

    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }

    body = {
        "model": ANTHROPIC_MODEL,
        "max_tokens": 4096,
        "messages": anthropic_messages,
        "system": system_text,
    }

    try:
        resp = requests.post(ANTHROPIC_API, headers=headers, json=body, timeout=120)
        if resp.status_code != 200:
            err = resp.json() if resp.text else {"error": {"message": "未知错误"}}
            msg = err.get("error", {}).get("message", str(err))
            return jsonify({"error": f"API 错误 ({resp.status_code}): {msg}"}), resp.status_code

        result = resp.json()
        reply = result["content"][0]["text"]
        return jsonify({"reply": reply})

    except requests.exceptions.Timeout:
        return jsonify({"error": "请求超时，请重试"}), 504
    except requests.exceptions.ConnectionError:
        return jsonify({"error": "无法连接 Anthropic 服务器，你可能需要代理/VPN"}), 502
    except Exception as e:
        return jsonify({"error": f"出错了: {str(e)}"}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
