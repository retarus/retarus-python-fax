import pytest
import os

from retarus.fax_in_poll.client import FaxInPollClient
from retarus.commons.config import Configuration
import tomllib
import os
import json


def _load_conf():
    with open("retarus-python-fax/test_env.toml", "rb") as conf:
        return tomllib.load(conf)


def set_env():
    config_data = _load_conf()
    for key, value in config_data.items():
        if type(value) == list:
            os.environ[key] = json.dumps(value)
            continue
        for k, v in value.items():
            os.environ[k] = str(v)

# Unit test vaiables
set_env()
Configuration.set_auth(os.environ["retarus_polling_user"], os.environ["retarus_polling_password"])
TOPIC = os.environ["topic"]
jobs = []

sdk = FaxInPollClient(True, timeout=5)



@pytest.mark.asyncio
async def test_create_instance_of_client():
    # Check if a client can be created
    client = FaxInPollClient(True)
    assert isinstance(client, FaxInPollClient)


@pytest.mark.asyncio
async def test_list_fax_jobs():
    global sdk
    global jobs
    Configuration.set_auth(os.environ["retarus_topic_user"], os.environ["retarus_topic_password"])
    res = await sdk.client.fetch_fax_list(TOPIC)
    print(res)
    jobs = [x for x in res["results"]]

    if isinstance(res, bool):
        assert res
    assert len(res) >= 1


@pytest.mark.dependency("test_list_fax_jobs")
@pytest.mark.asyncio
async def test_download_fax():
    global sdk
    Configuration.set_auth(os.environ["retarus_topic_user"], os.environ["retarus_topic_password"])
    url = "9201291.pdf"
    res = await sdk.client.download_fax(url)
    with open(url, "rb") as file:
        assert len(file.read()) != 0


@pytest.mark.dependency("test_download_fax")
@pytest.mark.asyncio
async def test_acknowledge_fax():
    global sdk
    global jobs
    Configuration.set_auth(os.environ["retarus_topic_user"], os.environ["retarus_topic_password"])
    res = await sdk.client.acknowledge_fax(TOPIC, jobs)