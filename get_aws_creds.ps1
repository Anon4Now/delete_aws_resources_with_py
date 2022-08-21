#Parameters for AWS profile being used & region that is being auth'ed to
param (
    [string]$aws_profile,
    [string]$aws_region
)

# Use PS cmdlet to join the aws\credentials file with USERPROFILE, and use the profile passed as a param
$aws_creds = (Get-AWSCredential -ProfileLocation $(Join-Path $env:USERPROFILE .aws\credentials) -ProfileName $aws_profile).GetCredentials()

#Set the env variables to be used by Docker
$AWS_ACCESS_KEY_ID= $aws_creds.AccessKey 
$AWS_SECRET_ACCESS_KEY= $aws_creds.SecretKey
$AWS_SESSION_TOKEN = $aws_creds.Token
$AWS_SECURITY_TOKEN = $aws_creds.Token
$AWS_DEFAULT_REGION= $aws_region

# Look for exe's in the current path
$location = (Get-Location).Path

# Run the container and pass in the created env variables -- use the docker image name as it will execute CMD [ "python3", "./main.py" ]
docker run -e AWS_SECURITY_TOKEN=$AWS_SECURITY_TOKEN -e AWS_SESSION_TOKEN=$AWS_SESSION_TOKEN -e AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY -e AWS_DEFAULT_REGION=$AWS_DEFAULT_REGION -v ${location}:/run -t <DOCKER IMAGE NAME>
