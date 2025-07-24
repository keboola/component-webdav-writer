Configure the WebDAV Writer by specifying your WebDAV connection details and how you'd like your files stored remotely.

- **Authorization** (Required)  
  Provide your WebDAV server credentials:
  - **WebDAV Hostname**: The URL of your WebDAV server, e.g. `https://webdav.example.com`.
  - **Username**: Your WebDAV login username.
  - **Password**: Your WebDAV login password (stored securely).

- **Synchronization Options** (Required)  
  Control how your data is organized on the remote server:
  - **Remote Path**: The base folder on your WebDAV server where files will be uploaded, e.g. `/backup/files/`.
  - **Append Datetime**: If enabled, a timestamp is added to filenames for easier versioning.
  - **Datetime Format**: Select the format for the timestamp suffix, such as `YYYY-MM-DD` or `YYYYMMDD_HHMMSS`.

During execution, the WebDAV Writer scans the input directories (`/data/in/tables/` and `/data/in/files/`) and uploads all discovered files to your configured WebDAV destination.
