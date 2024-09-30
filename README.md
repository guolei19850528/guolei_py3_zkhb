# guolei_py3_zkhb
### a python3 library for zhkb
# Example
```python
from guolei_py3_zkhb.library.pmf import (
    Api, UrlSetting
)
api = Api(base_url="YOUR BASE URL")
actual_charge_list = api.query_actual_charge_list(
    estate_id="<ESTATE ID>",
    types="<TYPES>",
    room_no="<ROOM NO>",
    end_date="<END DATE>"
)
```