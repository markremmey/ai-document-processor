import azure.durable_functions as df

import logging
import os
import json

name = "sharepointLookup"
bp = df.Blueprint()

@bp.function_name(name)
@bp.activity_trigger(input_name="inputData")
def sharepointLookup(inputData: dict):
  # Implement lookup logic here
  try:
    logging.info(f"sharepointLookup.py: Input Data: {inputData}")
    title = inputData.get('title')
    dummySharepointRecord = {'current_record': 'INSERT THE CURRENT RECORD FROM SHAREPOINT TO ASSESS', 'vendor_history': f'Sharepoint record for title {title}'}
    return dummySharepointRecord
  except Exception as e:
      logging.error(f"Error in Sharepoint Lookup Activity: {e}")
      return None