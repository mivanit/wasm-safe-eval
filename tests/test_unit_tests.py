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


class TestExceptions:
    """Test custom exception classes."""

    def test_wasmtime_not_found_error(self):
        """Test WasmtimeNotFoundError can be raised and caught."""
        with pytest.raises(WasmtimeNotFoundError):
            raise WasmtimeNotFoundError("Test message")

    def test_rustpython_wasm_not_found_error(self):
        """Test RustPythonWasmNotFoundError can be raised and caught."""
        with pytest.raises(RustPythonWasmNotFoundError):
            raise RustPythonWasmNotFoundError("Test message")

    def test_platform_not_supported_error(self):
        """Test PlatformNotSupportedError can be raised and caught."""
        with pytest.raises(PlatformNotSupportedError):
            raise PlatformNotSupportedError("Test message")


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

    def test_get_rustpython_wasm_path_success(self):
        """Test getting RustPython WASM path when file exists."""
        with patch('importlib.resources.files') as mock_files:
            mock_path = MagicMock()
            mock_path.exists.return_value = True
            mock_files.return_value.joinpath.return_value = mock_path
            
            with patch('pathlib.Path') as mock_path_class:
                mock_path_class.return_value = mock_path
                result = get_rustpython_wasm_path()
                assert result == mock_path

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


class TestInstallWasmtime:
    """Test wasmtime installation functionality."""

    def test_install_wasmtime_already_installed(self):
        """Test when wasmtime is already installed."""
        with patch('wasm_safe_eval.install_wasmtime._try_find_wasmtime', 
                   return_value='/usr/bin/wasmtime'):
            with patch('builtins.print') as mock_print:
                install_wasmtime()
                mock_print.assert_called_with('wasmtime already installed at: /usr/bin/wasmtime\nexiting.')

    def test_install_wasmtime_unsupported_platform(self):
        """Test installation on unsupported platform."""
        with patch('wasm_safe_eval.install_wasmtime._try_find_wasmtime', return_value=None):
            with patch('platform.system', return_value='Windows'):
                with pytest.raises(PlatformNotSupportedError):
                    install_wasmtime()

    def test_install_wasmtime_user_cancels(self):
        """Test when user cancels installation."""
        with patch('wasm_safe_eval.install_wasmtime._try_find_wasmtime', return_value=None):
            with patch('platform.system', return_value='Linux'):
                with patch('builtins.input', return_value='n'):
                    with patch('sys.exit') as mock_exit:
                        install_wasmtime()
                        mock_exit.assert_called_with(0)

    def test_install_wasmtime_success(self):
        """Test successful installation."""
        with patch('wasm_safe_eval.install_wasmtime._try_find_wasmtime', return_value=None):
            with patch('platform.system', return_value='Linux'):
                with patch('builtins.input', return_value='y'):
                    with patch('subprocess.run') as mock_run:
                        mock_run.return_value.returncode = 0
                        with patch('builtins.print') as mock_print:
                            install_wasmtime()
                            # Should print success message
                            mock_print.assert_any_call(
                                "wasmtime installed successfully! You may need to restart your terminal for changes to take effect."
                            )

    def test_install_wasmtime_failure(self):
        """Test failed installation."""
        with patch('wasm_safe_eval.install_wasmtime._try_find_wasmtime', return_value=None):
            with patch('platform.system', return_value='Linux'):
                with patch('builtins.input', return_value='y'):
                    with patch('subprocess.run') as mock_run:
                        mock_run.return_value.returncode = 1
                        mock_run.return_value.stderr = "Installation failed"
                        with pytest.raises(RuntimeError):
                            install_wasmtime()


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


class TestIntegrationHelpers:
    """Helper tests for integration scenarios."""

    def test_command_construction(self):
        """Test that wasmtime command is constructed correctly."""
        from wasm_safe_eval.safe_eval import safe_eval
        
        with patch('wasm_safe_eval.safe_eval._try_find_wasmtime', 
                   return_value='/usr/bin/wasmtime'):
            with patch('subprocess.run') as mock_run:
                mock_run.return_value.stdout = "test output"
                mock_run.return_value.stderr = ""
                mock_run.return_value.returncode = 0
                
                safe_eval("print('test')")
                
                # Check that subprocess.run was called with correct command structure
                call_args = mock_run.call_args[0][0]
                assert call_args[0] == '/usr/bin/wasmtime'
                assert call_args[1].endswith('rustpython.wasm')
                assert call_args[2].endswith('.py')

    def test_subprocess_parameters(self):
        """Test that subprocess is called with correct parameters."""
        from wasm_safe_eval.safe_eval import safe_eval
        
        with patch('wasm_safe_eval.safe_eval._try_find_wasmtime', 
                   return_value='/usr/bin/wasmtime'):
            with patch('subprocess.run') as mock_run:
                mock_run.return_value.stdout = ""
                mock_run.return_value.stderr = ""
                mock_run.return_value.returncode = 0
                
                safe_eval("print('test')")
                
                # Check subprocess parameters
                call_kwargs = mock_run.call_args[1]
                assert call_kwargs['text'] is True
                assert call_kwargs['capture_output'] is True
                assert call_kwargs['check'] is False