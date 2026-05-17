from saq.types import SettingsDict

from app.bg_jobs import hooks
from app.core.containers import AppContainer

settings: SettingsDict = {  # type: ignore[type-arg]
    'queue': AppContainer.saq_queue.resolve_sync(),
    'functions': (),
    'cron_jobs': (),
    'startup': hooks.startup,
    'shutdown': hooks.shutdown,
}
