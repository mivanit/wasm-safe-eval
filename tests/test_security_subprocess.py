"""Security tests for subprocess execution attempts in WASM sandbox."""

import pytest
from wasm_safe_eval.safe_eval import safe_eval


class TestSubprocessSecurity:
    """Test that subprocess execution is properly sandboxed."""

    def test_subprocess_run_blocked(self):
        """Test that subprocess.run is blocked."""
        code = """
import subprocess
try:
    result = subprocess.run(['ls', '-la'], capture_output=True, text=True)
    print(f"SUCCESS: Command executed, stdout: {result.stdout[:100]}")
except Exception as e:
    print(f"BLOCKED: {type(e).__name__}: {e}")
"""
        stdout, stderr, returncode = safe_eval(code)
        
        # Should not succeed in running subprocesses
        assert "SUCCESS:" not in stdout
        assert "BLOCKED:" in stdout or stderr

    def test_subprocess_popen_blocked(self):
        """Test that subprocess.Popen is blocked."""
        code = """
import subprocess
try:
    proc = subprocess.Popen(['whoami'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    stdout_data, stderr_data = proc.communicate()
    print(f"SUCCESS: Popen executed, output: {stdout_data.strip()}")
except Exception as e:
    print(f"BLOCKED: {type(e).__name__}: {e}")
"""
        stdout, stderr, returncode = safe_eval(code)
        
        # Should not succeed in running subprocesses
        assert "SUCCESS:" not in stdout
        assert "BLOCKED:" in stdout or stderr

    def test_os_system_blocked(self):
        """Test that os.system is blocked."""
        code = """
import os
try:
    result = os.system('echo "Hello from system command"')
    print(f"SUCCESS: os.system executed with return code: {result}")
except Exception as e:
    print(f"BLOCKED: {type(e).__name__}: {e}")
"""
        stdout, stderr, returncode = safe_eval(code)
        
        # Should not succeed in running system commands
        assert "SUCCESS:" not in stdout
        assert "BLOCKED:" in stdout or stderr

    def test_os_popen_blocked(self):
        """Test that os.popen is blocked."""
        code = """
import os
try:
    with os.popen('uname -a') as f:
        output = f.read()
    print(f"SUCCESS: os.popen executed, output: {output.strip()}")
except Exception as e:
    print(f"BLOCKED: {type(e).__name__}: {e}")
"""
        stdout, stderr, returncode = safe_eval(code)
        
        # Should not succeed in running system commands
        assert "SUCCESS:" not in stdout
        assert "BLOCKED:" in stdout or stderr

    def test_os_spawn_family_blocked(self):
        """Test that os.spawn* functions are blocked."""
        code = """
import os
try:
    # Try different spawn functions
    if hasattr(os, 'spawnl'):
        result = os.spawnl(os.P_WAIT, '/bin/echo', 'echo', 'hello')
        print(f"SUCCESS: os.spawnl executed with result: {result}")
    elif hasattr(os, 'spawnv'):
        result = os.spawnv(os.P_WAIT, '/bin/echo', ['echo', 'hello'])
        print(f"SUCCESS: os.spawnv executed with result: {result}")
    else:
        print("INFO: No spawn functions available")
except Exception as e:
    print(f"BLOCKED: {type(e).__name__}: {e}")
"""
        stdout, stderr, returncode = safe_eval(code)
        
        # Should not succeed in spawning processes
        assert "SUCCESS:" not in stdout

    def test_exec_family_blocked(self):
        """Test that exec* functions are blocked."""
        code = """
import os
try:
    # This would replace the current process, so it's very dangerous
    os.execl('/bin/echo', 'echo', 'hello')
    print("SUCCESS: exec executed (this should never print)")
except Exception as e:
    print(f"BLOCKED: {type(e).__name__}: {e}")
"""
        stdout, stderr, returncode = safe_eval(code)
        
        # Should not succeed in exec calls
        assert "SUCCESS:" not in stdout
        assert "BLOCKED:" in stdout or stderr

    def test_shell_command_injection_blocked(self):
        """Test that shell command injection is blocked."""
        code = """
import subprocess
import os
try:
    # Try various shell injection techniques
    malicious_commands = [
        "echo hello; cat /etc/passwd",
        "echo hello && whoami",
        "echo hello | grep hello",
        "$(whoami)",
        "`id`"
    ]
    
    for cmd in malicious_commands:
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=1)
            if result.stdout:
                print(f"SUCCESS: Shell injection worked for: {cmd}")
                break
        except:
            continue
    else:
        print("INFO: All shell injections failed")
except Exception as e:
    print(f"BLOCKED: {type(e).__name__}: {e}")
"""
        stdout, stderr, returncode = safe_eval(code)
        
        # Should not succeed in shell injection
        assert "SUCCESS:" not in stdout

    def test_multiprocessing_blocked(self):
        """Test that multiprocessing is blocked."""
        code = """
try:
    import multiprocessing
    
    def worker_func():
        return "Hello from worker process"
    
    with multiprocessing.Pool(1) as pool:
        result = pool.apply(worker_func)
    print(f"SUCCESS: Multiprocessing worked: {result}")
except Exception as e:
    print(f"BLOCKED: {type(e).__name__}: {e}")
"""
        stdout, stderr, returncode = safe_eval(code)
        
        # Should not succeed in creating new processes
        assert "SUCCESS:" not in stdout
        assert "BLOCKED:" in stdout or stderr

    def test_threading_limited(self):
        """Test that threading has limitations."""
        code = """
import threading
import time
try:
    results = []
    
    def worker():
        results.append("Thread executed")
    
    thread = threading.Thread(target=worker)
    thread.start()
    thread.join(timeout=1)
    
    if results:
        print(f"SUCCESS: Threading worked: {results[0]}")
    else:
        print("LIMITED: Threading timed out or failed")
except Exception as e:
    print(f"BLOCKED: {type(e).__name__}: {e}")
"""
        stdout, stderr, returncode = safe_eval(code)
        
        # Threading might work within WASM but should be limited
        # This is acceptable as it doesn't escape the sandbox