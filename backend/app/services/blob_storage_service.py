from pathlib import Path

from azure.storage.blob import BlobServiceClient
from azure.core.exceptions import ResourceNotFoundError


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

    def download_if_missing(self, blob_path: str, local_path: str) -> str:
        target_path = Path(local_path)
        target_path.parent.mkdir(parents=True, exist_ok=True)

        if target_path.exists() and target_path.stat().st_size > 0:
            print(f"Using cached file: {target_path}")
            return str(target_path)

        print(f"Downloading blob: {blob_path} -> {target_path}")
        try:
            blob_client = self.container_client.get_blob_client(blob_path)
            content = blob_client.download_blob().readall()
            target_path.write_bytes(content)
        except ResourceNotFoundError as exc:
            raise FileNotFoundError(f"Blob not found: {blob_path}") from exc
        except Exception as exc:
            raise RuntimeError(
                f"Failed to download blob: {blob_path} from container: {self.container_name}"
            ) from exc
        print(f"Downloaded: {target_path}")
        return str(target_path)
