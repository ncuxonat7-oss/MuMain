#!/usr/bin/env python3
"""Exercise the overlay CLI with a CP1252 default and a supplied pinned input."""
import argparse
from contextlib import redirect_stdout
import hashlib
import io
import json
from pathlib import Path
import runpy
import sys
import tempfile
from unittest.mock import patch

REPOSITORY = Path(__file__).resolve().parents[1]
EXPECTED_SHA256 = '1441360f93d80291659f63912022e0816125863acd0212ab4ec02fca33ebbb73'
PATH_OPEN = Path.open


def cp1252_default_open(self, mode='r', buffering=-1, encoding=None,
                       errors=None, newline=None):
    # Path.read_text resolves an omitted encoding to the 'locale' sentinel.
    if 'b' not in mode and encoding in (None, 'locale'):
        encoding = 'cp1252'
    return PATH_OPEN(self, mode, buffering, encoding, errors, newline)


def check_cli(source):
    with tempfile.TemporaryDirectory(prefix='overlay-encoding-') as directory:
        data = Path(directory)
        target = data / 'Items/Group12_Wing.json'
        target.parent.mkdir()
        target.write_bytes(source.read_bytes())
        script = REPOSITORY / 'scripts/apply-client-overlay.py'
        arguments = [str(script), '--data', str(data), '--overlay',
                     str(REPOSITORY / 'patches/client-socket-metadata.json')]
        output = io.StringIO()
        with patch.object(Path, 'open', cp1252_default_open), \
                patch.object(sys, 'argv', arguments), redirect_stdout(output):
            runpy.run_path(str(script), run_name='__main__')
        assert json.loads(output.getvalue()) == {
            'status': 'APPLIED', 'sha256': EXPECTED_SHA256}
        corrected = target.read_bytes()
        assert hashlib.sha256(corrected).hexdigest() == EXPECTED_SHA256
        entries = {item['number']: item for item in json.loads(corrected)['items']}
        assert entries[73]['name']['de'] == 'Sph\u00e4re (4)'
        assert entries[74]['name']['de'] == 'Sph\u00e4re (5)'


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', required=True, type=Path,
                        help='Authentic Group12_Wing.json, Git blob e2d19fa0bab76df8b3eeb9d146a6529ece26d544')
    args = parser.parse_args()
    check_cli(args.source)
    print('PASS: CLI with CP1252 default preserves reviewed output SHA256 and German names')
