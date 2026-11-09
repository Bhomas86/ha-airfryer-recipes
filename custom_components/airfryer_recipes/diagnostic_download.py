"""Short-lived, user-bound diagnostic preview snapshots; never persisted."""
from copy import deepcopy
import json
import secrets
import time

from .const import DOMAIN
from .recipe_repository import RecipePreviewExpiredError

DIAGNOSTIC_FILENAME = "airfryer-recipes-diagnostics.json"
DIAGNOSTIC_URL = f"/api/{DOMAIN}/diagnostics"
PREVIEW_SECONDS = 600


class DiagnosticDownloads:
    def __init__(self):
        self.snapshots = {}

    def create(self, uid, snapshot):
        now = time.monotonic()
        self.snapshots = {k: v for k, v in self.snapshots.items() if v[0] != uid and v[1] > now}
        if len(self.snapshots) >= 128:
            raise OSError("Diagnostic preview capacity reached")
        token = secrets.token_urlsafe(24)
        # Callers supply only the backend's allowlisted diagnostic result.
        payload = json.dumps(deepcopy(snapshot), ensure_ascii=False, indent=2).encode("utf-8")
        self.snapshots[token] = (uid, now + PREVIEW_SECONDS, payload)
        return token

    def read(self, uid, token):
        if not isinstance(token, str) or not 0 < len(token) <= 128:
            raise RecipePreviewExpiredError
        snapshot = self.snapshots.get(token)
        if snapshot is None or snapshot[0] != uid or snapshot[1] <= time.monotonic():
            raise RecipePreviewExpiredError
        return snapshot[2]


def previews(hass):
    state = hass.data[DOMAIN]
    if "diagnostic_downloads" not in state:
        state["diagnostic_downloads"] = DiagnosticDownloads()
    return state["diagnostic_downloads"]
