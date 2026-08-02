import os
import re
import json
import requests
from config import BOT_TOKEN, ADMIN_ID
 
TEXT_FILE = "message.txt"
JSON_FILE = "message.json"

# ---------- helpers ----------

def read_text(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read().strip()

def read_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def normalize_chat_target(raw: str):
    """
    Accepts:
      - https://t.me/telepostone
      - t.me/telepostone
      - @telepostone
      - telepostone
      - -1003523821626
      - 123456789
    Returns:
      int (for numeric IDs) or '@username'
    """
    s = (raw or "").strip()

    # Extract username from URL
    m = re.search(r"(?:https?://)?(?:t\.me|telegram\.me)/([A-Za-z0-9_]+)", s)
    if m:
        return "@" + m.group(1)

    # @username
    if s.startswith("@"):
        name = re.sub(r"[^A-Za-z0-9_]", "", s[1:])
        return "@" + name if name else s

    # Numeric chat ID
    if re.fullmatch(r"-?\d+", s):
        return int(s)

    # Bare username
    name = re.sub(r"[^A-Za-z0-9_]", "", s)
    return "@" + name if name else s


# ---------- BUTTON BUILDER (STACKED) ----------

def build_reply_markup(cfg):
    if not cfg.get("buttons_enable", False):
        return None

    try:
        count = int(cfg.get("button_count", 0))
    except Exception:
        return None

    if count <= 0:
        return None

    buttons = cfg.get("buttons", [])
    if not isinstance(buttons, list):
        return None

    buttons = buttons[:count]
    if not buttons:
        return None

    # One button per row (stacked)
    keyboard = []
    for b in buttons:
        keyboard.append([b])

    return {"inline_keyboard": keyboard}


# ---------- TELEGRAM SEND ----------

def tg_send_message(chat_id, caption, cfg):
    """
    Sends a message with optional media to chat_id using configuration in cfg.

    cfg keys used:
      - photo_enable (bool): whether to send an image/animation/document (default True)
      - photo (str): path to media file (default "image.jpg")
      - force_document (bool): if True, use sendDocument (uploads original file)
      - send_as_animation (bool): if True, use sendAnimation regardless of extension
      - has_spoiler (bool): included only when sending as photo (sendPhoto)
      - parse_mode (str): HTML/Markdown etc. (default "HTML")
      - protect_content (bool): if True, prevents forwarding/saving
      - buttons_enable, button_count, buttons: used by build_reply_markup
    """
    parse_mode = cfg.get("parse_mode", "HTML")
    reply_markup = build_reply_markup(cfg)

    def apply_common_flags(data: dict):
        # protect_content is supported in sendMessage/sendPhoto/sendDocument/sendAnimation
        if cfg.get("protect_content") is True:
            data["protect_content"] = True

    def _post(url, data, files=None, timeout=30):
        try:
            r = requests.post(url, data=data, files=files, timeout=timeout)
        except requests.RequestException as e:
            return False, {"error": "request_exception", "detail": str(e)}
        try:
            resp = r.json()
        except Exception:
            return False, {"error": "Invalid Telegram response", "status_code": getattr(r, "status_code", None)}
        ok = r.status_code == 200 and resp.get("ok") is True
        return ok, resp

    if cfg.get("photo_enable", True):
        media_path = cfg.get("photo", "image.jpg")

        if not os.path.exists(media_path):
            return False, {"error": f"Media file not found: {media_path}"}

        _, ext = os.path.splitext(media_path)
        ext = ext.lower()

        # Option to always upload as document (keeps original file & metadata)
        if cfg.get("force_document", False):
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
            data = {
                "chat_id": chat_id,
                "caption": caption,
                "parse_mode": parse_mode,
            }
            apply_common_flags(data)

            if reply_markup:
                data["reply_markup"] = json.dumps(reply_markup)

            with open(media_path, "rb") as f:
                return _post(url, data, files={"document": f})

        # If GIF or explicitly set to send as animation -> sendAnimation
        if ext == ".gif" or cfg.get("send_as_animation", False):
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendAnimation"
            data = {
                "chat_id": chat_id,
                "caption": caption,
                "parse_mode": parse_mode,
            }
            apply_common_flags(data)

            if reply_markup:
                data["reply_markup"] = json.dumps(reply_markup)

            with open(media_path, "rb") as f:
                return _post(url, data, files={"animation": f})

        # Default: send as photo
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
        data = {
            "chat_id": chat_id,
            "caption": caption,
            "parse_mode": parse_mode,
        }
        apply_common_flags(data)

        # has_spoiler is supported for photos
        if cfg.get("has_spoiler") is True:
            data["has_spoiler"] = True

        if reply_markup:
            data["reply_markup"] = json.dumps(reply_markup)

        with open(media_path, "rb") as img:
            return _post(url, data, files={"photo": img})

    # If no media, send plain text message
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": chat_id,
        "text": caption,
        "parse_mode": parse_mode,
    }
    apply_common_flags(data)

    if reply_markup:
        data["reply_markup"] = json.dumps(reply_markup)

    return _post(url, data)


# ---------- ERROR EXPLAIN ----------

def explain_common_errors(resp):
    """
    Prints human-friendly tips based on Telegram response dict.
    """
    if not isinstance(resp, dict):
        print("\nUnexpected response:", resp)
        return

    code = resp.get("error_code")
    desc = str(resp.get("description", "")).lower()

    if code == 403:
        print("\nFix (403 Forbidden):")
        print("- Bot must be added to the group/channel")
        print("- For channels, bot must be ADMIN with 'Post Messages' permission")

    elif code == 400 and "chat not found" in desc:
        print("\nFix (chat not found):")
        print("- Username may be wrong or changed")
        print("- Private channels require numeric -100... ID")
        print("- Bot must be a member of the target chat")

    elif code == 400 and "file is too big" in desc:
        print("\nFix (file is too big):")
        print("- Telegram enforces upload limits for bots. Try reducing file size.")
        print("- Convert GIF to MP4 (video) and send as animation, or host externally.")

    else:
        if desc:
            print(f"\nTelegram error ({code}): {resp.get('description')}")


# ---------- MAIN ----------

def main():
    caption = ""
    cfg = {}
    try:
        caption = read_text(TEXT_FILE)
    except Exception as e:
        print(f"Warning: could not read {TEXT_FILE}: {e}")

    try:
        cfg = read_json(JSON_FILE)
    except Exception as e:
        print(f"Warning: could not read {JSON_FILE}: {e}")

    raw_target = input("Enter target (URL / @username / username / chat_id): ").strip()
    target = normalize_chat_target(raw_target)

    # Admin preview
    print("Sending preview to admin...")
    ok, resp = tg_send_message(ADMIN_ID, caption, cfg)

    if not ok:
        print("Admin preview failed:", resp)
        explain_common_errors(resp)
        return

    print("Admin preview delivered.")

    confirm = input('Type "Y" to send to target: ').strip().upper()
    if confirm != "Y":
        print("Cancelled.")
        return

    print(f"Posting to: {target}")
    ok, resp = tg_send_message(target, caption, cfg)

    if ok:
        print("Post successful.")
    else:
        print("Post failed:", resp)
        explain_common_errors(resp)


if __name__ == "__main__":
    main()

