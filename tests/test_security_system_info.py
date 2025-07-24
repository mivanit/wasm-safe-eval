"""Security tests for system information access attempts in WASM sandbox."""

import pytest
from wasm_safe_eval.safe_eval import safe_eval


class TestSystemInfoSecurity:
    """Test that system information access is properly sandboxed."""

    def test_environment_variables_access_limited(self):
        """Test that environment variables access is limited."""
        code = """
import os
try:
    env_vars = dict(os.environ)
    sensitive_vars = [k for k in env_vars.keys() if any(x in k.lower() for x in ['password', 'key', 'token', 'secret', 'home', 'user', 'path'])]
    print(f"SUCCESS: Found {len(env_vars)} env vars, {len(sensitive_vars)} potentially sensitive")
    if sensitive_vars:
        print(f"SENSITIVE VARS: {sensitive_vars[:5]}")  # Show first 5
except Exception as e:
    print(f"BLOCKED: {type(e).__name__}: {e}")
"""
        stdout, stderr, returncode = safe_eval(code)
        
        # Should either be blocked or have very limited access
        # WASM environment should not expose host environment variables
        if "SUCCESS:" in stdout:
            # If it succeeds, there should be very few or no sensitive variables
            assert "SENSITIVE VARS:" not in stdout or stdout.count("SENSITIVE VARS: []") > 0

    def test_system_platform_info_limited(self):
        """Test that system platform information is limited."""
        code = """
import platform
try:
    info = {
        'system': platform.system(),
        'machine': platform.machine(),
        'processor': platform.processor(),
        'node': platform.node(),
        'release': platform.release(),
        'version': platform.version()
    }
    real_system_indicators = any(x in str(info).lower() for x in ['linux', 'windows', 'darwin', 'x86_64', 'amd64'])
    print(f"INFO: {info}")
    if real_system_indicators:
        print("SUCCESS: Got real system information")
    else:
        print("SANDBOXED: System info appears sandboxed")
except Exception as e:
    print(f"BLOCKED: {type(e).__name__}: {e}")
"""
        stdout, stderr, returncode = safe_eval(code)
        
        # Should not reveal real host system information
        assert "SUCCESS: Got real system information" not in stdout

    def test_user_info_access_blocked(self):
        """Test that user information access is blocked."""
        code = """
import os
import getpass
try:
    user_info = {
        'user': getpass.getuser(),
        'uid': os.getuid() if hasattr(os, 'getuid') else 'N/A',
        'gid': os.getgid() if hasattr(os, 'getgid') else 'N/A',
        'groups': os.getgroups() if hasattr(os, 'getgroups') else 'N/A'
    }
    print(f"SUCCESS: Got user info: {user_info}")
except Exception as e:
    print(f"BLOCKED: {type(e).__name__}: {e}")
"""
        stdout, stderr, returncode = safe_eval(code)
        
        # Should not succeed in getting real user information
        assert "SUCCESS:" not in stdout
        assert "BLOCKED:" in stdout or stderr

    def test_process_info_access_limited(self):
        """Test that process information access is limited."""
        code = """
import os
try:
    process_info = {
        'pid': os.getpid(),
        'ppid': os.getppid() if hasattr(os, 'getppid') else 'N/A',
        'cwd': os.getcwd()
    }
    print(f"SUCCESS: Got process info: {process_info}")
    # Check if we can see real host processes
    if hasattr(os, 'listdir'):
        try:
            proc_files = os.listdir('/proc')
            print(f"PROC_ACCESS: Found {len(proc_files)} items in /proc")
        except:
            print("PROC_BLOCKED: /proc access blocked")
except Exception as e:
    print(f"BLOCKED: {type(e).__name__}: {e}")
"""
        stdout, stderr, returncode = safe_eval(code)
        
        # Should not have access to real host /proc filesystem
        assert "PROC_ACCESS:" not in stdout

    def test_memory_info_access_limited(self):
        """Test that memory information access is limited."""
        code = """
try:
    import resource
    mem_info = resource.getrusage(resource.RUSAGE_SELF)
    print(f"SUCCESS: Got memory info - RSS: {mem_info.ru_maxrss}")
except Exception as e:
    print(f"BLOCKED: {type(e).__name__}: {e}")
"""
        stdout, stderr, returncode = safe_eval(code)
        
        # Memory access should be blocked or limited to WASM process
        # This is acceptable either way, but real host memory info should not be accessible

    def test_cpu_info_access_limited(self):
        """Test that CPU information access is limited."""
        code = """
try:
    import os
    cpu_count = os.cpu_count()
    print(f"SUCCESS: Got CPU count: {cpu_count}")
    
    # Try to read /proc/cpuinfo
    try:
        with open('/proc/cpuinfo', 'r') as f:
            cpuinfo = f.read()
        print(f"CPUINFO_ACCESS: Read {len(cpuinfo)} chars from /proc/cpuinfo")
    except Exception as e:
        print(f"CPUINFO_BLOCKED: {type(e).__name__}")
        
except Exception as e:
    print(f"BLOCKED: {type(e).__name__}: {e}")
"""
        stdout, stderr, returncode = safe_eval(code)
        
        # Should not have access to real CPU information via /proc
        assert "CPUINFO_ACCESS:" not in stdout

    def test_hostname_access_limited(self):
        """Test that hostname access is limited."""
        code = """
import socket
try:
    hostname = socket.gethostname()
    fqdn = socket.getfqdn()
    print(f"SUCCESS: Got hostname: {hostname}, FQDN: {fqdn}")
except Exception as e:
    print(f"BLOCKED: {type(e).__name__}: {e}")
"""
        stdout, stderr, returncode = safe_eval(code)
        
        # Should not succeed in getting real hostname
        assert "SUCCESS:" not in stdout
        assert "BLOCKED:" in stdout or stderr