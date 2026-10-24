"""
Wayback Machine client for link monuments.
Uses the availability API: https://archive.org/wayback/available?url=...
"""

import logging
import httpx

logger = logging.getLogger(__name__)

WAYBACK_AVAILABILITY_URL = "https://archive.org/wayback/available"


async def check_wayback(url: str) -> dict:
    """
    Query the Wayback Machine for the closest archived snapshot of a URL.

    Returns:
        {
            "archived": bool,
            "last_seen": "YYYYMMDDHHMMSS" | None,
            "snapshot_url": str | None,
            "status": str | None,  # HTTP status of the archived page
        }
    """
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            r = await client.get(
                WAYBACK_AVAILABILITY_URL,
                params={"url": url},
            )
            r.raise_for_status()
            data = r.json()

        snapshot = data.get("archived_snapshots", {}).get("closest")
        if snapshot and snapshot.get("available"):
            return {
                "archived": True,
                "last_seen": snapshot.get("timestamp"),
                "snapshot_url": snapshot.get("url"),
                "status": snapshot.get("status"),
            }
        return {"archived": False, "last_seen": None, "snapshot_url": None, "status": None}

    except httpx.TimeoutException:
        logger.warning(f"Wayback Machine timeout for URL: {url}")
        return {"archived": False, "last_seen": None, "snapshot_url": None, "status": "timeout"}
    except Exception as e:
        logger.warning(f"Wayback Machine error for URL {url}: {e}")
        return {"archived": False, "last_seen": None, "snapshot_url": None, "status": "error"}


def format_wayback_date(timestamp: str | None) -> str | None:
    """Convert Wayback timestamp (YYYYMMDDHHMMSS) to human-readable format."""
    if not timestamp or len(timestamp) < 8:
        return timestamp
    try:
        year = timestamp[0:4]
        month = timestamp[4:6]
        day = timestamp[6:8]
        return f"{year}-{month}-{day}"
    except Exception:
        return timestamp
