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



if __name__ == "__main__":

    with open('code.json') as f:
        code = json.load(f)

    with open('call_graph.json') as f:
        call_graph = json.load(f)

    explanation_file_path = "output_explanation.json"

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

    explanation_data = {"prompt": prompt, "explanation": azure_integration.get_explanation(prompt)}

    #Write the explanation to a JSON file
    with open(explanation_file_path, "w") as json_file:
       json.dump(explanation_data, json_file, indent=4)


# import os
# import csv
# import json
# import openai
# from openai import OpenAI
# from dotenv import load_dotenv
# import json
# import time

# load_dotenv()


# # Set API key and endpoint for Azure OpenAI
# openai.api_key = os.getenv("AZURE_OPENAI_API_KEY")
# openai.api_base = os.getenv("AZURE_OPENAI_ENDPOINT")
# openai.api_type = "azure"
# openai.api_version = "2023-05-15"  # Use the correct API version for Azure OpenAI

# class OpenAIIntegration:
#     def __init__(self):
#         self.deployment_name = "gpt-4o"  # Replace with your Azure deployment name

#     def get_explanation(self, prompt, role="user"):
        
#         system_message = """
#         You are an expert code reviewer providing an explanation of code. 
#         Evaluate the following code and explain its functionality, 
#         and usage area to a developer who is curious about this code.
#         """

#         # specified model and messages
#         completion = openai.ChatCompletion.create(
#             engine=self.deployment_name,  # Use the deployment name
#             model="gpt-4o",
#             messages=[
#             {"role": "system", "content": system_message},
#             {"role": role, "content": prompt}
#             ],
#             temperature = 0.2, #deterministic
#             #max_tokens=10
#         )
        
#         # Return the response content
#         return completion["choices"][0]["message"]["content"]
    
#     def get_code(self, prompt, role="user"):
        
#         system_message = """
#         You are an expert software engineer writing code from the explanation. 
#         Evaluate the following explanation and generate code based on this explanation.
#         """

#         # specified model and messages
#         completion = openai.ChatCompletion.create(
#             engine=self.deployment_name,  # Use the deployment name
#             model="gpt-4o",
#             messages=[
#             {"role": "system", "content": system_message},
#             {"role": role, "content": prompt}
#             ],
#             temperature = 0.2, #deterministic
#             #max_tokens=10
#         )
        
#         # Return the response content
#         return completion["choices"][0]["message"]["content"]
    
# with open('code.json') as f:
#     code = json.load(f)

# with open('call_graph.json') as f:
#     call_graph = json.load(f)

# explanation_file_path = "output_explanation.json"


# prompt = """

# Explain the functionality of the following code, which we also provide its call graph.

# Code: {code}

# Call Graph: {call_graph}

# """

# explanation_data = {"prompt": prompt, "explanation": OpenAIIntegration().get_explanation(prompt)}

# # Write the explanation to a JSON file
# with open(explanation_file_path, "w") as json_file:
#     json.dump(explanation_data, json_file, indent=4)


