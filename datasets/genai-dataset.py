import boto3
import csv
import json

DATASET_SIZE = 50
# [SCAM or LEGIT] - update the prompt accordingly
SCENARIO = "LEGIT"

prompt = """
Human: Rewrite the below phone transcript. Incorporate defined Input Rules, Scam call examples, Non-scam call examples, and Output Rules.  

Input Rules:

* Use supplied data points to create a Non-Scam call example phone transcript.

Scam Call Examples

* A scammer often tries to make the situation urgent
* A scammer often cannot provide proper identification
* A scammer often cannot provide the information requested by the helpdesk operator
* A scammer tries to act like a real employee of the company when in fact they are not
* A scammer often uses the name of a real employee of the company
* A scammer will sometimes use words like "I lost", "emergency", "shutdown", "extremely important", "security risk", "you don't seem to understand", "highly critical", and "if this doesn't happen my boss will fire me"
* A scammer can sometimes not be cooperative
* A scammer can sometimes pretend to be cooperative but ultimately does not cooperate
* A scammer will often provide seemingly legitimate data that is actually fake data

Non-Scam Call Examples

* Is usually very cooperative
* Can usually provide proper and valid identification as requested by the Helpdesk operator
* Not often, but may sometimes forget employee details like employee ID number and office phone number, but will remember other information such as full name or the last 4 digitis of their social security number
* May sometimes express anxiety, embarassment, or impatience, but ultimately cooperates.

Output Rules:

* Output should consist of the following:
    * The phone transcript should either be an employee who is performing a scam call example or a non-scam call example who calls a helpdesk operator.
    * A phone call between an employee and a helpdesk operator where the helpdesk operators answers the call from an employee who has a problem they are trying to solve.
    * If the call is a scammer call example it means the employee is a scammer, otherwise the employee is a non-scammer.
    * The call should start with a greeting and identification
    * The call should end with helpdesk operator trying to do their best to solve the employee's problem.
    * The phone transcript should not last more than 10 minutes when spoken.
    * The phone transcript should be written in first person simulating an actual phone call.

* Output format
    * The output should be the actual complete phone call transcript between the Helpdesk operator and the Scammer all written on a single line of text.


Data points:

* Employee: Is trying to ether reset their corporate password, get personal information or data on other employees, gain access to a corprorate office building, or install malware on the helpdesk operator's computer, obtain the helpdesk operator's password
* Hepdesk operator: Who is male or female is trying to properly identify the employee in order to help resolve their issue but should never provide any employment details that was not provided by the Employee first.

Assistant:

"""

# Download S3 Dataset file to read and write to
# "s3://social-hacking-helper/shh-dataset.csv"
bucket = "social-hacking-helper"
key = "shh-dataset.csv"
filename = "shh-dataset.csv"
count = 0

# Write a function to take an input string and append to a csv file located in an s3 bucke3 bucket
def write_to_dataset(result):
    global count
    # Format input_string
    data = result.split('\n')[2:]   # ignore the first two lines of the transcript. 
    data = ' '.join(data)           # replace newlines with a space.
    
    # Open the dataset file in append mode
    with open(filename, mode="a", newline='') as file:
        writer = csv.writer(file)
        # Write the input string to the file
        writer.writerow([SCENARIO, data])
        # Close the file
        file.close()
        # Upload the dataset file to the s3 bucket
        s3client.upload_file(filename, bucket, key)
        # Print a success message
        count += 1
        print(f"Dataset {count} updated successfully")
        

s3client = boto3.client('s3')
s3client.download_file(bucket, key, filename)


bedrock = boto3.client(service_name = 'bedrock-runtime')

body = json.dumps({
    "prompt": prompt,
    "temperature": 0.7,
    "top_p": 0.7,
    "top_k": 200,
    "max_tokens_to_sample": 4000,
})

modelId = 'anthropic.claude-v2'
accept = 'application/json'
contentType = 'application/json'

for i in range(DATASET_SIZE):
    response = bedrock.invoke_model(body=body, modelId=modelId, accept=accept, contentType=contentType)
    
    response_body = json.loads(response.get('body').read())
    
    result = response_body.get('completion')
    #print(result)
    write_to_dataset(result)


