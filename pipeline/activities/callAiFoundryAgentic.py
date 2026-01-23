import azure.durable_functions as df
import asyncio
import logging
from agent_framework.azure import AzureAIAgentClient

from pipelineUtils.agent_functions import create_word_document, agent_context
from configuration import Configuration

name = "callAiFoundryAgentic"
bp = df.Blueprint()

config = Configuration()


AGENT_INSTRUCTIONS = """You are a document processing assistant. Your task is to analyze the provided document text and create a well-formatted Word document summary.

When processing the document:
1. Identify the main topics and key points
2. Create a clear, descriptive title for the document
3. Write a brief executive summary (2-3 sentences)
4. Organize the main content in a logical, readable format

You MUST use the create_word_document tool to generate the output document. The tool will save the document to blob storage automatically.

Always call the create_word_document tool with:
- title: A descriptive title for the document
- summary: A brief executive summary
- content: The main organized content (use newlines to separate paragraphs)
"""


async def run_agent(document_text: str, blob_name: str) -> str:
    """
    Runs the Azure AI Foundry agent to process the document and create a Word document.

    Args:
        document_text (str): The extracted document text to process.
        blob_name (str): The original blob name for naming the output file.

    Returns:
        str: The result message from the agent.
    """
    # Load config values at runtime (not import time) to avoid startup failures
    azure_ai_project_endpoint = config.get_value("AZURE_AI_PROJECT_ENDPOINT")
    openai_model = config.get_value("OPENAI_MODEL")

    # Set context for the tool to access
    agent_context['blob_name'] = blob_name

    async with AzureAIAgentClient(
        project_endpoint=azure_ai_project_endpoint,
        model_deployment_name=openai_model,
        credential=config.credential,
    ).as_agent(
        name="DocumentProcessor",
        instructions=AGENT_INSTRUCTIONS,
        tools=create_word_document
    ) as agent:
        prompt = f"Please analyze the following document text and create a Word document summary:\n\n{document_text}"
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
