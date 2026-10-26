"""M1 regression: absence of a server sync log cannot permit recovery."""
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parent/'operations'))
import fleet_health as h


class MissingSyncLogTests(unittest.TestCase):
    def test_missing_server_sync_log_blocks_health_and_recovery(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            report=root/'result.json'
            report.write_text(json.dumps(dict(processes={},cgroup=str(root/'missing-cgroup'),
                                              game_port=29880,query_port=29881,bots=1,
                                              dll_sha256=h.DLL)))
            query=dict(gamever='1.07',numplayers='1',maxplayers='16',
                       activemod='',player_0=h.q.ROSTER[0])
            with patch.object(h.q,'query',return_value=query), \
                 patch.object(h.q,'validate_master_resolution',return_value=True), \
                 patch.object(h,'udp_owners',return_value=set()), \
                 patch.object(h,'available_memory',return_value=2*1024**3):
                snapshot,verdict=h.collect(report)
            self.assertFalse(snapshot['sync_scan_complete'],
                             'missing file was silently admitted as zero bad syncs')
            self.assertFalse(verdict['safe_recovery'])
            self.assertIn('SYNC_LOG_SCAN_PENDING',verdict['alerts'])


if __name__=='__main__':unittest.main()
