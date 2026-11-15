"""Explicit tree -> fresh archive -> fresh tree; no retirement or deletion API.

Linux only. Caller supplies a quiescent, exclusively owned tree and owns capacity,
locks and external backup verification. Unsupported metadata/sparse detection fails.
"""
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import stat
import tarfile

CHUNK = 128 * 1024
MAX_MANIFEST = 32 * 1024 * 1024
MAX_RECORDS = 65536
FLAGS = os.O_RDONLY | os.O_NOFOLLOW | os.O_NOATIME | os.O_NONBLOCK


def _path(value):
    p = Path(value).absolute()
    if p != p.resolve(strict=False) or '.git' in p.parts:
        raise ValueError('symlink/alias/.git path')
    return p


def _attrs(fd):
    return {n: os.getxattr(fd, n).hex() for n in sorted(os.listxattr(fd))}


def _identity(st):
    return (st.st_dev, st.st_ino, st.st_mode, st.st_uid, st.st_gid, st.st_size,
            st.st_nlink, st.st_atime_ns, st.st_mtime_ns, st.st_ctime_ns)


def _hash(fd):
    os.lseek(fd, 0, os.SEEK_SET)
    h = hashlib.sha256()
    while True:
        b = os.read(fd, CHUNK)
        if not b:
            return h.hexdigest()
        h.update(b)


def _record(fd, name):
    s = os.fstat(fd)
    directory = stat.S_ISDIR(s.st_mode)
    if not directory and (not stat.S_ISREG(s.st_mode) or s.st_nlink != 1):
        raise ValueError('not a single-link regular file or directory')
    a = _attrs(fd)
    r = dict(path=name, kind='directory' if directory else 'file',
             uid=s.st_uid, gid=s.st_gid, mode=stat.S_IMODE(s.st_mode),
             atime_ns=s.st_atime_ns, mtime_ns=s.st_mtime_ns, xattrs=a)
    if not directory:
        if s.st_size and os.lseek(fd, 0, os.SEEK_HOLE) != s.st_size:
            raise ValueError('sparse file')
        r.update(size=s.st_size, sha256=_hash(fd))
    if _identity(s) != _identity(os.fstat(fd)) or a != _attrs(fd):
        raise ValueError('source changed during read')
    return r


def inventory(exact_root):
    """Hash bytes and exact reconstructible metadata without updating access times."""
    root = _path(exact_root)
    records = []
    def walk(fd, name, depth):
        if depth > 64 or len(records) >= MAX_RECORDS:
            raise ValueError('tree bound')
        before = _identity(os.fstat(fd))
        r = _record(fd, name)
        records.append(r)
        if r['kind'] == 'directory':
            for child in sorted(os.listdir(fd)):
                if child == '.git':
                    raise ValueError('.git forbidden')
                # NONBLOCK prevents a raced FIFO from blocking before fstat.
                c = os.open(child, FLAGS, dir_fd=fd)
                try:
                    walk(c, child if name == '.' else name + '/' + child, depth + 1)
                finally:
                    os.close(c)
        if before != _identity(os.fstat(fd)) or r['xattrs'] != _attrs(fd):
            raise ValueError('tree changed during inventory')
    fd = os.open(root, FLAGS | os.O_DIRECTORY)
    try:
        walk(fd, '.', 0)
    finally:
        os.close(fd)
    return {'schema': 'OWN_RESTORE_COPY_V1', 'records': records}


def _relative(name):
    if not isinstance(name, str) or len(name) > 4096:
        raise ValueError('path type/length')
    p = PurePosixPath(name)
    if (name == '.' or not p.parts or p.is_absolute() or str(p) != name
            or any(x in ('.', '..', '.git') for x in p.parts)):
        raise ValueError('unsafe relative path')
    return p


