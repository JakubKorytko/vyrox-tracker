"""Fetch vyrox match data from Toornament (used in GitHub Actions)."""
import datetime
import json
import pathlib
import urllib.request

PARTICIPANT_ID = "2600325438708242431"
BASE = "https://play.toornament.com/api/matches"


def fetch(query: str) -> dict:
    url = f"{BASE}?{query}"
    req = urllib.request.Request(url, headers={"User-Agent": "vyrox-tracker-action/1.0"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.load(resp)


def main() -> None:
    upcoming = fetch(
        f"participant_ids={PARTICIPANT_ID}"
        "&statuses=pending,running&sort=scheduled_asc&limit=5"
    )
    completed = fetch(
        f"participant_ids={PARTICIPANT_ID}"
        "&statuses=completed&sort=latest_results&limit=12"
    )
    payload = {
        "updatedAt": datetime.datetime.now(datetime.timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z"),
        "participantId": PARTICIPANT_ID,
        "upcoming": upcoming,
        "completed": completed,
    }
    out = pathlib.Path(__file__).resolve().parents[1] / "data" / "live.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Wrote {out} ({payload['updatedAt']})")


if __name__ == "__main__":
    main()
