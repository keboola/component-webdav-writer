import os
import pytest
import tempfile
from unittest import mock
from webdav_client import WebDAVClient
from configuration import Configuration

@pytest.fixture
def temp_dir_with_files(tmp_path):
    tables_dir = tmp_path / "in" / "tables"
    files_dir = tmp_path / "in" / "files"
    tables_dir.mkdir(parents=True, exist_ok=True)
    files_dir.mkdir(parents=True, exist_ok=True)

    (tables_dir / "test_table.csv").write_text("id,name\n1,Alice\n2,Bob\n")
    (tables_dir / "test_table.csv.manifest").write_text("{}")

    (files_dir / "document.txt").write_text("This is a test file.")

    return tmp_path

@pytest.fixture
def config_dict():
    return {
        "parameters": {
            "authorization": {
                "webdav_hostname": "https://example.com",
                "username": "user",
                "#password": "secret"
            },
            "sync_options": {
                "remote_path": "/backup",
                "append_datetime": False
            }
        }
    }

def test_scan_table_inputs(temp_dir_with_files, config_dict):
    fake_component = mock.MagicMock()
    fake_component.configuration.data_dir = str(temp_dir_with_files)

    config = Configuration(**config_dict)
    client = WebDAVClient(config, fake_component)

    tables = client.scan_table_inputs()
    assert len(tables) == 1
    assert tables[0]["name"] == "test_table.csv"
    assert tables[0]["source"].endswith("test_table.csv")

def test_scan_file_inputs(temp_dir_with_files, config_dict):
    fake_component = mock.MagicMock()
    fake_component.configuration.data_dir = str(temp_dir_with_files)

    config = Configuration(**config_dict)
    client = WebDAVClient(config, fake_component)

    files = client.scan_file_inputs()
    assert len(files) == 1
    assert files[0]["name"] == "document.txt"

@mock.patch("webdav_client.Client")
def test_upload_files(mock_webdav_client_class, temp_dir_with_files, config_dict):
    fake_component = mock.MagicMock()
    fake_component.configuration.data_dir = str(temp_dir_with_files)

    config = Configuration(**config_dict)
    client = WebDAVClient(config, fake_component)

    test_file = {
        "name": "test_upload.csv",
        "source": os.path.join(str(temp_dir_with_files), "test_upload.csv")
    }
    with open(test_file["source"], "w") as f:
        f.write("data,data,data")

    mock_webdav_client_instance = mock_webdav_client_class.return_value
    mock_webdav_client_instance.upload_sync.return_value = None

    client.upload_files([test_file])

    mock_webdav_client_instance.upload_sync.assert_called_once()
