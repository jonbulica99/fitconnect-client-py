import requests
from hashlib import sha512
from fitconnect_client.log import logger
from fitconnect_client.environment import Environment, ENV_CONFIG
from fitconnect_client.objects import Attachment, Submission
from fitconnect_client.objects.exception import APIError
from fitconnect_client.crypto import convert_dict_to_json_bytes, encrypt_dict_with_key, encrypt_bytes_with_key


class FitconnectClient:
    def __init__(self, environment: Environment, client_id: str, client_secret: str):
        self.environment = ENV_CONFIG[environment]
        self.submission_api_url = self.environment.get("SUBMISSION_API")
        self.oauth_api_url = self.environment.get("OAUTH_ENDPOINT")
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = None
        logger.debug(f"Initialized client with: {environment}")

    def obtain_access_token(self) -> str:
        response = requests.post(self.oauth_api_url,
                                 data={
                                     "grant_type": "client_credentials",
                                     "client_id": self.client_id,
                                     "client_secret": self.client_secret
                                 })
        if response.ok:
            self.access_token = response.json().get("access_token")
            logger.debug(f"Obtained access token: {self.access_token}")
            return self.access_token
        raise APIError(f"Failed to obtain access token: {response.content}")

    def get_destination_info(self, destination_id: str) -> dict:
        response = requests.get(f"{self.submission_api_url}/destinations/{destination_id}",
                                headers={"Authorization": f"Bearer {self.access_token}"})
        if response.ok:
            return response.json()
        raise APIError(f"Failed to retrieve destination info for {destination_id}: {response.content}")

    def get_jwk_for_destination(self, destination_id: str) -> dict:
        destination_info = self.get_destination_info(destination_id)
        encryption_kid = destination_info.get("encryptionKid")
        response = requests.get(f"{self.submission_api_url}/destinations/{destination_id}/keys/{encryption_kid}")
        if response.ok:
            return response.json()
        raise APIError(f"Failed to retrieve encryption keys for {destination_id}: {response.content}")

    def create_submission(self, destination_id: str, service_type: str,
                          service_name: str, attachments: list[Attachment] = None) -> Submission:
        submission = Submission(destination_id, service_type, service_name, attachments)
        response = requests.post(f"{self.submission_api_url}/submissions",
                                 headers={"Authorization": f"Bearer {self.access_token}"},
                                 json=submission.get_api_json_impl())
        if response.ok:
            data = response.json()
            submission.submission_id = data.get("submissionId")
            logger.info(f"{submission} created successfully")
            return submission
        raise APIError(f"Failed to create {submission}: {response.content}")

    def upload_attachment(self, submission: Submission, attachment: Attachment, key: dict) -> requests.Response:
        try:
            with open(attachment.path, "rb") as file:
                data = file.read()
        except OSError as e:
            logger.error(f"Could not read {attachment}: {e}")
            data = None

        encrypted_data = encrypt_bytes_with_key(data, key)

        return requests.put(
            f"{self.submission_api_url}/submissions/{submission.submission_id}/attachments/{attachment.id}",
            headers={
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/jose"
            },
            data=encrypted_data)

    def send_submission(self, submission: Submission, metadata: dict) -> dict:
        logger.info(f"Preparing {submission}")

        logger.debug("Obtaining destination encryption keys")
        encryption_keys = self.get_jwk_for_destination(submission.destination_id)

        if submission.attachments:
            logger.info(f"Handling {len(submission.attachments)} attachment(s)")
            for attachment in submission.attachments:
                result = self.upload_attachment(submission=submission, attachment=attachment, key=encryption_keys)
                if result.ok:
                    logger.debug(f"{attachment} uploaded successfully")
                else:
                    raise APIError(f"Failed to upload {attachment}: {result.content}")

        logger.debug("Encrypting metadata")
        encrypted_metadata = self._encrypt_data(metadata, encryption_keys)

        response = requests.put(f"{self.submission_api_url}/submissions/{submission.submission_id}",
                                headers={"Authorization": f"Bearer {self.access_token}"},
                                json={"encryptedMetadata": encrypted_metadata})
        if response.ok:
            logger.info(f"{submission} was sent successfully")
            return response.json()
        raise APIError(f"Failed to submit {submission}: {response.content}")

    @staticmethod
    def create_metadata(submission_date: str,
                        sender_reference: str,
                        submission_schema_url: str,
                        metadata_schema_url: str,
                        email_reply_to: str,
                        attachments: list[Attachment] = None,
                        auth_info: list[dict] = None,
                        payment_info: dict = None) -> dict:
        metadata_template = {
            "contentStructure": {
                "data": {
                    "submissionSchema": {
                        "schemaUri": submission_schema_url,
                        "mimeType": "application/json"
                    }
                    # TODO: implement
                    # "hash": {
                    #    "type": "sha512",
                    #    "content": content_hash
                    # }
                },
                "attachments": [attachment.get_api_metadata_impl() for attachment in attachments] if attachments else []
            },
            "replyChannel": {
                # TODO: implement other reply channels
                "eMail": {
                    "address": email_reply_to
                }
            },
            "additionalReferenceInfo": {
                "senderReference": sender_reference,
                "applicationDate": submission_date
            }
        }
        if metadata_schema_url:
            # $schema could be null in newer versions
            metadata_template["$schema"] = metadata_schema_url
        if auth_info:
            metadata_template["authenticationInformation"] = auth_info
        if payment_info:
            metadata_template["paymentInformation"] = payment_info

        return metadata_template

    @staticmethod
    def _hash_data(data) -> str:
        if isinstance(data, dict):
            data = convert_dict_to_json_bytes(data)
        elif isinstance(data, str):
            data = data.encode('utf-8')
        return sha512(data).hexdigest()

    @staticmethod
    def _encrypt_data(payload: dict, encryption_keys: dict) -> str:
        return encrypt_dict_with_key(payload, encryption_keys)
