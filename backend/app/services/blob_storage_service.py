import logging
from pathlib import Path

from azure.core.exceptions import ResourceNotFoundError
from azure.storage.blob import BlobServiceClient

logger = logging.getLogger("panganai")


class BlobStorageService:
    def __init__(self, settings):
        self.connection_string = settings.AZURE_STORAGE_CONNECTION_STRING
        self.container_name = settings.AZURE_BLOB_CONTAINER

        if not self.connection_string:
            raise ValueError("AZURE_STORAGE_CONNECTION_STRING tidak boleh kosong.")
        if not self.container_name:
            raise ValueError("AZURE_BLOB_CONTAINER tidak boleh kosong.")

        try:
            self.blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)
            self.container_client = self.blob_service_client.get_container_client(self.container_name)
            self.container_client.get_container_properties()
        except Exception as exc:
            raise RuntimeError("Failed to connect to Azure Blob Storage") from exc

    def _log_blob_metadata(self, blob_client, local_path: Path) -> None:
        try:
            props = blob_client.get_blob_properties()
            logger.info(
                "Blob metadata | name=%s local=%s size=%s last_modified=%s",
                blob_client.blob_name,
                local_path,
                getattr(props, "size", None),
                getattr(props, "last_modified", None),
            )
        except Exception:
            logger.info("Blob metadata | name=%s local=%s (properties unavailable)", blob_client.blob_name, local_path)

    def download_blob_if_needed(self, blob_name: str, local_path: str) -> str:
        target_path = Path(local_path)
        target_path.parent.mkdir(parents=True, exist_ok=True)

        blob_client = self.container_client.get_blob_client(blob_name)
        self._log_blob_metadata(blob_client, target_path)

        if target_path.exists() and target_path.stat().st_size > 0:
            logger.info(
                "Using cached blob | name=%s local=%s file_size=%s",
                blob_name,
                target_path,
                target_path.stat().st_size,
            )
            return str(target_path)

        logger.info("Downloading blob | name=%s local=%s", blob_name, target_path)
        try:
            content = blob_client.download_blob().readall()
            target_path.write_bytes(content)
        except ResourceNotFoundError as exc:
            raise FileNotFoundError(f"Blob not found: {blob_name}") from exc
        except Exception as exc:
            raise RuntimeError(
                f"Failed to download blob: {blob_name} from container: {self.container_name}"
            ) from exc

        logger.info("Downloaded blob | name=%s local=%s file_size=%s", blob_name, target_path, target_path.stat().st_size)
        return str(target_path)

    # Backward compatibility with existing calls.
    def download_if_missing(self, blob_path: str, local_path: str) -> str:
        return self.download_blob_if_needed(blob_path, local_path)
