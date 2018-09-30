#!/usr/bin/python
# -*- coding: utf-8 -*- 

import sys, getopt, boto3
#from boto.s3.connection import S3Connection
#from boto.s3.key import Key
from socket import gethostname

awskey = ''
awssecretkey = ''
bucket_name = ''
file = ''

def usage():
       print 'usage: copyFile2S3.py -k <awskey> -s <aws-secretkey> -f <inputfile> -b <bucket>'
       print '    --file  ,       -f  : input file to copy to S3'
       print '    --bucket,       -b  : bucket on S3 to copy file to ( will create if not there)'
       print '    --awssecretkey, -a  : aws secret key for access'
       print '    --awskey,       -k  : aws key for access'
       sys.exit()

def loadvalues(argv):
   global awskey
   global awssecretkey
   global bucket_name
   global file
   inputfile = ''
   outputfile = ''
   try:
      opts, args = getopt.getopt(argv,"hk:s:f:b:",["awskey=", "awssecretkey=","file=","bucket_name="])
   except getopt.GetoptError:
      usage()
   for opt, arg in opts:
      if opt == '-h':
      	 usage() 
      elif opt in ("-f", "--file"):
         file = arg
      elif opt in ("-b", "--bucket"):
         bucket_name = arg
      elif opt in ("-s", "--awssecretkey"):
         awssecretkey = arg
      elif opt in ("-k", "--awskey"):
         awskey = arg

def copy():
    global awskey
    global awssecretkey
    global bucket_name
    global file
    
    s3 = boto3.client('s3')
    response = s3.list_buckets()
    buckets = [bucket['Name'] for bucket in response['Buckets']]
    if (bucket_name not in buckets):
        s3.create_bucket(Bucket=bucket_name)
    s3.upload_file(file, bucket_name, file)

#    con = S3Connection(awskey, awssecretkey)
#    targetBucket = con.create_bucket(bucket)
#    k = Key(targetBucket)
#    myList = file.split('/')
#    rootFile = myList[-1]
#    k.key = gethostname()+'/'+rootFile
#    k.set_contents_from_filename(file)
#    k.set_contents_from_filename(file)

if __name__ == "__main__":
	loadvalues(sys.argv[1:])
	copy();