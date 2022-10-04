# Modify/Delete Default AWS VPC Resources

This script programmatically provides a way to alter the VPC resources that are created by AWS automatically when a new account is created.

AWS has a total of 17 regions that are activated on behalf of the end-user, which means that there are 17 default VPC's that are created 1-per-region. This is a security gap as it means that you have unused/unaccounted resources existing in regions that you in all likelihood are not going to use. Using this script will allow for either a modification of the default Security Groups and NACL's to block all ingress/egress traffic to that default VPC, or will allow for full deletion of the VPC (including most of the VPC resources).

The default VPC resources that are created in these regions are below:

- Default Internet Gateway (can be deleted by itself)
- Default Subnets (can be deleted by itself)
- Default Route Table (\*cannot be deleted by itself -- will not prevent the deletion of VPC)
- Default NACL (\*cannot be deleted by itself -- if the entire VPC is deleted this will also be deleted)
- Default Security Group (\*cannot be deleted by itself -- if the entire VPC is deleted this will also be deleted)
- Default VPC (\*cannot be deleted until all other resources are detached/deleted)

## Tool Functionality:

- Will use Boto3 SDK to programmtically interact with AWS
- Will provide 2 command line arguments for the user to choose ['delete' OR 'modify']
- Can be run from inside a Docker container if AWS credentials want to passed an environment variables to the container, or run from CLI

## Tool Requirements:

- To use the default functionality of this tool (making API calls to AWS) a module will need to be installed using pip
  - [boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)

## Quick Notes:

- This script can be automated as part of a IaC pipeline to run after a new account is vended
- This script could be used to clean up non-default resources as well, some alterations on API calls would be needed
- This script could be adapted to other cloud service providers, the API calls and SDK would need to be changed

## Resource Path:

```
rootdir:.
│   .gitignore
│   config.json
│   Dockerfile
│   get_aws_creds.ps1
│   License
│   logs.log
│   README.md
│   requirements.txt
│
├───delete_aws_resources_with_py
│   │   default_resources.py
│   │   main.py
│   │   resource_updates.py
│   │   utils.py
│   │   __init__.py
│
├───tests
│   │   conftest.py
│   │   test_default_resources.py
│   │   test_resource_updates.py
│   │   __init__.py
│   │
│   ├───json_files
│   │       egress_sg_rule.json
```

## Using the Tool:

#### Note: I will be running this tool from the CLI in the examples, I have also run it successfully using a Docker container

#### Step 1:

Run the binary or standalone exe to start CLI prompts.
![start_program](https://user-images.githubusercontent.com/80045938/192074954-0cf77f16-3bfe-457c-a764-64261a1c420c.gif)

#### Step 2:

Download the wanted file, the program will generate SHA256, SHA1, and MD5 hashes.
![gen_hashes](https://user-images.githubusercontent.com/80045938/192074964-0a41519b-c3e7-40e7-a3a0-cce12917a349.gif)

#### Step 3:

**IMPORTANT** For this option to be presented to the user, a .env file will need to be present
![get_api_results](https://user-images.githubusercontent.com/80045938/192074974-54a5731e-e2ca-4661-ad9d-480d14fad8d2.gif)