def _manifest(m):
    if not isinstance(m, dict) or set(m) != {'schema', 'records'} or m['schema'] != 'OWN_RESTORE_COPY_V1':
        raise ValueError('manifest schema')
    if not isinstance(m['records'], list) or not 1 <= len(m['records']) <= MAX_RECORDS:
        raise ValueError('manifest count')
    seen = {}
    base = {'path','kind','uid','gid','mode','atime_ns','mtime_ns','xattrs'}
    for i, r in enumerate(m['records']):
        if not isinstance(r, dict) or r.get('kind') not in ('directory', 'file'):
            raise ValueError('record kind')
        if set(r) != base | ({'size','sha256'} if r['kind'] == 'file' else set()):
            raise ValueError('record fields')
        n = r['path']
        if i == 0:
            if n != '.' or r['kind'] != 'directory':
                raise ValueError('root record')
        else:
            p = _relative(n)
            if seen.get(str(p.parent)) != 'directory':
                raise ValueError('missing directory parent')
        if n in seen:
            raise ValueError('duplicate path')
        seen[n] = r['kind']
        for k in ('uid','gid','mode','atime_ns','mtime_ns'):
            if type(r[k]) is not int or (k not in ('atime_ns','mtime_ns') and r[k] < 0):
                raise ValueError('metadata integer')
        if r['mode'] > 0o7777 or not isinstance(r['xattrs'], dict):
            raise ValueError('mode/xattrs')
        for k, v in r['xattrs'].items():
            if not isinstance(k, str) or not k or '\0' in k or not isinstance(v, str) or bytes.fromhex(v).hex() != v:
                raise ValueError('xattr encoding')
        if r['kind'] == 'file':
            if type(r['size']) is not int or r['size'] < 0 or not isinstance(r['sha256'], str) or len(r['sha256']) != 64:
                raise ValueError('file metadata')
            if bytes.fromhex(r['sha256']).hex() != r['sha256']:
                raise ValueError('digest encoding')
    return m


def _open_relative(root_fd, name):
    parts = _relative(name).parts
    fd = os.dup(root_fd)
    try:
        for i, p in enumerate(parts):
            nxt = os.open(p, FLAGS | (os.O_DIRECTORY if i + 1 < len(parts) else 0), dir_fd=fd)
            os.close(fd)
            fd = nxt
        return fd
    except BaseException:
        os.close(fd)
        raise


def _read_checked_archive(fd, expected):
    if _hash(fd) != expected:
        raise ValueError('archive SHA256 differs')
    os.lseek(fd, 0, os.SEEK_SET)
    # tar is read, never extractall; only exact indexed regular members accepted.
    with os.fdopen(os.dup(fd), 'rb') as stream, tarfile.open(fileobj=stream, mode='r:gz') as tf:
        first = tf.next()
        if first is None or first.name != 'manifest.json' or first.type != tarfile.REGTYPE or first.sparse is not None or first.size > MAX_MANIFEST:
            raise ValueError('manifest member')
        m = _manifest(json.loads(tf.extractfile(first).read()))
        files = [r for r in m['records'] if r['kind'] == 'file']
        for r in files:
            member = tf.next()
            if member is None or member.name != 'files/' + r['path'] or member.type != tarfile.REGTYPE or member.sparse is not None or member.size != r['size']:
                raise ValueError('payload member')
            h = hashlib.sha256()
            f = tf.extractfile(member)
            while True:
                b = f.read(CHUNK)
                if not b:
                    break
                h.update(b)
            if h.hexdigest() != r['sha256']:
                raise ValueError('payload SHA256 differs')
        if tf.next() is not None:
            raise ValueError('unexpected member')
    return m


class _ReservedWriter:
    """Admission before each unbuffered compressed write, including gzip framing.

    Caller may inspect real free space and require floor + reserve + len(data).
    Denial/exception is sticky: even a subsequent gzip footer cannot write.
    """
    name = ''
    def __init__(self, raw, reserve):
        self.raw, self.reserve, self.failed = raw, reserve, False

    def write(self, data):
        if self.failed:
            raise ValueError('reserve/output previously failed')
        try:
            if data and self.reserve is not None and self.reserve(len(data)) is not True:
                raise ValueError('caller reserve rejected compressed write')
            n = self.raw.write(data)
            if n != len(data):
                raise OSError('short archive write')
            return n
        except BaseException:
            self.failed = True
            raise

    def flush(self):
        return self.raw.flush()


