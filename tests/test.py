import pytest
import os

from retarus.fax.client import FaxClient
from retarus.fax.model import SendRecipient, Job, Document, BulkRequest
from retarus.commons.config import Configuration


def init():
    Configuration.set_auth(os.environ["retarus_userid"], os.environ["retarus_fax_password"])
    Configuration.customer_number = os.environ["retarus_customer_number"]


init()

# Test variables
test_job_id = ""

sdk = FaxClient(True)


@pytest.mark.asyncio
async def test_send_fax_job():
    global test_job_id
    doc = Document.from_path("tests/assets/test.pdf")
    recipients = SendRecipient(number="4900000000000")
    job = Job(recipients=[recipients], documents=[doc])
    job_id = await sdk.client.send_fax_job(job)
    print(job_id)
    test_job_id = job_id["jobId"]
    assert job_id != ""


@pytest.mark.asyncio
async def test_get_fax_report():
    global test_job_id
    res = await sdk.client.get_fax_report(test_job_id)
    print(res)
    assert isinstance(res, dict)
    assert res["pages"] == 0


@pytest.mark.asyncio
async def test_get_fax_reports():
    res = await sdk.client.get_fax_reports()
    assert isinstance(res, dict)
    assert "reports" in res


@pytest.mark.asyncio
async def test_delete_fax_report():
    global test_job_id
    res = await sdk.client.delete_fax_report(test_job_id)
    assert res["jobId"] == test_job_id
    assert res["deleted"] is True


@pytest.mark.asyncio
async def test_delete_fax_reports():
    doc = Document.from_path("tests/assets/test.pdf")
    recipients = SendRecipient(number="4900000000000")
    job = Job(recipients=[recipients], documents=[doc])
    res1 = await sdk.client.send_fax_job(job)
    res2 = await sdk.client.send_fax_job(job)
    xy = [res1, res2]

    bulk = BulkRequest(action="DELETE", jobIds=xy)
    res = await sdk.client.bulk_operation(payload=bulk)
    print(res)
    assert "reports" in res
    assert len(res["reports"]) != 0
