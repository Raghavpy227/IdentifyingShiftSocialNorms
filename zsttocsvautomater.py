# -*- coding: utf-8 -*-
"""
Created on Fri Jul 14 23:01:44 2023

@author: sragh
The aim of this code is to extract the meaningful columns such as submission id , 
creation date , subreddit name and number of comments and convert the file format to csv
"""

import os
import sys
import boto3
path=r"C:\Users\sragh\Downloads\reddit\submissions"
os.chdir(path)
rs_files=os.listdir()

s3_client = boto3.client('s3',aws_access_key_id='AKIA6IIIHUJEZKQH5NEZ',aws_secret_access_key='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')
for i in rs_files:
    
    if i[0:2]=="RS" and i[len(i)-3:len(i)] == "zst":
     
        filename=i[:-3]
        command="python zsttocsv.py "+ i + " "+ filename+"csv"+ " id,created_utc,subreddit,num_comments"
        os.system(command)
        s3_client.upload_file(os.path.join(path,i),'zst-reddit-submission-files',i)
        s3_client.upload_file(os.path.join(path,filename+"csv"),'csv-extracted-files',filename+"csv")
        os.remove(os.path.join(path,i))
        os.remove(os.path.join(path,filename+"csv"))
    
       
#For comments
#"python zsttocsv.py "+ i + " "+ filename+"csv"+ " author_flair_text,parent_id,id,created_utc,link_id,parent_id,subreddit,controversiality,body"