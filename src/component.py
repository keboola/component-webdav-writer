"""
WebDAV Writer Component main class.
"""
from datetime import datetime, UTC
import logging
from keboola.component.base import ComponentBase
from keboola.component.exceptions import UserException

from configuration import Configuration
from webdav_client import WebDAVClient


class Component(ComponentBase):
    def __init__(self):
        super().__init__()

    def run(self):
        run_time = datetime.now(UTC)
        run_time_str = run_time.strftime("%Y-%m-%dT%H:%M:%SZ")

        logging.info("[WebDAV Writer]: Starting upload process...")

        raw_config = {
            "parameters": self.configuration.parameters,
            "action": getattr(self.configuration, "action", "run")
        }

        config = Configuration(**raw_config)
        client = WebDAVClient(config, self)

        tables = client.scan_table_inputs()
        if tables:
            logging.info(f"[WebDAV Writer]: Uploading {len(tables)} table(s)...")
            client.upload_files(tables)

        files = client.scan_file_inputs()
        if files:
            logging.info(f"[WebDAV Writer]: Uploading {len(files)} file(s)...")
            client.upload_files(files)

        new_state = {
            "last_successful_run": run_time_str
        }

        logging.info("[WebDAV Writer]: Saving component state...")
        self.write_state_file(new_state)

        logging.info("[WebDAV Writer]: Upload process completed successfully.")

"""
Main entrypoint
"""
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    try:
        comp = Component()
        comp.execute_action()
    except UserException as exc:
        logging.exception(exc)
        exit(1)
    except Exception as exc:
        logging.exception(exc)
        exit(2)
