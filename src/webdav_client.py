import os
import logging
from webdav3.client import Client
from keboola.component import UserException

class WebDAVClient:
    def __init__(self, config, component):
        """
        WebDAV Client for Keboola Writer Component.

        :param config: validated Configuration object
        :param component: Keboola ComponentBase instance
        """
        self.config = config
        self.component = component
        self.data_dir = self.component.configuration.data_dir

        # Initialize the webdavclient3 client
        self.client = Client({
            "webdav_hostname": self.config.auth.webdav_hostname,
            "webdav_login": self.config.auth.username,
            "webdav_password": self.config.auth.password,
        })

        logging.info(f"[WebDAVClient] Initialized for {self.config.auth.webdav_hostname}")

    def scan_table_inputs(self):
        """
        Scan data/in/tables and return file metadata.

        :return: list of dicts:
            - name
            - source
        """
        return self._scan_directory("in/tables")

    def scan_file_inputs(self):
        """
        Scan data/in/files and return file metadata.

        :return: list of dicts:
            - name
            - source
        """
        return self._scan_directory("in/files")

    def _scan_directory(self, relative_path):
        """
        Scan a path relative to the Keboola data_dir and return file info.

        :param relative_path: e.g. "in/tables"
        :return: list of dicts:
            - name
            - source (absolute local path)
        """
        dir_path = os.path.join(self.data_dir, relative_path)

        if not os.path.exists(dir_path):
            logging.info(f"[WebDAVClient] Directory does not exist: {dir_path} → skipping scan.")
            return []

        logging.info(f"[WebDAVClient] Scanning directory: {dir_path}")

        files = []
        for filename in os.listdir(dir_path):
            if filename.endswith(".manifest"):
                logging.debug(f"[WebDAVClient] Skipping manifest file: {filename}")
                continue

            full_path = os.path.join(dir_path, filename)
            if os.path.isfile(full_path):
                files.append({
                    "name": filename,
                    "source": full_path,
                })

        logging.info(f"[WebDAVClient] Found {len(files)} files in {dir_path}")
        return files


    def upload_files(self, files, remote_path=None):
        """
        Upload multiple files to WebDAV.

        :param files: list of dicts:
            - name
            - source
        :param remote_path: override config.sync.remote_path
        """
        for file in files:
            self._upload_single_file(file, remote_path)

    def _upload_single_file(self, file, remote_path_override=None):
        """
        Upload a single file to WebDAV.

        :param file: dict
            - name
            - source
        :param remote_path_override: str or None
        """
        local_path = file["source"]
        filename = file["name"]

        remote_path = remote_path_override or self.config.sync.remote_path
        destination_path = self._build_remote_destination(remote_path, filename)

        logging.info(f"[WebDAVClient] Uploading {local_path} → {destination_path}")

        try:
            self.client.upload_sync(
                remote_path=destination_path,
                local_path=local_path
            )
            logging.info(f"[WebDAVClient] Upload succeeded: {destination_path}")

        except Exception as e:
            logging.error(f"[WebDAVClient] Upload failed for {destination_path}")
            raise UserException(f"WebDAV upload failed: {str(e)}")

    def _build_remote_destination(self, remote_path, filename):
        """
        Generate the remote path (possibly with datetime suffix).

        :param remote_path: base folder on the server
        :param filename: local filename
        :return: str full remote path
        """
        if not self.config.sync.append_datetime:
            final_name = filename
        else:
            base, ext = os.path.splitext(filename)
            suffix = self.config.datetime_suffix
            if ext:
                final_name = f"{base}_{suffix}{ext}"
            else:
                final_name = f"{base}_{suffix}"

        remote_path_clean = remote_path.rstrip("/")
        destination = f"{remote_path_clean}/{final_name}"
        return destination.replace("//", "/")
