# Modify/Delete Default AWS VPC Resources

This script programmatically provides a way to alter the VPC resources that are created by AWS automatically when a new account is created.

AWS has a total of 17 regions that are activated on behalf of the end-user, which means that there are 17 default VPC's that are created 1-per-region. This is a security gap as it means that you have unused/unaccounted resources existing in regions that you in all likelihood are not going to use. Using this script will allow for either a modification of the default Security Groups and NACL's to block all ingress/egress traffic to that default VPC, or will allow for full deletion of the VPC (including most of the VPC resources).

The default VPC resources that are created in these regions are below:

- Default Internet Gateway (can be deleted by itself)
- Default Subnets (can be deleted by itself)
- Default Route Table (\*cannot be deleted by itself -- will not prevent the deletion of VPC)
- Default NACL (\*cannot be deleted by itself -- if the entire VPC is deleted this will also be deleted)
- Default Security Group (\*cannot be deleted by itself -- if the entire VPC is deleted this will also be deleted)
- Default VPC (\*cannot be deleted until all other resources are detached/deleted -- except for those that cannot be deleted)

## Tool Functionality:

- Will use Boto3 SDK to programmtically interact with AWS
- Will provide 2 command line arguments for the user to choose ['delete' OR 'modify']
- Can be run from inside a Docker container if AWS credentials want to passed an environment variables to the container, or run from CLI
- The *'Modify'* option will remove the ingress & egress rules from both the default Security Group as well as the default NACL
- The *'Delete'* option will attempt to detach and delete all resources (that can be deleted) from the VPC and then delete the default VPC itself
- Both the *'Modify'* and *'Delete'* options will also update the AWS SSM preferences to block SSM Document public access, this can easily be skipped

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

#### Note: I will be running this tool from the CLI in the examples, I have also run it successfully using a Docker container.

#### Check Arg Menu:

Check what arguments are expected with the '-o' flag.
![help_menu](https://user-images.githubusercontent.com/80045938/193708749-cc68bd69-0376-4759-b774-c0ca755ea5ee.gif)

#### Run with *'Modify'* option:

Run the script with the '-o modify' option.
![modify_option](https://user-images.githubusercontent.com/80045938/193708972-92546d2f-2f52-4c66-84d1-9c468b935dc0.gif)

#### Run with *'Delete'* option:
Run the script with the '-o delete' option.
![delete_option](https://user-images.githubusercontent.com/80045938/193708991-612efaad-4f9a-48db-a2dc-99ca11618cbd.gif)
