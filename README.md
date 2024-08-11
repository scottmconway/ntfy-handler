# ntfy-handler
This repo contains an extremely simple logging handler that relays log events to ntfy.

## Installation
`pip install ntfy-handler`

## Usage
```python
import logging
from ntfy_handler import NtfyHandler

logger = logging.getLogger()
logging.basicConfig()

nh = NtfyHandler(topic_name="my_topic")
logger.addHandler(nh)

logger.info("Info!")
```

## Advanced Options
In addition to `topic_name`, the following parameters can be passed to a NtfyHandler during construction:

|Parameter Name|Type|Description|Default Value|
|-|-|-|-|
|`server_url`|`str`|The base URL of the ntfy server to utilize.|`"https://ntfy.sh"`|
|`log_level_priority_map`|`Optional[Dict[int, int]]`|A dict of `{log_level: ntfy_priority}` items, where `log_level` is defined as a log\_level // 10 * 10, and `ntfy_priority` is the priority to use when sending the ntfy message.|See below|
|`ntfy_headers`|`Optional[Dict[str, Union[str, bytes]]]`|A dict of headers to be used when sending a ntfy message.|`None`|
|`access_token`|`Optional[str]`|An access token to use when sending a message, retrieved from the /account page of a ntfy server.|`None`|
|`username`|`Optional[str]`|A username to use when sending a message|`None`|
|`password`|`Optional[str]`|A password to use when sending a message|`None`|

### `ntfy_headers`
If advanced functionality is desired, custom headers can be passed to each request made by the NtfyHandler with this parameter. See [this page](https://ntfy.sh/docs/publish/#list-of-all-parameters) for an up-to-date list of the headers that ntfy uses.

The `Authorization` header may be set here. If it is, `access_token`, `username`, and `password` will not override the manually set value.

The `X-Title` and `X-Priority` headers will be overridden for each log record, so setting them here would be ineffectual.

### `log_level_priority_map`
By default, log levels are mapped to their corresponding priorities in ntfy (defined [here](https://ntfy.sh/docs/publish/#message-priority)). However, a custom mapping from log level -> ntfy priority can be defined with the `log_level_priority_map` parameter when constructing a NtfyHandler.

The default map is as follows:
```
{
    logging.DEBUG: 1,
    logging.INFO: 2,
    logging.WARNING: 3,
    logging.ERROR: 4,
    logging.FATAL: 5,
}
```

Levels for log records are truncated to the nearest 10, to normalize them into the above options. With the default configuration, a log record with a level outside of `range(9, 60)` will be sent with ntfy's default priority (3).
To customize this option, provide a dict with keys set to log levels truncated to the nearest 10 and values set to the ntfy priorities to be used for those levels.
