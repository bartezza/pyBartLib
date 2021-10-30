
from bartlib import init_logging, PageGetter


if __name__ == "__main__":
    init_logging()
    
    url_session_init = "https://www.amazon.it"
    use_cache = True
    pg = PageGetter(url_session_init=url_session_init, headers=None,
                    use_cache=use_cache, cache_path="cache")

    url = "https://www.amazon.it/dp/B078211KBB"
    params = {}
    ret = pg.get_page(url=url, cache_filename="test.htm", use_cache=use_cache,
                      method="get", params=params)
    
    print(f"Size = {len(ret)}")
