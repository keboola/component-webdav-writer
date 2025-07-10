import pytest
from configuration import Configuration, UserException, ALLOWED_DATETIME_FORMATS

def test_valid_configuration():
    raw_config = {
        "parameters": {
            "authorization": {
                "webdav_hostname": "https://example.com",
                "username": "user",
                "#password": "secret"
            },
            "sync_options": {
                "remote_path": "/backup",
                "append_datetime": True,
                "datetime_format": "%Y-%m-%d_%H-%M-%S"
            }
        }
    }

    config = Configuration(**raw_config)
    assert config.auth.webdav_hostname == "https://example.com"
    assert config.sync.remote_path == "/backup"
    assert config.sync.datetime_format == "%Y-%m-%d_%H-%M-%S"
    suffix = config.datetime_suffix
    assert isinstance(suffix, str)
    assert suffix

def test_invalid_hostname():
    raw_config = {
        "parameters": {
            "authorization": {
                "webdav_hostname": "   ",
                "username": "user",
                "#password": "secret"
            },
            "sync_options": {
                "remote_path": "/backup",
            }
        }
    }
    with pytest.raises(UserException) as exc_info:
        Configuration(**raw_config)

    assert "webdav_hostname" in str(exc_info.value)

def test_invalid_datetime_format():
    raw_config = {
        "parameters": {
            "authorization": {
                "webdav_hostname": "https://example.com",
                "username": "user",
                "#password": "secret"
            },
            "sync_options": {
                "remote_path": "/backup",
                "append_datetime": True,
                "datetime_format": "invalid_format"
            }
        }
    }
    with pytest.raises(UserException) as exc_info:
        Configuration(**raw_config)

    assert "datetime_format" in str(exc_info.value)

@pytest.mark.parametrize("fmt", ALLOWED_DATETIME_FORMATS)
def test_datetime_suffix_formats(fmt):
    raw_config = {
        "parameters": {
            "authorization": {
                "webdav_hostname": "https://example.com",
                "username": "user",
                "#password": "secret"
            },
            "sync_options": {
                "remote_path": "/backup",
                "append_datetime": True,
                "datetime_format": fmt
            }
        }
    }
    config = Configuration(**raw_config)
    suffix = config.datetime_suffix
    assert isinstance(suffix, str)
    assert suffix
