import pandas as pd
from azure.storage.blob import BlobServiceClient
from io import StringIO
import datetime

# This is the full SAS URL for the *account*, which includes ?sv=...&sig=...
# e.g. "https://mystorageacct.blob.core.windows.net?sv=2021-08-06&ss=b&srt=sco&sp=rwlacx&se=..."
ACCOUNT_SAS_URL = "https://heiaepin001dwehitt01.blob.core.windows.net/sip?sp=rw&st=2024-12-26T05:56:04Z&se=2024-12-26T13:56:04Z&skoid=aadf5aea-c5a4-4f96-a295-4b1c269948b4&sktid=66e853de-ece3-44dd-9d66-ee6bdf4159d4&skt=2024-12-26T05:56:04Z&ske=2024-12-26T13:56:04Z&sks=b&skv=2022-11-02&spr=https&sv=2022-11-02&sr=c&sig=epxSBA0gJHNBf3icCmso7UvN0E6RHDNyGsKGiJd1fwI%3D"

CONTAINER_NAME = "sip"

def upload_dataframe_with_sas(df, file_name):

    # Convert to CSV in-memory
    csv_buffer = StringIO()
    df.to_csv(csv_buffer, index=False)

    # Initialize the client with the account-level SAS URL
    blob_service_client = BlobServiceClient(account_url=ACCOUNT_SAS_URL)

    # Access the container client
    container_client = blob_service_client.get_container_client(CONTAINER_NAME)
    try:
        container_client.create_container()
    except Exception:
        pass  # Container might already exist, that's okay

    # Upload to blob
    blob_client = container_client.get_blob_client(file_name)
    blob_client.upload_blob(csv_buffer.getvalue(), overwrite=True)

    print(f"Uploaded CSV to blob: {file_name}")
