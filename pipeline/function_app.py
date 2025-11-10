import azure.functions as func
import azure.durable_functions as df
import json
from activities import callAoai, sharepointLookup
from configuration import Configuration
import logging
from pipelineUtils.prompts import load_prompts
from pipelineUtils.azure_openai import run_prompt

config = Configuration()

NEXT_STAGE = config.get_value("NEXT_STAGE")

app = df.DFApp(http_auth_level=func.AuthLevel.ANONYMOUS)

import logging


# An HTTP-triggered function with a Durable Functions client binding
@app.route(route="client")
@app.durable_client_input(client_name="client")
async def start_orchestrator_http(req: func.HttpRequest, client):
  """
  Starts a new orchestration instance and returns a response to the client.

  args:
    req (func.HttpRequest): The HTTP request object. Contains an array of JSONs with fields: 
    {
        "records": [
            {
             "title": "Sample Title",
             "siteUrl": "https://contoso.sharepoint.com/sites/Marketing",
            }
        ]
    }

    client (DurableOrchestrationClient): The Durable Functions client.
  response:
    func.HttpResponse: The HTTP response object.
  """
  
  #Perform basic validation on the request body
  try:
      body = req.get_json()
  except ValueError:
      return func.HttpResponse("Invalid JSON request", status_code=400)

  records = body.get("records")
  
  #invoke the orchestrator function with the list of records
  instance_id = await client.start_new('orchestrator', client_input=records)
  logging.info(f"Started orchestration with Batch ID = '{instance_id}'.")

  response = client.create_check_status_response(req, instance_id)
  return response

# Orchestrator
@app.function_name(name="orchestrator")
@app.orchestration_trigger(context_name="context")
def run(context):
    records_array = context.get_input()
    logging.info(f"Context {context}")
    logging.info(f"Input data: {records_array}")
    logging.info(f"Number of records to process: {len(records_array)}")

    # file_path = 'data/jobCategoryMapping.json'
    # Get Job Category mappings from local files data/jobCategoryMapping.json

    for record in records_array:
        logging.info(f"Processing record: {record}")
        title = record.get('title')
        siteUrl = record.get('siteUrl')

        sharepointInput = {
            "title": title,
            "siteUrl": siteUrl
        }
        logging.info(f"Sharepoint Input: {sharepointInput}")
        sharepointOutput = yield context.call_activity("sharepointLookup", sharepointInput)
        logging.info(f"Sharepoint Output: {sharepointOutput}")
        call_aoai_input = {
            "vendor_history": sharepointOutput.get('vendor_history'),
            "current_record": record.get('current_record'),
            "instance_id": context.instance_id
        }

        aoaiOutput = yield context.call_activity("callAoai", call_aoai_input)
        logging.info(f"AOAI Output: {aoaiOutput}")

    return {
        "aoaiOutput": aoaiOutput
    }

app.register_functions(sharepointLookup.bp)
app.register_functions(callAoai.bp)