import datetime as dt


MAX_NUM_PIGMENTS = 2400
BASE_URL = f"https://www.kremer-pigmente.com/en/pigments/?f=19&sPage=1&sPerPage={MAX_NUM_PIGMENTS:d}"

CACHE_EXPIRE_AFTER = dt.timedelta(days=200)
