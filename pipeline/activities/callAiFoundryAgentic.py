import azure.durable_functions as df
import asyncio
import logging
import os
from agent_framework.azure import AzureAIAgentClient
from azure.identity.aio import DefaultAzureCredential as AsyncDefaultAzureCredential

from configuration import Configuration

# Import agent tools from pipelineUtils/agents
from pipelineUtils.agents import create_word_document, set_word_doc_context, get_weather

# Import agent instructions from pipelineUtils
from pipelineUtils.agentic_instructions import (
    DOCUMENT_PROCESSOR_INSTRUCTIONS,
    WEATHER_AGENT_INSTRUCTIONS,
)

name = "callAiFoundryAgentic"
bp = df.Blueprint()

config = Configuration()
AZURE_AI_PROJECT_ENDPOINT = config.get_value("AZURE_AI_PROJECT_ENDPOINT")
OPENAI_MODEL = config.get_value("OPENAI_MODEL")


def _get_async_credential() -> AsyncDefaultAzureCredential:
    """
    Creates an async Azure credential matching the Configuration pattern.
    """
    tenant_id = os.environ.get('AZURE_TENANT_ID', "*")

    if os.environ.get("AZURE_FUNCTIONS_ENVIRONMENT") == "Development":
        return AsyncDefaultAzureCredential(
            additionally_allowed_tenants=tenant_id,
            exclude_environment_credential=True,
            exclude_managed_identity_credential=True,
            exclude_cli_credential=False,
            exclude_powershell_credential=False,
            exclude_shared_token_cache_credential=True,
            exclude_developer_cli_credential=False,
            exclude_interactive_browser_credential=True
        )
    else:
        return AsyncDefaultAzureCredential(
            additionally_allowed_tenants=tenant_id,
            exclude_environment_credential=True,
            exclude_managed_identity_credential=False,
            exclude_cli_credential=True,
            exclude_powershell_credential=True,
            exclude_shared_token_cache_credential=True,
            exclude_developer_cli_credential=True,
            exclude_interactive_browser_credential=True
        )


async def run_agent(document_text: str, blob_name: str) -> str:
    """
    Runs the Azure AI Foundry agent to process the document and create a Word document.

    Args:
        document_text (str): The extracted document text to process.
        blob_name (str): The original blob name for naming the output file.

    Returns:
        str: The result message from the agent.
    """
    # Set context for the word document tool
    set_word_doc_context(blob_name=blob_name)

    async with (
        _get_async_credential() as credential,
        AzureAIAgentClient(
            project_endpoint=AZURE_AI_PROJECT_ENDPOINT,
            model_deployment_name=OPENAI_MODEL,
            async_credential=credential,
            agent_name="DocumentProcessor"
        ).as_agent(
            instructions=DOCUMENT_PROCESSOR_INSTRUCTIONS,
            tools=create_word_document
        ) as agent,
    ):
        prompt = f"Please analyze the following document text and create a Word document summary:\n\n{document_text}"
        result = await agent.run(prompt)
        return result.text


async def run_weather_agent(location: str) -> str:
    """
    Sample agent that gets weather for a location.
    
    Args:
        location (str): The location to get weather for.

    Returns:
        str: The weather information from the agent.
    """
    async with (
        _get_async_credential() as credential,
        AzureAIAgentClient(
            project_endpoint=AZURE_AI_PROJECT_ENDPOINT,
            model_deployment_name=OPENAI_MODEL,
            async_credential=credential,
            agent_name="WeatherAssistant"
        ).as_agent(
            instructions=WEATHER_AGENT_INSTRUCTIONS,
            tools=get_weather
        ) as agent,
    ):
        prompt = f"What's the weather like in {location}?"
        result = await agent.run(prompt)
        return result.text


@bp.function_name(name)
@bp.activity_trigger(input_name="inputData")
def run(inputData: dict):
    """
    Calls the Azure AI Foundry Agentic service to process a document and create a Word document.

    Args:
        inputData (dict): Dictionary containing:
            - text_result (str): The extracted document text to process.
            - instance_id (str): The instance ID for logging purposes.
            - blob_name (str, optional): The original blob name for naming output.

    Returns:
        str: The result from the Azure AI Foundry agent.
    """
    try:
        text_result = inputData.get('text_result', '')
        instance_id = inputData.get('instance_id')
        blob_name = inputData.get('blob_name', f'document_{instance_id}')

        logging.info(f"callAiFoundryAgentic.py: Processing document for instance {instance_id}")

        # Run the async agent function
        response = asyncio.run(run_agent(text_result, blob_name))

        logging.info(f"callAiFoundryAgentic.py: Document processed for instance {instance_id}")

        return response

    except Exception as e:
        logging.error(f"Error processing callAiFoundryAgentic for instance {instance_id}: {e}")
        raise
