
import logging
from typing import List, Optional, Union
import requests
from pathlib import Path


def does_contain(name: str, stopw: List[str]):
    for w in stopw:
        if name.find(w) >= 0:
            return True
    return False


class PageGetter:
    _log: logging.Logger = logging.getLogger("PageGetter")
    session: requests.Session
    session_used: bool
    use_cache: bool
    cache_path: Path
    url_session_init: str
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36",
        'Accept-Language': 'it-IT, it;q=0.5',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'it-IT,it;q=0.9,en-US;q=0.8,en;q=0.7',
        'cache-control': 'max-age=0',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36'
    }

    
    def __init__(self, url_session_init: str, headers: Optional[dict] = None, use_cache: bool = False, cache_path: Union[str, Path] = "cache"):
        # create session
        self.session = requests.Session()
        # add default headers
        for key, val in self.headers.items():
            self.session.headers[key] = val
        # add custom headers
        if headers is not None:
            for key, val in headers.items():
                self.session.headers[key] = val
        # not used yet
        self.session_used = False
        self.use_cache = use_cache
        self.cache_path = Path(cache_path)
        self.url_session_init = url_session_init
        
    def get_page(self, url: str, cache_filename: str, use_cache: Optional[bool] = None,
                 method: str = "get", **kwargs):
        use_cache = use_cache if use_cache is not None else self.use_cache
        self.cache_path.mkdir(exist_ok=True)
        cache_file = self.cache_path / cache_filename
        if not cache_file.exists() or not use_cache:
            if not self.session_used:
                self._log.debug(f"Initializing session ({self.url_session_init})")
                req = self.session.get(self.url_session_init)
                req.raise_for_status()
                self.session_used = True

            # req = self.session.get(url)
            req = self.session.request(method, url, **kwargs)
            req.raise_for_status()

            with cache_file.open("wb") as fp:
                fp.write(req.content)
            content = req.content
        else:
            self._log.info(f"Reading cached '{cache_filename}'")
            with cache_file.open("rb") as fp:
                content = fp.read()
        return content
