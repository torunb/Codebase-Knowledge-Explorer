import os
import openai
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class AzureOpenAIIntegration:
    def __init__(self):
        # Set the API key and base URL for Azure OpenAI
        openai.api_key = os.getenv("OPENAI_API_KEY")  # Ensure your .env file contains this key
        openai.api_base = os.getenv("OPENAI_API_BASE")  # Example: "https://your-resource-name.openai.azure.com/"
        openai.api_type = "azure"
        openai.api_version = "2023-05-15"  # Update with your Azure OpenAI version

        # Define the deployment name
        self.deployment_name = os.getenv("DEPLOYMENT_NAME")  # Ensure your .env file contains this key

    def get_explanation(self, prompt):
        
        system_message = """
        You are an expert code reviewer providing an explanation of code. 
        Evaluate the following code and explain its functionality, 
        and usage area to a developer who is curious about this code.
        """

        try:
            response = openai.ChatCompletion.create(
                deployment_id=self.deployment_name,  # Use the deployment name from Azure
                model="gpt-4o",  # Replace with your model name
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": prompt},
                ],
            )
            return response["choices"][0]["message"]["content"]
        except Exception as e:
            return f"An error occurred: {e}"
        

    def get_code(self, prompt):
        
        system_message = """
        You are an expert software engineer writing code from the explanation. 
        Evaluate the following explanation and generate code based on this explanation.
        """

        try:
            response = openai.ChatCompletion.create(
                deployment_id=self.deployment_name,  # Use the deployment name from Azure
                model="gpt-4o",  # Replace with your model name
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": prompt},
                ],
            )
            return response["choices"][0]["message"]["content"]
        except Exception as e:
            return f"An error occurred: {e}"



def generate_explanation_and_code():

    with open('code.json') as f:
        code = json.load(f)

    with open('call_graph.json') as f:
        call_graph = json.load(f)

    explanation_file_path = "output_explanation.json"
    code_file_path = "output_code.json"

    prompt = f"""
        You are an expert in code review and explanation. Analyze the following code and its corresponding call graph.

        1. Provide a detailed explanation of the code's functionality.
        2. Discuss its potential use cases and relevance.
        3. Highlight any patterns, optimizations, or potential issues.

        Code:
        {json.dumps(code, indent=4)}

        Call Graph:
        {json.dumps(call_graph, indent=4)}
    """

    azure_integration = AzureOpenAIIntegration()

    explanation_data = {"explanation": azure_integration.get_explanation(prompt)}

    #Write the explanation to a JSON file
    with open(explanation_file_path, "w") as json_file:
       json.dump(explanation_data, json_file, indent=4)


    # Generate code based on the explanation
    code_prompt = f"""
    The following explanation describes a code implementation. Please generate the corresponding code based on the explanation. 
    No need for any other text, information, context, prompt, or explanation.

    Explanation:
    {explanation_data}
    """
    generated_code = azure_integration.get_code(code_prompt)
    code_data = {"code": generated_code}

    # Write the generated code to a JSON file
    with open(code_file_path, "w") as json_file:
        json.dump(code_data, json_file, indent=4)

    return explanation_data, code_data, code


