import subprocess
import sys

import pytest

from brujula.runlock import BuildLock


def test_lock_is_exclusive_and_reusable_after_process_exit(tmp_path):
    with BuildLock(tmp_path) as lock:
        lock.record({"run_id": "one"})
        result = subprocess.run([sys.executable, "-c", "from pathlib import Path; from brujula.runlock import BuildLock; import sys; lock=BuildLock(Path(sys.argv[1])); lock.__enter__()", str(tmp_path)], capture_output=True)
        assert result.returncode != 0
        assert b"build is running" in result.stderr
    with BuildLock(tmp_path) as lock:
        assert lock.previous == {"run_id": "one"}


def test_os_releases_lock_on_abrupt_exit(tmp_path):
    result = subprocess.run([sys.executable, "-c", "from pathlib import Path; from brujula.runlock import BuildLock; import sys,os; lock=BuildLock(Path(sys.argv[1])); lock.__enter__(); lock.record({'run_id':'crashed'}); os._exit(9)", str(tmp_path)])
    assert result.returncode == 9
    with BuildLock(tmp_path) as lock:
        assert lock.previous == {"run_id": "crashed"}


def test_legacy_lock_is_preserved(tmp_path):
    path = tmp_path / ".build.lock"
    path.write_text("manual-owner")
    with pytest.raises(RuntimeError, match="inspection"):
        with BuildLock(tmp_path):
            pass
    assert path.read_text() == "manual-owner"
