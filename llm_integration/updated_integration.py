import os
import openai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class UpdatedAzureOpenAIIntegration:
    def __init__(self):
        # Set the API key and base URL for Azure OpenAI
        openai.api_key = os.getenv("OPENAI_API_KEY")  # Ensure your .env file contains this key
        openai.api_base = os.getenv("OPENAI_API_BASE")  # Example: "https://your-resource-name.openai.azure.com/"
        openai.api_type = "azure"
        openai.api_version = "2023-05-15"  # Update with your Azure OpenAI version

        # Define the deployment name
        self.deployment_name = os.getenv("DEPLOYMENT_NAME")  # Ensure your .env file contains this key

    def get_explanation(self, function_code, caller_functions_code, callee_functions_code):
        # Create the explanation prompt using all provided code
        prompt = f"""
        You are an expert code reviewer. Analyze the following code block (`function_code`) in the context of its caller and callee functions.

        1. Provide a detailed explanation of what `function_code` does, referencing relevant context from `caller_functions_code` and `callee_functions_code`.
        2. Include potential use cases, optimizations, and any issues.

        function_code:
        {function_code}

        caller_functions_code:
        {caller_functions_code}

        callee_functions_code:
        {callee_functions_code}
        """

        try:
            response = openai.ChatCompletion.create(
                deployment_id=self.deployment_name,  # Use the deployment name from Azure
                model="gpt-4o",  # Replace with your model name
                messages=[
                    {"role": "system", "content": "You are an expert code reviewer."},
                    {"role": "user", "content": prompt},
                ],
            )
            return response["choices"][0]["message"]["content"]
        except Exception as e:
            return f"An error occurred: {e}"

    def get_code(self, explanation):
        # Create the code-generation prompt using the explanation
        prompt = f"""
        You are an expert software engineer. Based on the following explanation, generate a corresponding implementation in Python:

        Explanation:
        {explanation}
        """

        try:
            response = openai.ChatCompletion.create(
                deployment_id=self.deployment_name,  # Use the deployment name from Azure
                model="gpt-4o",  # Replace with your model name
                messages=[
                    {"role": "system", "content": "You are an expert software engineer."},
                    {"role": "user", "content": prompt},
                ],
            )
            return response["choices"][0]["message"]["content"]
        except Exception as e:
            return f"An error occurred: {e}"
