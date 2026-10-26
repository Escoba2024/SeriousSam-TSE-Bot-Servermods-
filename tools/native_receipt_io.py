"""Bounded reads of JSON receipts whose native writer uses truncate+write."""
import json
from pathlib import Path
import time


def read_receipt(path, *, attempts=5, max_bytes=16*1024**2, pause=time.sleep):
    if type(attempts) is not int or not 1<=attempts<=20:
        raise ValueError('bounded receipt attempts required')
    if type(max_bytes) is not int or not 1<=max_bytes<=16*1024**2:
        raise ValueError('bounded receipt size required')
    last=None
    for attempt in range(attempts):
        try:
            with Path(path).open('rb') as stream:raw=stream.read(max_bytes+1)
            if len(raw)>max_bytes:raise ValueError('receipt exceeds size limit')
            value=json.loads(raw)
            if not isinstance(value,dict):raise ValueError('receipt must be a JSON object')
            return value
        except (FileNotFoundError,json.JSONDecodeError) as exc:
            last=exc
            if attempt+1<attempts:pause(0.1)
    raise RuntimeError('native receipt unavailable or incomplete; no fallback state') from last
