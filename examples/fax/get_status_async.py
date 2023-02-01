import asyncio
import os
from dotenv import load_dotenv 

from retarus.fax.model import Document, Job, SendRecipient
from retarus.commons.config import Configuration
from retarus.fax.client import FaxClient
from retarus.commons.region import Region

'''
How to use this example
1. Setup the SDK like described in the README file on top level of the repository. If 
   you need additonal help, please have a look at our OpenAPI here: 
   https://developers.retarus.com/docs/fax/api/sending-fax/
2. Create an .env file somewhere in your project. It must at least contain key / value
   pairs of "retarus_userid" and "retarus_fax_password" and may also contain 
   "retarus_customer_number" if you want to reference that too. You need the values to
   authenticate and optionally set the customer number as can be seen below. An entry 
   looks like this:
   retarus_userid=user123
   We recommend to create the .env file on the same level as this script.
3. You can either retrieve the status for an individual job ID or all currently 
   available fax jobs. To do so, just comment our or in the handling at the bottom
   of this example.
     a) Getting the status of an individual job
        This requires that you send a fax job request first with the send function.
        The example will overtake the test PDF from the assets folder in the fax examples.
        Feel free to set any other path you like in the read_document function. Also, you
        should replace the recipient number in the main function by your own one to see a
        result when you send a fax.
        After that, you use status() with the job ID you just created.
     b) Getting the status of all currently available jobs
        You do not need a new job for that if you already have at least one. In any case,
        you execute status() with no argument.
     c) we have added some little examples that you can use to play with the retrieved data.
        Feel free to comment them in and try them out as you like.
4. When you are satisfied with your settings, execute this script. Feel free to adjust
   the status handling in the way you like it.
'''


def initialize():
    # Here, you overtake credentials and customer number from the .env file and configure the SDK.
    Configuration.set_auth(os.environ["retarus_userid"], os.environ["retarus_fax_password"])
    Configuration.customer_number = os.environ["retarus_customer_number"]
    # You can choose from the regions Europe, America, Switzerland and Singapore
    Configuration.set_region(Region.Europe)

    # create a new recipient, read a file and return create a new document instance
    job = Job(recipients=[SendRecipient(number="+4900000000000")], documents=[Document.from_path("./assets/test.pdf")])
    return job


async def send(job):
    # create a new client instance
    sdk = FaxClient(True)

    # send the fax to process via the client instance we just created
    id = await sdk.client.send_fax_job(job)
    print("Fax job was sent successfully, you can track it with job ID " + id['jobId'])
    return id['jobId']


async def status(id = None):
    sdk = FaxClient(True)

    if id == None:
        res = await sdk.client.get_fax_reports()
    else:
        res = await sdk.client.get_fax_report(id)
    return res


# Prints all jobs where the status is not "OK"
def get_failed_jobs(jobs):
    for job in jobs["reports"]:
        if job["recipientStatus"][0]['status'] != "OK":
            job_id = job["jobId"]
            print("Job with job ID {} failed with status {}".format(job_id, job["recipientStatus"][0]['status']))


# Creation of a simple log file  
def log_job_ids(jobs):
    if os.path.exists("./assets/fax_job_ids.txt"):
        with open("./assets/fax_job_ids.txt", "r+") as f:
            for job in jobs["reports"]:
                job_exists = False
                f.seek(0)
                for line in f:
                    if job["jobId"] in line:
                        job_exists = True
                if not job_exists:
                    f.write("Job ID: " + job["jobId"] + "\n")
    else:
        print("Missing log file, please add one or adjust the path above.")


if __name__ == "__main__":
    load_dotenv()
    job = initialize()

    # get status for an individual job (id)
    id = asyncio.run(send(job))
    res = asyncio.run(status(id))

    # get report for all currently available fax jobs
    # res = asyncio.run(status())
    
    # sample operations for the further processing of report data
    print(res)
    # get_failed_jobs(res)
    # log_job_ids(res)

