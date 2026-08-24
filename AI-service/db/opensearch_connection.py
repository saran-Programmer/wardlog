import os

from opensearchpy import OpenSearch

_username = os.environ.get("OPENSEARCH_USERNAME")
_password = os.environ.get("OPENSEARCH_PASSWORD")

client = OpenSearch(
    hosts=[
        {
            "host": os.environ["OPENSEARCH_HOST"],
            "port": int(os.environ["OPENSEARCH_PORT"]),
        }
    ],
    http_auth=(_username, _password) if _username and _password else None,
    use_ssl=os.environ.get("OPENSEARCH_USE_SSL", "false").lower() == "true",
    verify_certs=os.environ.get("OPENSEARCH_VERIFY_CERTS", "false").lower() == "true",
)


def verify_connection() -> None:
    client.info()
