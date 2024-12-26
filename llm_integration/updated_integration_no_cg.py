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

    def get_explanation(self, function_code, caller_functions_code=None, callee_functions_code=None):
        # Create the explanation prompt using the required and optional code
        caller_functions_code = caller_functions_code or "Not provided."
        callee_functions_code = callee_functions_code or "Not provided."

        prompt = f"""
        You are an expert code reviewer. Provide a short explanation of the following code block (`function_code`). 

        function_code:
        {function_code}
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
        The following explanation describes a code implementation. Please generate the corresponding code based on the explanation. 
        No need for any other text, information, context, prompt, or explanation.

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
