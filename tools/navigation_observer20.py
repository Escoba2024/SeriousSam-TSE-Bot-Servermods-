"""Stage only the pinned own observer script, inside its sealed transaction."""
import hashlib
from pathlib import Path

EXPECTED_PATH=Path('/srv/tse-arena-isolated-20261111/vanilla/Scripts/CecilObserver.ini')
BEFORE_SHA256='9152b8cf7bb1f8bdf569427b17881311d754c41504c0c07ca41cc68837c6fd5d'


def transform(raw):
 if hashlib.sha256(raw).hexdigest()!=BEFORE_SHA256:raise ValueError('exact original observer script required')
 for name in (b'sam_iMaxFPSActive',b'sam_iMaxFPSInactive'):
  before=name+b'=30;'
  if raw.count(before)!=1:raise ValueError('exact original FPS assignment required')
  raw=raw.replace(before,name+b'=20;',1)
 return raw


def stage(path):
 path=Path(path)
 if path.is_symlink()or path.resolve()!=EXPECTED_PATH:raise ValueError('own observer script only')
 before=path.read_bytes();after=transform(before)
 path.write_bytes(after)
 if path.read_bytes()!=after:raise ValueError('staged observer script differs')
 return dict(before_sha256=hashlib.sha256(before).hexdigest(),after_sha256=hashlib.sha256(after).hexdigest(),fps=20,
  scope='COMMON_OWN_ORIGINAL_RENDER_CONFIG_ONLY_NOT_ACTUAL_FPS_MEASUREMENT',retail_binary_changed=False)
