# python
import logging
from typing import Any, Optional
from datetime import datetime
import requests
import nsemine

logger = logging.getLogger(__name__)


DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/91.0.4472.124 Safari/537.36"
    ),
    "Accept": "text/plain, */*; q=0.01",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Referer": "https://www.nseindia.com/",
    "X-Requested-With": "XMLHttpRequest",
}


class NseMineWrapper:
    """
    Wrapper around `nsemine` that maintains a shared requests.Session and
    maps calls to nsemine modules/functions. Attempts to pass `session=...`
    to target functions and falls back to calling without it if not accepted.
    """

    def __init__(self, session: Optional[requests.Session] = None, headers: Optional[dict] = None):
        self.session = session or requests.Session()
        self.session.headers.update(headers or DEFAULT_HEADERS)

    def preflight(self, timeout: int = 10) -> None:
        """Optional preflight GET to NSE homepage to warm cookies/headers."""
        try:
            self.session.get("https://www.nseindia.com", timeout=timeout)
        except requests.RequestException:
            logger.debug("NSE homepage preflight failed or skipped")

    def call(self, module: str, func_name: str, *args: Any, **kwargs: Any) -> Any:
        """
        Generic invoker: look up module in `nsemine`, call function `func_name`.
        Try to provide shared session via kwarg `session`; if target doesn't
        accept it, call without session.
        """
        mod = getattr(nsemine, module, None)
        if mod is None:
            raise AttributeError(f"nsemine has no module '{module}'")

        func = getattr(mod, func_name, None)
        if func is None:
            raise AttributeError(f"nsemine.{module} has no function '{func_name}'")

        # Try passing session first
        try:
            return func(*args, session=self.session, **kwargs)
        except TypeError as e:
            # function likely doesn't accept session; call without session
            logger.debug("Function %s.%s did not accept session kwarg: %s", module, func_name, e)
            return func(*args, **kwargs)

    # Convenience thin wrappers for commonly used nsemine calls.
    def get_eq_masters(self) -> Any:
        return self.call("nse", "get_eq_masters")

    def get_stock_historical_data(self, symbol: str, start: datetime, end: datetime) -> Any:
        return self.call("historical", "get_stock_historical_data", symbol, start, end, 'D')

    def get_live_data(self, symbol: str) -> Any:
        # try common names across nsemine submodules
        for mod in ("live", "nse"):
            try:
                return self.call(mod, "get_live_data", symbol)
            except AttributeError:
                continue
        raise AttributeError("No live data function found in nsemine.live or nsemine.nse")

    def get_fno_data(self, *args: Any, **kwargs: Any) -> Any:
        return self.call("fno", "get_fno_data", *args, **kwargs)


# module-level singleton to import elsewhere
client = NseMineWrapper()
client.preflight()
