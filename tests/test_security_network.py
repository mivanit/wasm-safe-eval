"""Security tests for network access attempts in WASM sandbox."""

import pytest
from wasm_safe_eval.safe_eval import safe_eval


class TestNetworkSecurity:
    """Test that network operations are properly sandboxed."""

    def test_http_request_fails(self):
        """Test that HTTP requests are blocked."""
        code = """
try:
    import urllib.request
    response = urllib.request.urlopen('http://httpbin.org/get')
    data = response.read()
    print(f"SUCCESS: HTTP request returned {len(data)} bytes")
except Exception as e:
    print(f"BLOCKED: {type(e).__name__}: {e}")
"""
        stdout, stderr, returncode = safe_eval(code)
        
        # Should not succeed in making HTTP requests
        assert "SUCCESS:" not in stdout
        assert "BLOCKED:" in stdout or stderr

    def test_https_request_fails(self):
        """Test that HTTPS requests are blocked."""
        code = """
try:
    import urllib.request
    response = urllib.request.urlopen('https://httpbin.org/get')
    data = response.read()
    print(f"SUCCESS: HTTPS request returned {len(data)} bytes")
except Exception as e:
    print(f"BLOCKED: {type(e).__name__}: {e}")
"""
        stdout, stderr, returncode = safe_eval(code)
        
        # Should not succeed in making HTTPS requests
        assert "SUCCESS:" not in stdout
        assert "BLOCKED:" in stdout or stderr

    def test_socket_connection_fails(self):
        """Test that socket connections are blocked."""
        code = """
try:
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('google.com', 80))
    s.send(b'GET / HTTP/1.1\\r\\nHost: google.com\\r\\n\\r\\n')
    data = s.recv(1024)
    s.close()
    print(f"SUCCESS: Socket connection returned {len(data)} bytes")
except Exception as e:
    print(f"BLOCKED: {type(e).__name__}: {e}")
"""
        stdout, stderr, returncode = safe_eval(code)
        
        # Should not succeed in making socket connections
        assert "SUCCESS:" not in stdout
        assert "BLOCKED:" in stdout or stderr

    def test_dns_lookup_fails(self):
        """Test that DNS lookups are blocked."""
        code = """
try:
    import socket
    ip = socket.gethostbyname('google.com')
    print(f"SUCCESS: DNS lookup returned IP: {ip}")
except Exception as e:
    print(f"BLOCKED: {type(e).__name__}: {e}")
"""
        stdout, stderr, returncode = safe_eval(code)
        
        # Should not succeed in DNS lookups
        assert "SUCCESS:" not in stdout
        assert "BLOCKED:" in stdout or stderr

    def test_ftp_connection_fails(self):
        """Test that FTP connections are blocked."""
        code = """
try:
    import ftplib
    ftp = ftplib.FTP('ftp.debian.org')
    ftp.login()
    files = ftp.nlst()
    ftp.quit()
    print(f"SUCCESS: FTP connection listed {len(files)} files")
except Exception as e:
    print(f"BLOCKED: {type(e).__name__}: {e}")
"""
        stdout, stderr, returncode = safe_eval(code)
        
        # Should not succeed in FTP connections
        assert "SUCCESS:" not in stdout
        assert "BLOCKED:" in stdout or stderr

    def test_localhost_connection_fails(self):
        """Test that localhost connections are blocked."""
        code = """
try:
    import urllib.request
    response = urllib.request.urlopen('http://localhost:80')
    data = response.read()
    print(f"SUCCESS: Localhost connection returned {len(data)} bytes")
except Exception as e:
    print(f"BLOCKED: {type(e).__name__}: {e}")
"""
        stdout, stderr, returncode = safe_eval(code)
        
        # Should not succeed in localhost connections
        assert "SUCCESS:" not in stdout
        assert "BLOCKED:" in stdout or stderr

    def test_internal_ip_connection_fails(self):
        """Test that internal IP connections are blocked."""
        code = """
try:
    import urllib.request
    response = urllib.request.urlopen('http://192.168.1.1')
    data = response.read()
    print(f"SUCCESS: Internal IP connection returned {len(data)} bytes")
except Exception as e:
    print(f"BLOCKED: {type(e).__name__}: {e}")
"""
        stdout, stderr, returncode = safe_eval(code)
        
        # Should not succeed in internal IP connections
        assert "SUCCESS:" not in stdout
        assert "BLOCKED:" in stdout or stderr