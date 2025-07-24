"""Security tests for filesystem access attempts in WASM sandbox."""

import pytest
from wasm_safe_eval.safe_eval import safe_eval


class TestFilesystemSecurity:
    """Test that filesystem operations are properly sandboxed."""

    def test_file_read_attempt_fails(self):
        """Test that attempting to read files fails in sandbox."""
        code = """
try:
    with open('/etc/passwd', 'r') as f:
        content = f.read()
    print(f"SUCCESS: Read {len(content)} chars")
except Exception as e:
    print(f"BLOCKED: {type(e).__name__}: {e}")
"""
        stdout, stderr, returncode = safe_eval(code)
        
        # Should not succeed in reading system files
        assert "SUCCESS:" not in stdout
        assert "BLOCKED:" in stdout or stderr
        
    def test_file_write_attempt_fails(self):
        """Test that attempting to write files fails in sandbox."""
        code = """
try:
    with open('/tmp/malicious_file.txt', 'w') as f:
        f.write("This should not work")
    print("SUCCESS: File written")
except Exception as e:
    print(f"BLOCKED: {type(e).__name__}: {e}")
"""
        stdout, stderr, returncode = safe_eval(code)
        
        # Should not succeed in writing files
        assert "SUCCESS:" not in stdout
        assert "BLOCKED:" in stdout or stderr
        
    def test_directory_listing_fails(self):
        """Test that directory listing is blocked."""
        code = """
import os
try:
    files = os.listdir('/')
    print(f"SUCCESS: Found {len(files)} files in root")
except Exception as e:
    print(f"BLOCKED: {type(e).__name__}: {e}")
"""
        stdout, stderr, returncode = safe_eval(code)
        
        # Should not succeed in listing directories
        assert "SUCCESS:" not in stdout
        assert "BLOCKED:" in stdout or stderr
        
    def test_path_traversal_fails(self):
        """Test that path traversal attacks are blocked."""
        code = """
try:
    with open('../../../etc/passwd', 'r') as f:
        content = f.read()
    print(f"SUCCESS: Path traversal worked, read {len(content)} chars")
except Exception as e:
    print(f"BLOCKED: {type(e).__name__}: {e}")
"""
        stdout, stderr, returncode = safe_eval(code)
        
        # Should not succeed with path traversal
        assert "SUCCESS:" not in stdout
        assert "BLOCKED:" in stdout or stderr
        
    def test_home_directory_access_fails(self):
        """Test that home directory access is blocked."""
        code = """
import os
try:
    home = os.path.expanduser('~')
    files = os.listdir(home)
    print(f"SUCCESS: Listed {len(files)} files in home directory")
except Exception as e:
    print(f"BLOCKED: {type(e).__name__}: {e}")
"""
        stdout, stderr, returncode = safe_eval(code)
        
        # Should not succeed in accessing home directory
        assert "SUCCESS:" not in stdout
        assert "BLOCKED:" in stdout or stderr
        
    def test_temp_directory_access_fails(self):
        """Test that temp directory access is blocked."""
        code = """
import tempfile
import os
try:
    temp_dir = tempfile.gettempdir()
    files = os.listdir(temp_dir)
    print(f"SUCCESS: Listed {len(files)} files in temp directory")
except Exception as e:
    print(f"BLOCKED: {type(e).__name__}: {e}")
"""
        stdout, stderr, returncode = safe_eval(code)
        
        # Should not succeed in accessing temp directory
        assert "SUCCESS:" not in stdout
        assert "BLOCKED:" in stdout or stderr
        
    def test_file_creation_in_current_dir_fails(self):
        """Test that file creation in current directory fails."""
        code = """
try:
    with open('test_file.txt', 'w') as f:
        f.write("malicious content")
    print("SUCCESS: Created file in current directory")
except Exception as e:
    print(f"BLOCKED: {type(e).__name__}: {e}")
"""
        stdout, stderr, returncode = safe_eval(code)
        
        # Should not succeed in creating files
        assert "SUCCESS:" not in stdout
        assert "BLOCKED:" in stdout or stderr