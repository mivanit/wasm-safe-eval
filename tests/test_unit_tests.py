"""Unit tests for individual modules and functions."""

import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path
import tempfile
import os
import shutil

from wasm_safe_eval._exceptions import (
    WasmtimeNotFoundError, 
    RustPythonWasmNotFoundError, 
    PlatformNotSupportedError
)
from wasm_safe_eval._paths import _try_find_wasmtime, get_rustpython_wasm_path, WASMTIME_EXEC
from wasm_safe_eval.install_wasmtime import install_wasmtime


class TestPaths:
    """Test path utility functions."""

    def test_try_find_wasmtime_in_default_location(self):
        """Test finding wasmtime in default location."""
        with patch('pathlib.Path.exists', return_value=True):
            result = _try_find_wasmtime()
            assert result == WASMTIME_EXEC

    def test_try_find_wasmtime_in_path(self):
        """Test finding wasmtime in system PATH."""
        with patch('pathlib.Path.exists', return_value=False):
            with patch('shutil.which', return_value='/usr/bin/wasmtime'):
                result = _try_find_wasmtime()
                assert result == '/usr/bin/wasmtime'

    def test_try_find_wasmtime_not_found(self):
        """Test when wasmtime is not found anywhere."""
        with patch('pathlib.Path.exists', return_value=False):
            with patch('shutil.which', return_value=None):
                result = _try_find_wasmtime()
                assert result is None

    def test_get_rustpython_wasm_path_not_found(self):
        """Test RustPythonWasmNotFoundError when WASM file doesn't exist."""
        with patch('importlib.resources.files') as mock_files:
            mock_path = MagicMock()
            mock_path.exists.return_value = False
            mock_files.return_value.joinpath.return_value = mock_path
            
            with patch('pathlib.Path') as mock_path_class:
                mock_path_class.return_value = mock_path
                with pytest.raises(RustPythonWasmNotFoundError):
                    get_rustpython_wasm_path()


class TestSafeEvalInternals:
    """Test internal functionality of safe_eval."""

    def test_temporary_file_cleanup(self):
        """Test that temporary files are properly cleaned up."""
        from wasm_safe_eval.safe_eval import safe_eval
        
        # Track created temporary files
        original_tempfile = tempfile.NamedTemporaryFile
        temp_files = []
        
        def mock_tempfile(*args, **kwargs):
            tf = original_tempfile(*args, **kwargs)
            temp_files.append(tf.name)
            return tf
        
        with patch('tempfile.NamedTemporaryFile', side_effect=mock_tempfile):
            with patch('wasm_safe_eval.safe_eval._try_find_wasmtime', 
                       return_value='/fake/wasmtime'):
                with patch('subprocess.run') as mock_run:
                    mock_run.return_value.stdout = ""
                    mock_run.return_value.stderr = ""
                    mock_run.return_value.returncode = 0
                    
                    safe_eval("print('test')")
                    
                    # Check that all temporary files were cleaned up
                    for temp_file in temp_files:
                        assert not os.path.exists(temp_file)

    def test_no_result_sentinel(self):
        """Test _NoResultSentinel behavior."""
        from wasm_safe_eval.safe_eval import _NoResultSentinel
        
        sentinel = _NoResultSentinel()
        assert "No result returned" in str(sentinel)
        assert "No result returned" in repr(sentinel)
        assert "No result returned" in sentinel.message
