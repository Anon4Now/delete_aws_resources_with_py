#!/usr/bin/env python
from __future__ import print_function
from get_resources import GetRegions
import optparse
import boto3
import logging

#  VPC resources created by AWS 'https://docs.aws.amazon.com/vpc/latest/userguide/default-vpc.html'

# Logger configurations
logger = logging.getLogger()
logging.basicConfig(level=logging.INFO, format='%(asctime)s: %(levelname)s: %(message)s')

parser = optparse.OptionParser()


def getArgs():
    parser.add_option("-o", "--option", dest="sanitize_option",
                      help="Use this flag to select an option to run against account (e.g. --option deleteonly || -o modifyonly --"
                           "The options available are 'all', 'deleteonly', 'modifyonly'"
                           "the default action with be run 'alloptions'")
    parsingInput = parser.parse_args()

    (options, args) = parsingInput

    if not options.sanitize_option:
        parser.error("[-] Please specify an option flag, --help for more info")
    else:
        return options


regionClient = boto3.client('ec2')
regionResources = GetRegions(regionClient)
regions = regionResources.getRegions()


#  Main Function
def main():
    outArgs = getArgs()
    for region in regions:
        try:
            vpcClient = boto3.client('ec2', region_name=region)
            ec2 = boto3.resource('ec2', region_name=region)
            optionSet = SetArgsAndObjects(vpcClient, ec2, region)

            if outArgs.sanitize_option == "all":
                optionSet.allOptions()
            elif outArgs.sanitize_option == "deleteonly":
                optionSet.deleteResourcesOption()
            elif outArgs.sanitize_option == "modifyonly":
                optionSet.modifyResourceOption()
            else:
                logger.error("[-] The option provided was not found, please try again (--help for more info)")
        except Exception as e:
            logger.error("[-] Failed to create variables with error: %s", e)


if __name__ == "__main__":
    main()
