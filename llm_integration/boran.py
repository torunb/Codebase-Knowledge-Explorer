import os
import csv
import openai
from openai import OpenAI
from dotenv import load_dotenv
import json
import time

load_dotenv()



class OpenAIIntegration:
    def __init__(self):
        self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

    def get_chat_response(self, prompt, role="user"):
        system_message = "You are an expert code reviewer providing feedback on code comments. Evaluate the following comment and label it based on common code comment smells."

        # specified model and messages
        completion = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_message},
                {"role": role, "content": prompt}
            ],
            temperature = 0.2, #deterministic
            max_tokens=10
        )
        
        # Return the response content
        return completion.choices[0].message.content

taxonomy = """
Misleading: 
Description: Comments that do not accurately represent what the code does 
Example: public int add(int x, int y){
// Returns x - y
return x + y;
} 

Obvious: 
Description: Comments that restate what the code does in an obvious manner 
Example: count = 0; // assigning count a value of 0 

Commented-out code:
Description: A code piece that is commented out 
Example: //facade.registerProxy(newSoundAssetProxy()); 

Irrelevant:
Description: Comments that do not intend to explain the code
Example: /* I dedicate all this code, all my work, to my wife,
Darlene, who will have to support me and our children
and the dog once it gets released into the public.*/

Task
Description: Comments explaining the work that could/should be done in future or was already completed
Example: // TODO: clear and optimize this code later 

Too much information:
Description: Overly verbose comments
Example: // this makes a new scanner, which can read from
// STDIN, located at System.in. The scanner lets us look
// for tokens, aka stuff the user has entered.
Scanner sc = new Scanner(System.in);

Attribution:
Description: Comments that give information about who wrote the code 
Example: /* Added by Rick */ 7

Beautification:
Description: Comments that aim to distinguish the parts of the code
Example:
//*********************
// VARIABLES
//*********************

Non-local:
Description: Comments that provide systemwide information or mention code that is not near
Example: public void setFitnessePort(int fitnessePort) {
// Port on which fitnesse would run. Defaults to 8082
this.fitnessePort = fitnessePort;
}

Vague:
Description: Comments that are not clearly understandable 
Example: taskTmpPath = ttp; //_task_tmp 

Not a smell:
Description:
- Provides useful context or explanation that enhances code comprehension.
- Clarifies the purpose or intent of the code.
- Warns about potential issues or edge cases.
- Documents complex algorithms or business logic.
- Follows best practices for commenting style and clarity.
"""


# Read comment-label pairs
with open("boran_dataset.json", 'r') as json_file:
    data = json.load(json_file)

num_comments = len(data)

openai_integration = OpenAIIntegration()

csv_file_path = "output_results_gpt4_ipek.csv"

with open(csv_file_path, mode="a", newline='') as  csv_file:
    csv_writer = csv.writer(csv_file)

    csv_writer.writerow(["comment", "label", "gpt prediction"])
    true_predictions = 0


    for entry in data:
        comment = entry['comment']
        label = entry['label']
        code = entry['code']
        
        prompt = f"""
        Code comments are considered to be smells if they degrade software quality \
        or comments that do not actually help readers much in terms of code comprehension. 
        They are bad practices for software development. You will be provided with \
        a Taxonomy of 10 Inline Code Comment Smells delimited by triple quotes. 
        Taxonomy includes descriptions and examples for each smell type.

        '''{taxonomy}'''

        Now I will provide you code comment delimited by double quotes and related code \
        segment delimited by double quotes. \
        Your task is to consider if the given inline code comment within the given code segment \
        and label it according to the given taxonomy if it is a comment smell. \
        If the given comment is not a smell, label the comment as "not a smell"
        Give the answer as one of the following: [Misleading, Obvious, Commented out code, Irrelevant, \ 
        Task, Too much info, Beautification, Nonlocal info, Vague, Not a smell]
        Make sure to select only one category as the answer.

        Make sure to select only one category as the answer.

        Additionally, a comment can be considered "not a smell" if it:
        - Provides useful context or explanation that enhances code comprehension.
        - Clarifies the purpose or intent of the code.
        - Warns about potential issues or edge cases.
        - Documents complex algorithms or business logic.
        - Follows best practices for commenting style and clarity.

        Code comment: ''{comment}''
        Code segment: ''{code}''
        """

        response = openai_integration.get_chat_response(prompt, role="user")

        print(f"Comment: {comment}")
        print(f"Label (ground truth): {label}")
        print(f"GPT Prediction: {response}\n")

        if label.lower() == response.lower():
            true_predictions += 1
        
        csv_writer.writerow([comment, label, response])
        time.sleep(20)

accuracy = true_predictions/num_comments
print(f"Accuracy is: {accuracy}")
    

