import base64
import logging
from typing import Dict, Optional, Union

import requests


class NtfyHandler(logging.Handler):

    # default priority to use if a log level is not in range(9, 60)
    DEFAULT_PRIORITY = 3

    # map of rounded log level -> ntfy priority
    LOG_LEVEL_PRIORITY_MAP = {
        logging.DEBUG: 1,
        logging.INFO: 2,
        logging.WARNING: 3,
        logging.ERROR: 4,
        logging.FATAL: 5,
    }

    def __init__(
        self,
        topic_name: str,
        server_url: str = "https://ntfy.sh",
        log_level_priority_map: Optional[Dict[int, int]] = None,
        ntfy_headers: Optional[Dict[str, Union[str, bytes]]] = None,
        access_token: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
    ) -> None:
        """
        :param topic_name: The name of the topic to post messages to
        :type topic_name: str
        :param server_url: The base URL of the ntfy server to utilize,
            defaulting to https://ntfy.sh
        :type server_url: str
        :param log_level_priority_map: A dict of {log_level: ntfy_priority} items,
            where `log_level` is defined as a log_level // 10 * 10,
            and `ntfy_priority` is the priority to use when sending the ntfy message
        :type log_level_priority_map: Optional[Dict[int, int]]
        :param ntfy_headers: A dict of headers to be used when sending a ntfy message
            see this page for valid options:
            https://ntfy.sh/docs/publish/#list-of-all-parameters
        :type ntfy_headers: Optional[Dict[str, Union[str, bytes]]]
        :param access_token: An access token to use when sending a message,
            retrieved from the /account page of a ntfy server.
        :type access_token: Optional[str]
        :param username: A username to use when sending a message
        :type username: Optional[str]
        :param password: A password to use when sending a message
        :type password: Optional[str]
        :rtype: None
        """

        super(NtfyHandler, self).__init__()

        self.topic_url = f"{server_url}/{topic_name}"

        # set user-defined headers
        headers = {}

        if ntfy_headers:
            headers = {k: v for k, v in ntfy_headers.items()}

        # automatically set Authorization header
        # if not set by user
        if "Authorization" not in headers:
            if access_token:
                headers["Authorization"] = f"Bearer {access_token}"
            elif username and password:
                token = base64.b64encode(f"{username}:{password}".encode()).decode()
                headers["Authorization"] = f"Basic {token}"

        self.ntfy_session = requests.Session()
        self.ntfy_session.headers = headers

        self.log_level_priority_map = {}
        if log_level_priority_map:
            # cast keys as int to allow loggingConfig to load from JSON
            for log_level, ntfy_priority in log_level_priority_map.items():
                self.log_level_priority_map[int(log_level)] = ntfy_priority
        else:
            self.log_level_priority_map = NtfyHandler.LOG_LEVEL_PRIORITY_MAP

    def emit(self, record):
        try:
            # set message priority from lookup table
            rounded_level = record.levelno // 10 * 10
            priority = self.log_level_priority_map.get(
                rounded_level, NtfyHandler.DEFAULT_PRIORITY
            )
            self.ntfy_session.headers["X-Priority"] = str(priority)
            self.ntfy_session.headers["X-Title"] = f"{record.levelname}: {record.name}"

            res = self.ntfy_session.post(self.topic_url, data=record.getMessage())
            res.raise_for_status()

        except BaseException:
            self.handleError(record)
