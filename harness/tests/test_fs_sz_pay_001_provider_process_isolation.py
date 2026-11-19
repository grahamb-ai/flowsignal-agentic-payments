"""Negative startup tests for reference provider process credential containment."""
import os
import subprocess
import sys

def test_provider_refuses_inherited_writer_credentials():
    env = dict(os.environ)
    env["FS_QUAL_EXECUTOR_DSN"] = "host=localhost dbname=unused"
    env["FS_QUAL_WRITER_DSN"] = "must-not-be-present"
    result = subprocess.run(
        [sys.executable, "-m", "external_targets.fs_sz_pay_001_postgres_http_service",
         "--port", "0", "--mandate-id", "MANDATE-A",
         "--issuer-public-key-file", "not-used.pem"],
        env=env, capture_output=True, text=True, timeout=5,
    )
    assert result.returncode != 0
    assert "must not receive institutional authority-writer credentials" in result.stderr

def test_provider_refuses_public_network_bind():
    env = dict(os.environ)
    env["FS_QUAL_EXECUTOR_DSN"] = "host=localhost dbname=unused"
    env.pop("FS_QUAL_WRITER_DSN", None)
    result = subprocess.run(
        [sys.executable, "-m", "external_targets.fs_sz_pay_001_postgres_http_service",
         "--host", "0.0.0.0", "--port", "0", "--mandate-id", "MANDATE-A",
         "--issuer-public-key-file", "not-used.pem"],
        env=env, capture_output=True, text=True, timeout=5,
    )
    assert result.returncode != 0
    assert "refuses non-loopback bind" in result.stderr
