import json


class GetRegions:

    skip_regions = []

    #  ---Class Methods---
    def __init__(self, client):
        self.regionClient = client
        self.regionList = []

    #  Get region data and pass it to the delete module
    def getRegions(self):
        getRegions = self.regionClient.describe_regions()

        #  json data parsing
        jsonStr = json.dumps(getRegions)
        response = json.loads(jsonStr)
        regionStr = json.dumps(response['Regions'])
        regions = json.loads(regionStr)

        #  add region's to instance attribute
        for region in regions:
            if region['RegionName'] not in GetRegions.skip_regions:
                self.regionList.append(region['RegionName'])
        return self.regionList


class GetVPCS:

    #  ---Class Methods---
    def __init__(self, client):
        self.vpcClient = client
        self.vpcList = []

    # Get VPC data and pass it to the delete module
    def getDefaultVpcs(self):
        vpcs = self.vpcClient.describe_vpcs(
            Filters=[
                {
                    'Name': 'isDefault',
                    'Values': [
                        'true',

                    ],
                },
            ]
        )

        # json data parsing
        vpcString = json.dumps(vpcs)
        response = json.loads(vpcString)
        outData = json.dumps(response['Vpcs'])
        vpcs = json.loads(outData)

        # add vpc's to instance attribute
        for vpc in vpcs:
            self.vpcList.append(vpc['VpcId'])
        return self.vpcList
