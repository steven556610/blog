"""
hackmd_sync.py — HackMD 公開筆記同步模組
==========================================
功能：
  - 呼叫 HackMD API v1 拉取個人帳號公開筆記清單
  - 對每篇筆記再拉取完整 Markdown 內容
  - 存入 SQLite（HackMDNote 資料表），支援 upsert
  - 可獨立執行（python hackmd_sync.py）或從 Flask APScheduler 排程呼叫

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


def _get_headers() -> dict:
    if not API_TOKEN:
        raise ValueError("HACKMD_API_TOKEN 未設定，請確認 .env 檔案")
    return {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json",
    }


def fetch_my_notes() -> List[dict]:
    """從 HackMD API 取得個人帳號的所有筆記清單"""
    url = f"{HACKMD_API_BASE}/me/notes"
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


def _parse_ts(ts) -> Optional[datetime]:
    """將 HackMD 時間戳（毫秒 epoch 或 ISO 字串）轉為 datetime"""
    if ts is None:
        return None
    try:
        if isinstance(ts, (int, float)):
            return datetime.fromtimestamp(ts / 1000, tz=timezone.utc).replace(tzinfo=None)
        if isinstance(ts, str):
            return datetime.fromisoformat(ts.replace("Z", "+00:00")).replace(tzinfo=None)
    except Exception:
        pass
    return None


def sync_notes(app=None) -> Tuple[int, int, int]:
    """
    主同步函式。
    - 可直接 import 後呼叫（需傳入 Flask app 以取得 app_context）
    - 或獨立執行（會自行建立 Flask app）
    回傳 (synced_count, skipped_count, error_count)
    """
    # 避免 circular import：在函式內 import
    if app is None:
        # 獨立執行模式：建立 Flask app
        from app import app as flask_app
        _app = flask_app
    else:
        _app = app

    from models import db, HackMDNote

    synced = skipped = errors = 0

    with _app.app_context():
        # 確保資料表存在
        db.create_all()

        try:
            all_notes = fetch_my_notes()
        except Exception as e:
            logger.error(f"[HackMD] 無法取得筆記清單: {e}")
            return 0, 0, 1

        # 只同步公開筆記 (readPermission == "guest")
        public_notes = [n for n in all_notes if n.get("readPermission") == "guest"]
        logger.info(f"[HackMD] 公開筆記: {len(public_notes)} / 全部: {len(all_notes)}")

        for note_meta in public_notes:
            hackmd_id = note_meta.get("id") or note_meta.get("shortId", "")
            if not hackmd_id:
                errors += 1
                continue

            try:
                # 取得完整內容
                content = fetch_note_content(hackmd_id)

                # 準備欄位
                title = note_meta.get("title") or "Untitled"
                tags_raw = note_meta.get("tags", [])
                tags_json = json.dumps(tags_raw, ensure_ascii=False)

                short_id     = note_meta.get("shortId", "")
                permalink    = note_meta.get("permalink", "")
                user_path    = note_meta.get("userPath", "")
                publish_link = note_meta.get("publishLink", "")
                if not publish_link and user_path and short_id:
                    publish_link = f"https://hackmd.io/@{user_path}/{short_id}"

                created_at = _parse_ts(note_meta.get("createdAt"))
                updated_at = _parse_ts(
                    note_meta.get("lastChangedAt") or note_meta.get("updatedAt")
                )

                # Upsert：找到就更新，找不到就新增
                existing = HackMDNote.query.filter_by(hackmd_id=hackmd_id).first()

                if existing:
                    # 只有內容有更動時才更新
                    if existing.hackmd_updated_at != updated_at or existing.content != content:
                        existing.title            = title
                        existing.tags             = tags_json
                        existing.content          = content
                        existing.permalink        = permalink
                        existing.publish_link     = publish_link
                        existing.read_permission  = note_meta.get("readPermission", "guest")
                        existing.write_permission = note_meta.get("writePermission", "owner")
                        existing.hackmd_created_at = created_at
                        existing.hackmd_updated_at = updated_at
                        existing.synced_at        = datetime.utcnow()
                        synced += 1
                        logger.info(f"[HackMD] 更新: {title}")
                    else:
                        skipped += 1
                        logger.debug(f"[HackMD] 無變動，跳過: {title}")
                else:
                    new_note = HackMDNote(
                        hackmd_id        = hackmd_id,
                        short_id         = short_id,
                        title            = title,
                        tags             = tags_json,
                        content          = content,
                        permalink        = permalink,
                        publish_link     = publish_link,
                        read_permission  = note_meta.get("readPermission", "guest"),
                        write_permission = note_meta.get("writePermission", "owner"),
                        hackmd_created_at = created_at,
                        hackmd_updated_at = updated_at,
                        synced_at        = datetime.utcnow(),
                    )
                    db.session.add(new_note)
                    synced += 1
                    logger.info(f"[HackMD] 新增: {title}")

            except Exception as e:
                logger.error(f"[HackMD] 處理筆記 {hackmd_id} 時錯誤: {e}")
                errors += 1
                db.session.rollback()
                continue

        try:
            db.session.commit()
        except Exception as e:
            logger.error(f"[HackMD] Commit 失敗: {e}")
            db.session.rollback()
            return 0, 0, 1

    logger.info(f"[HackMD] 同步完成 — 新增/更新: {synced}, 跳過: {skipped}, 錯誤: {errors}")
    return synced, skipped, errors


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s"
    )
    synced, skipped, errors = sync_notes()
    print(f"\n同步結果：新增/更新 {synced} 篇 | 跳過 {skipped} 篇 | 錯誤 {errors} 篇")
