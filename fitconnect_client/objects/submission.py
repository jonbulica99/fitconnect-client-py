from fitconnect_client.objects.attachment import Attachment


class Submission:
    def __repr__(self) -> str:
        return f"Submission<{self.submission_id or 'new'}>({self.service_name})"

    def __init__(self, destination_id: str,
                 service_identifier: str,
                 service_name: str,
                 attachments: list[Attachment]) -> None:
        self.submission_id = None
        self.destination_id = destination_id
        self.service_identifier = service_identifier
        self.service_name = service_name
        self.attachments = attachments

    def get_api_json_impl(self) -> dict:
        return {
            "destinationId": self.destination_id,
            "serviceType": {
                "name": self.service_name,
                "identifier": self.service_identifier
            },
            "announcedAttachments": self.get_attachment_ids()}

    def get_attachment_ids(self) -> list[str]:
        return [attachment.id for attachment in self.attachments]
