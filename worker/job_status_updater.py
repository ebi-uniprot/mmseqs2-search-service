import json
import logging
import requests


class JobStatusUpdater:
    """Handles updating job status in the database via API call."""

    def __init__(self, api_base_url):
        self.api_base_url = api_base_url

    def update_job_status(self, job_id, job_status, timestamp=None):
        api_url = f"{self.api_base_url}/job/{job_id}"
        logging.info(f"Updating job {job_id} status to {job_status} at {api_url}")

        if timestamp is None:
            payload = {"status": job_status}
        else:
            payload = {"status": job_status, "completed_at": timestamp}

        try:
            logging.info(f"Sending to {api_url} payload: {json.dumps(payload)}")
            response = requests.patch(api_url, json=payload)
            response.raise_for_status()
            logging.info(f"Updated job {job_id} status to {job_status}")
        except requests.RequestException as e:
            logging.error(f"Failed to update job status for {job_id}: {e}")
            raise Exception(f"Failed to update job status for {job_id}: {e}")
