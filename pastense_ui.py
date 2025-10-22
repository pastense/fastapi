# pastense_ui.py
from __future__ import annotations

from typing import Optional, Callable, Dict
from pathlib import Path
import json
import contextlib

from nicegui import ui
import httpx

# --------- Default lightweight keystore (file-based, per-user if platformdirs is present) ---------
class KeyStore:
    def __init__(self, app_name: str = "Pastense", org: str = "Parv", filename: str = "keys.json"):
        self.path = self._resolve_path(app_name, org) / filename
        self.path.parent.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _resolve_path(app_name: str, org: str) -> Path:
        # Try to use proper per-OS data dir; fall back to local ./data
        with contextlib.suppress(Exception):
            from platformdirs import user_data_dir  # optional dependency
            print(Path(user_data_dir(app_name,org)))
            return Path(user_data_dir(app_name, org))
        return Path("./data")

    def load(self) -> Dict[str, str]:
        if self.path.exists():
            with contextlib.suppress(Exception):
                return json.loads(self.path.read_text())
        return {}

    def get(self, name: str) -> Optional[str]:
        return self.load().get(name)

    def set(self, name: str, value: str) -> None:
        data = self.load()
        data[name] = value
        self.path.write_text(json.dumps(data, indent=2))

# --------- Public API: call this from main.py ---------
def register_ui(
    app,
    *,
    base_url: str = "http://127.0.0.1:8000",
    get_key: Optional[Callable[[str], Optional[str]]] = None,
    set_key: Optional[Callable[[str, str], None]] = None,
    title: str = "Pastense – Local UI",
):
    """
    Mounts a NiceGUI UI onto an existing FastAPI app.

    Usage (in main.py):
        from pastense_ui import register_ui
        register_ui(app, base_url="http://127.0.0.1:8000")
        # run: uvicorn main:app --reload --port 8000
    """
    # Bind NiceGUI to your existing FastAPI app
    ui.run_with(app)

    # Provide a default keystore if none is injected
    _ks = KeyStore()
    _get = get_key if get_key else _ks.get
    _set = set_key if set_key else _ks.set

    @ui.page("/")  # Home page
    def home():
        ui.markdown(f"# {title}")

        # ----------------- Card 1: API Key Manager -----------------
        with ui.card().style('max-width: 720px'):
            ui.label('API Key Manager')

            service = ui.input('Service name (e.g., openai)').props('outlined')
            key = ui.input('Paste API key').props('type=password outlined')

            def on_save():
                s = (service.value or "").strip()
                v = (key.value or "").strip()
                if not s or not v:
                    ui.notify('Service and key required', color='negative')
                    return
                try:
                    _set(s, v)
                    ui.notify(f'Saved key for "{s}"', color='positive')
                except Exception as e:
                    ui.notify(f'Error saving key: {e}', color='negative')

            def on_load():
                s = (service.value or "").strip()
                if not s:
                    ui.notify('Enter a service name to load', color='warning')
                    return
                try:
                    v = _get(s)
                    if v:
                        key.value = v
                        ui.notify('Loaded existing key', color='positive')
                    else:
                        ui.notify('No key saved for that service', color='warning')
                except Exception as e:
                    ui.notify(f'Error loading key: {e}', color='negative')

            with ui.row():
                ui.button('Save / Update', on_click=on_save)
                ui.button('Load', on_click=on_load)
                ui.button('Clear fields', on_click=lambda: (setattr(service, 'value', ''), setattr(key, 'value', '')))