def pack(exact_root, fresh_archive, *, reserve=None):
    root, out = _path(exact_root), _path(fresh_archive)
    if out == root or root in out.parents:
        raise ValueError('archive inside source')
    m = _manifest(inventory(root))
    encoded = json.dumps(m, sort_keys=True, separators=(',', ':')).encode()
    if len(encoded) > MAX_MANIFEST:
        raise ValueError('manifest bound')
    root_fd = os.open(root, FLAGS | os.O_DIRECTORY)
    try:
        out_fd = os.open(out, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
        with os.fdopen(out_fd, 'wb', buffering=0) as raw, tarfile.open(fileobj=_ReservedWriter(raw, reserve), mode='w:gz') as tf:
            h = tarfile.TarInfo('manifest.json'); h.size = len(encoded)
            tf.addfile(h, io.BytesIO(encoded))
            for r in m['records']:
                if r['kind'] != 'file':
                    continue
                fd = _open_relative(root_fd, r['path'])
                with os.fdopen(fd, 'rb') as src:
                    if _record(src.fileno(), r['path']) != r:
                        raise ValueError('source differs from inventory')
                    src.seek(0)
                    h = tarfile.TarInfo('files/' + r['path']); h.size = r['size']
                    tf.addfile(h, src)
                    if _record(src.fileno(), r['path']) != r:
                        raise ValueError('source changed during packing')
        if inventory(root) != m:
            raise ValueError('source changed during packing')
    finally:
        os.close(root_fd)
    fd = os.open(out, FLAGS)
    try:
        digest = _hash(fd)
        if _read_checked_archive(fd, digest) != m:
            raise ValueError('archive manifest differs')
    finally:
        os.close(fd)
    return dict(verified=True, manifest=m, archive_sha256=digest)


def _apply(p, r):
    os.chown(p, r['uid'], r['gid'], follow_symlinks=False)
    os.chmod(p, r['mode'], follow_symlinks=False)
    for n in os.listxattr(p, follow_symlinks=False):
        os.removexattr(p, n, follow_symlinks=False)
    for n, v in r['xattrs'].items():
        os.setxattr(p, n, bytes.fromhex(v), follow_symlinks=False)
    os.utime(p, ns=(r['atime_ns'], r['mtime_ns']), follow_symlinks=False)


def restore(archive, fresh_target, expected_archive_sha256):
    arc, target = _path(archive), _path(fresh_target)
    fd = os.open(arc, FLAGS)
    try:
        m = _read_checked_archive(fd, expected_archive_sha256)
        target.mkdir(mode=0o700)  # fresh only, after full payload/hash/path validation
        for r in m['records'][1:]:
            if r['kind'] == 'directory':
                (target / r['path']).mkdir(mode=0o700)
        os.lseek(fd, 0, os.SEEK_SET)
        with os.fdopen(os.dup(fd), 'rb') as stream, tarfile.open(fileobj=stream, mode='r:gz') as tf:
            tf.next()
            for r in m['records']:
                if r['kind'] != 'file':
                    continue
                member = tf.next()
                p = target / r['path']
                out = os.open(p, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
                with os.fdopen(out, 'wb') as dest:
                    f = tf.extractfile(member)
                    while True:
                        b = f.read(CHUNK)
                        if not b:
                            break
                        dest.write(b)
                _apply(p, r)
        for r in reversed(m['records']):
            if r['kind'] == 'directory':
                _apply(target if r['path'] == '.' else target / r['path'], r)
        if inventory(target) != m or _hash(fd) != expected_archive_sha256:
            raise ValueError('restored tree/archive differs')
    finally:
        os.close(fd)
    return dict(verified=True, manifest=m, archive_sha256=expected_archive_sha256)
