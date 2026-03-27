import pytest
from unittest.mock import MagicMock, patch
from secret_backend.config import loadVaultConfiguration


class TestLoadVaultConfigurationSuccess:
    @patch("secret_backend.config.configFileExists", return_value=True)
    def test_valid_json(self, mock_exists, mock_config_globals):
        mock_s3 = mock_config_globals
        mock_s3.get_object.return_value = {
            "Body": MagicMock(read=MagicMock(return_value=b'{"keys": ["abc"], "root_token": "tok"}'))
        }
        result = loadVaultConfiguration("vault_access.json")
        assert result == {"keys": ["abc"], "root_token": "tok"}

    @patch("secret_backend.config.configFileExists", return_value=True)
    def test_s3_get_object_called_with_correct_args(self, mock_exists, mock_config_globals):
        mock_s3 = mock_config_globals
        mock_s3.get_object.return_value = {
            "Body": MagicMock(read=MagicMock(return_value=b'{}'))
        }
        loadVaultConfiguration("my_custom_file.json")
        mock_s3.get_object.assert_called_once_with(Bucket="test-bucket", Key="my_custom_file.json")


class TestLoadVaultConfigurationReturnsNone:
    @patch("secret_backend.config.configFileExists", return_value=False)
    def test_file_does_not_exist(self, mock_exists, mock_config_globals):
        mock_s3 = mock_config_globals
        result = loadVaultConfiguration("vault_access.json")
        assert result is None
        mock_s3.get_object.assert_not_called()

    @patch("secret_backend.config.configFileExists", return_value=True)
    def test_s3_get_object_fails(self, mock_exists, mock_config_globals):
        mock_s3 = mock_config_globals
        mock_s3.get_object.side_effect = Exception("S3 connection error")
        result = loadVaultConfiguration("vault_access.json")
        assert result is None


class TestLoadVaultConfigurationRaises:
    @patch("secret_backend.config.configFileExists", return_value=True)
    def test_invalid_json_raises_value_error(self, mock_exists, mock_config_globals):
        mock_s3 = mock_config_globals
        mock_s3.get_object.return_value = {
            "Body": MagicMock(read=MagicMock(return_value=b"not valid json"))
        }
        with pytest.raises(ValueError, match="invalid JSON"):
            loadVaultConfiguration("vault_access.json")

    @patch("secret_backend.config.configFileExists", return_value=True)
    def test_empty_json_body_raises_value_error(self, mock_exists, mock_config_globals):
        mock_s3 = mock_config_globals
        mock_s3.get_object.return_value = {
            "Body": MagicMock(read=MagicMock(return_value=b""))
        }
        with pytest.raises(ValueError, match="invalid JSON"):
            loadVaultConfiguration("vault_access.json")

    def test_config_file_exists_raises_propagates(self, mock_config_globals):
        with patch("secret_backend.config.configFileExists", side_effect=Exception("S3 error")):
            with pytest.raises(Exception, match="S3 error"):
                loadVaultConfiguration("vault_access.json")
