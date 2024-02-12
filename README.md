# fitconnect-client-py
This is a python SDK for the German [FIT-Connect](https://docs.fitko.de/fit-connect/docs/) system. This is still a work in progress, it should however be possible to make simple submissions.

## Usage

```python3
from fitconnect_client import FitconnectClient, Environment, Attachment

client = FitconnectClient(Environment.TESTING,
                          client_id="b00ffff-xxxx-xxxxxxxxxxxxxxx-xxxx",
                          client_secret="HZ-xxxx-xxxxxxxxxxxxxxx-xxxx")
client.obtain_access_token()

DESTINATION_ID = "b00ffff-xxxxxx-xxxxxxxxxxxxx-xxxx"
SERVICE_IDENTIFIER = "urn:de:fim:leika:leistung:xxxxxxxxxxxxxxxxxxxx"
SUBMISSION_SCHEMA_URL = "https://schema.fitko.de/fim/xxxxxxxxxxx.schema.json"
METADATA_SCHEMA_URL = "https://schema.fitko.de/fit-connect/metadata/1.0.0/metadata.schema.json"

attachments = [
    Attachment("file1.pdf"),
    Attachment("/full/path/to/file2.pdf")]

metadata = client.create_metadata(submission_date=datetime.today().strftime("%d.%m.%Y"),
                                  sender_reference="ref-XXXXXXXX",
                                  submission_schema_url=SUBMISSION_SCHEMA_URL,
                                  metadata_schema_url=METADATA_SCHEMA_URL,
                                  email_reply_to="sender@example.com",
                                  attachments=attachments)
submission = client.create_submission(destination_id=DESTINATION_ID,
                                      service_type=SERVICE_IDENTIFIER,
                                      service_name="Service Name based on SERVICE_IDENTIFIER",
                                      attachments=attachments)
client.send_submission(submission, metadata=metadata)
```

Currently, the SDK can only make submissions and not receive them. 

## Disclaimer
This is still work-in-progress and is provided as-is. Use at your own risk. I am not liable for anything you might do with this script.

## LICENSE
See `LICENSE`.
