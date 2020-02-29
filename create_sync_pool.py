#!/usr/bin/python3 

import boto3
import logging
import pprint
import json
import argparse
import sys



def _createSynchronizedUserPools( args ):
    userPoolName = "SyncID_Pool_{0}_{1}".format(args.syncid_user_id, args.pool_name)

    for regionName in args.aws_region:
        cognitoClient = boto3.client( 'cognito-idp', region_name=regionName )

        createResponse = cognitoClient.create_user_pool(
            PoolName                = userPoolName, 
            UsernameAttributes      = [ 'email' ]
        )  
        

def _validateUserPoolName( args ):
    validationPassed = True
    
    for currRegion in args.aws_region:
        #logging.debug( "Checking user pool name {0} in region {1} for user {2}".format(
        #    args.pool_name, currRegion, args.syncid_user_id) ) 
        userPools = _getUserPoolsForRegion( currRegion )

        logging.debug( "User pools in region {0}:\n{1}".format(
            currRegion, json.dumps(userPools, indent=4, sort_keys=True)) )

        checkPoolName = "SyncID_Pool_{0}_{1}".format(args.syncid_user_id, args.pool_name) 
        if checkPoolName in userPools:
            logging.error( "Found user pool {0} in region {1}, cannot create".format(checkPoolName, currRegion) )
            validationPassed = False
            break

    return validationPassed


def _getUserPoolsForRegion( regionName ):

    userPoolsInRegion = []

    cognitoClient = boto3.client( 'cognito-idp', region_name=regionName )

    nextToken = None
    maxResults = 60
    while True:
        if nextToken is None:
            userPoolsResponse = cognitoClient.list_user_pools(
                MaxResults=maxResults )
        else:
            userPoolsResponse = cognitoClient.list_user_pools(
                NextToken   = nextToken, MaxResults  = maxResults )

        for currPool in userPoolsResponse[ 'UserPools' ]:
            print( "Found pool name: {0}".format(currPool['Name']) )
            userPoolsInRegion.append( currPool[ 'Name' ] )

        if 'NextToken' in userPoolsResponse:
            nextToken = userPoolsResponse[ 'NextToken' ]
        else:
            break

    return userPoolsInRegion


def _parseArgs():
    argParser = argparse.ArgumentParser(description="Create synchronized Cognito User Pool across multiple AWS regions")
    argParser.add_argument( "syncid_user_id",   
        help="UUID of the user who will own the pool" )
    argParser.add_argument( "pool_name",       
        help="Name of the synchronized pool, needs to be unique for this user in all regions" )
    argParser.add_argument( "aws_region",       
        help="region ID's to build synchronized pool", 
        nargs="+" )

    return argParser.parse_args()


def _silenceOtherLoggers():
    loggersToSilence = (
        'botocore',
        'urllib3'
    )

    for currLogger in loggersToSilence:
        logging.getLogger(currLogger).setLevel(logging.WARNING)


def _main():
    _silenceOtherLoggers()

    # Confirm new user announcement SNS exists in us-east-1

    # Confirm that the process new user announcement SQS exists in all regions

    args = _parseArgs()

    # Validate user pool name is not present in any of the specified regions
    if _validateUserPoolName( args ) is False:
        logging.critical( "Pool name {0} is already in use for user ID {1}".format(
                args.pool_name, args.syncid_user_id) )
        sys.exit( 1 )

    # Create the pool in all regions
    _createSynchronizedUserPools( args )

    # Add announce new user Lambda to all regions

    # Add replicate new user info Lambda to all regions

    # Set post-confirmation trigger in all regions to fire the user-replication Lambda



if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    _main()
