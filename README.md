# WebDAV Writer (Python)

The WebDAV Writer uploads files from Keboola’s input mapping directly to any WebDAV-compatible storage server.

## Features

- **Flexible WebDAV Uploads**
  - Supports any WebDAV-compatible server (Nextcloud, ownCloud, WebDAV-enabled storage, etc.).
  
- **Handles Tables and Files**
  - Uploads all files found in:
    - `/data/in/tables/`
    - `/data/in/files/`

- **Dynamic Filenames with Datetime**
  - Optional timestamp suffix added to filenames for versioning.

- **Secure Credentials**
  - Credentials stored securely.
  - No secrets printed to logs.

- **Manifest-Safe**
  - Ignores `.manifest` files automatically.

## Configuration

The writer uses a JSON configuration file structured like this:

```json
{
  "parameters": {
    "authorization": {
      "webdav_hostname": "https://webdav.example.com",
      "username": "your-username",
      "#password": "your-password"
    },
    "sync_options": {
      "remote_path": "/backup/files",
      "append_datetime": true,
      "datetime_format": "%Y-%m-%d_%H-%M-%S"
    }
  },
  "action": "run"
}
```

### Configuration Parameters

| Parameter                       | Required | Description                                                                                                                                                  |
| ------------------------------- | -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `authorization.webdav_hostname` | Yes      | URL of your WebDAV server, e.g. `https://webdav.example.com`.                                                                                                |
| `authorization.username`        | Yes      | Your WebDAV username.                                                                                                                                        |
| `authorization.#password`       | Yes      | Your WebDAV password (stored securely in Keboola).                                                                                                           |
| `sync_options.remote_path`      | Yes      | The remote folder on your WebDAV server where files will be uploaded, e.g. `/backup/files/`.                                                                 |
| `sync_options.append_datetime`  | No       | Whether to append a datetime suffix to filenames. Defaults to `false`.                                                                                       |
| `sync_options.datetime_format`  | No       | Datetime format string for suffix if `append_datetime` is enabled. Supported formats: `%Y-%m-%d`, `%Y-%m-%d_%H-%M-%S`, `%Y%m%d`, `%Y%m%d_%H%M%S`, `{epoch}`. |


#### Notes:

- `.manifest` files are automatically ignored.
- If datetime suffixing is enabled, filenames will look like:

```text
your_file.csv → your_file_2024-07-01_12-30-00.csv
```

## Upload Process

During execution:

1. All files in `/data/in/tables/` and `/data/in/files/` are scanned.
2. Each file is uploaded to the configured WebDAV destination path.
3. Filenames are adjusted if the datetime suffix is enabled.

## Running Locally

To test locally, create a `data/config.json` file:

```json
{
  "parameters": {
    "authorization": {
      "webdav_hostname": "http://localhost:8080",
      "username": "admin",
      "#password": "password"
    },
    "sync_options": {
      "remote_path": "/upload",
      "append_datetime": true,
      "datetime_format": "%Y-%m-%d"
    }
  }
}
```

Run the component:

```bash
python3 src/component.py
```

### Example Local WebDAV Server

```bash
docker run -d \
  --name webdav \
  -e AUTH_TYPE=Basic \
  -e USERNAME=admin \
  -e PASSWORD=password \
  -e SERVER_NAMES=localhost \
  -p 8080:80 \
  bytemark/webdav
```

Then access your server at `http://localhost:8080`.

### Development & Testing

Install all dependencies into your virtual environment using `uv`:

```bash
uv pip sync
```

This installs everything listed in your `uv.lock` file, ensuring a fully reproducible environment matching your `pyproject.toml` specifications.

To update your lockfile after changing dependencies in `pyproject.toml`, run:

```bash
uv pip compile pyproject.toml --output-file uv.lock
```

Run tests with:

```bash
pytest
```

## License

MIT License