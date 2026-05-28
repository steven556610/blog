"""
hackmd_sync.py — HackMD 公開筆記同步模組 (JSON 靜態匯出版)
==========================================
功能：
  - 呼叫 HackMD API v1 拉取個人帳號公開筆記清單
  - 對每篇筆記再拉取完整 Markdown 內容
  - 將結果存成 JSON 檔案 (hackmd_notes.json) 供 Flask 讀取
  - 獨立執行（python hackmd_sync.py）

公開筆記定義：readPermission == "guest"
"""

import os
import json
import logging
from datetime import datetime, timezone
from typing import Optional, List, Tuple

import requests as http_requests
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

HACKMD_API_BASE = "https://api.hackmd.io/v1"
API_TOKEN = os.getenv("HACKMD_API_TOKEN") or os.getenv("HACKMD_API_KEY", "")
JSON_OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "hackmd_notes.json")

def _get_headers() -> dict:
    if not API_TOKEN:
        raise ValueError("HACKMD_API_TOKEN 未設定，請確認 .env 檔案")
    return {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json",
    }

def fetch_my_notes() -> List[dict]:
    """從 HackMD API 取得個人帳號的所有筆記清單"""
    url = f"{HACKMD_API_BASE}/notes"
    resp = http_requests.get(url, headers=_get_headers(), timeout=15)
    resp.raise_for_status()
    notes = resp.json()
    logger.info(f"[HackMD] 取得 {len(notes)} 篇筆記")
    return notes

def fetch_note_content(note_id: str) -> Optional[str]:
    """取得單篇筆記的 Markdown 完整內容"""
    url = f"{HACKMD_API_BASE}/notes/{note_id}"
    try:
        resp = http_requests.get(url, headers=_get_headers(), timeout=15)
        resp.raise_for_status()
        data = resp.json()
        return data.get("content", "")
    except Exception as e:
        logger.warning(f"[HackMD] 無法取得筆記 {note_id} 內容: {e}")
        return None

def _parse_ts_to_iso(ts) -> str:
    """將 HackMD 時間戳轉為 ISO 格式字串"""
    if ts is None:
        return ""
    try:
        if isinstance(ts, (int, float)):
            dt = datetime.fromtimestamp(ts / 1000, tz=timezone.utc).replace(tzinfo=None)
            return dt.isoformat()
        if isinstance(ts, str):
            dt = datetime.fromisoformat(ts.replace("Z", "+00:00")).replace(tzinfo=None)
            return dt.isoformat()
    except Exception:
        pass
    return ""

def sync_notes() -> Tuple[int, int, int]:
    """
    主同步函式 (匯出為 JSON)
    """
    synced = skipped = errors = 0
    
    # 讀取現有資料
    existing_notes = {}
    if os.path.exists(JSON_OUTPUT_PATH):
        try:
            with open(JSON_OUTPUT_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                for n in data.get("notes", []):
                    existing_notes[n["hackmd_id"]] = n
        except Exception as e:
            logger.warning(f"無法讀取舊有 JSON 紀錄，將重新建立: {e}")

    try:
        all_notes = fetch_my_notes()
    except Exception as e:
        logger.error(f"[HackMD] 無法取得筆記清單: {e}")
        return 0, 0, 1

    # 只同步公開筆記
    public_notes = [n for n in all_notes if n.get("readPermission") == "guest"]
    logger.info(f"[HackMD] 公開筆記: {len(public_notes)} / 全部: {len(all_notes)}")

    new_notes_data = []

    for note_meta in public_notes:
        hackmd_id = note_meta.get("id") or note_meta.get("shortId", "")
        if not hackmd_id:
            errors += 1
            continue

        try:
            title = note_meta.get("title") or "Untitled"
            tags_raw = note_meta.get("tags", [])
            short_id     = note_meta.get("shortId", "")
            permalink    = note_meta.get("permalink", "")
            user_path    = note_meta.get("userPath", "")
            publish_link = note_meta.get("publishLink", "")
            if not publish_link and user_path and short_id:
                publish_link = f"https://hackmd.io/@{user_path}/{short_id}"

            created_at = _parse_ts_to_iso(note_meta.get("createdAt"))
            updated_at = _parse_ts_to_iso(note_meta.get("lastChangedAt") or note_meta.get("updatedAt"))

            existing = existing_notes.get(hackmd_id)
            
            # 判斷是否需要重新拉取內容
            if existing and existing.get("hackmd_updated_at") == updated_at and existing.get("content"):
                logger.debug(f"[HackMD] 無變動，跳過: {title}")
                new_notes_data.append(existing)
                skipped += 1
            else:
                content = fetch_note_content(hackmd_id)
                new_note = {
                    "hackmd_id": hackmd_id,
                    "short_id": short_id,
                    "title": title,
                    "tags": tags_raw,
                    "content": content,
                    "permalink": permalink,
                    "publish_link": publish_link,
                    "read_permission": note_meta.get("readPermission", "guest"),
                    "write_permission": note_meta.get("writePermission", "owner"),
                    "hackmd_created_at": created_at,
                    "hackmd_updated_at": updated_at,
                    "synced_at": datetime.utcnow().isoformat()
                }
                new_notes_data.append(new_note)
                synced += 1
                logger.info(f"[HackMD] 新增/更新: {title}")

        except Exception as e:
            logger.error(f"[HackMD] 處理筆記 {hackmd_id} 時錯誤: {e}")
            errors += 1
            continue

    # 依照更新時間排序 (最新在前)
    new_notes_data.sort(key=lambda x: x.get("hackmd_updated_at", ""), reverse=True)

    # 寫入 JSON
    output_data = {
        "last_synced": datetime.utcnow().isoformat(),
        "total_notes": len(new_notes_data),
        "notes": new_notes_data
    }
    
    try:
        with open(JSON_OUTPUT_PATH, "w", encoding="utf-8") as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"[HackMD] 寫入 JSON 失敗: {e}")
        return synced, skipped, 1

    logger.info(f"[HackMD] 同步完成 — 新增/更新: {synced}, 跳過: {skipped}, 錯誤: {errors}")
    return synced, skipped, errors


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s"
    )
    synced, skipped, errors = sync_notes()
    print(f"\n同步結果：新增/更新 {synced} 篇 | 跳過 {skipped} 篇 | 錯誤 {errors} 篇")
