# -*- coding: utf-8 -*-
"""
Created on Wed Aug  9 22:03:47 2023

@author: sragh
This piece of code is responsible for dividing the data into eras 2005-2010 and 2011-2015 . Initially 2016-2019 was considered but Removed later
"""

import os
import sys
import boto3
import redditcleaner
import pandas as pd

path = r"C:\Users\sragh\OneDrive\Documents\Dissertation\Data\s3_submissions_downloads"
s3_client = boto3.Session(aws_access_key_id='AKIA6IIIHUJETGQMT54O',aws_secret_access_key='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')
s3=s3_client.resource('s3')
s3_bucket_processed=s3.Bucket('comment-extracted-reddit-files')
s3_client = boto3.client('s3',aws_access_key_id='AKIA6IIIHUJEZKQH5NEZ',aws_secret_access_key='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')
all_objects=s3_bucket_processed.objects.all()
all_csv=[]
for i in all_objects:
    all_csv.append(i.key)
df_2005_2010=0
df_2010_2015=0
df_2016_2019=0
count_2005_2010=0
count_2011_2015=0
count_2016_2019=0
for i in all_csv:
    if int(i[3:7])>= 2005 and int(i[3:7])<=2010:
        print("Joining "+str(i)+"to 2005-2010")
        s3_client.download_file('comment-extracted-reddit-files',Key=i,Filename=os.path.join(path,i))
        if count_2005_2010 == 0:
            df_2005_2010=pd.read_csv(os.path.join(path,i))
            count_2005_2010+=1
        else:
            df_2005_2010=pd.concat([df_2005_2010,pd.read_csv(os.path.join(path,i))],axis=0)
            
    elif int(i[3:7])>= 2011 and int(i[3:7])<=2015:
        print("Joining "+str(i)+"to 2011-2015")
        s3_client.download_file('comment-extracted-reddit-files',Key=i,Filename=os.path.join(path,i))
        if count_2011_2015 == 0:
            df_2011_2015=pd.read_csv(os.path.join(path,i))
            count_2011_2015+=1
        else:
            df_2011_2015=pd.concat([df_2011_2015,pd.read_csv(os.path.join(path,i))],axis=0)  
    elif int(i[3:7])>= 2016 and int(i[3:7])<=2019:
        print("Joining "+str(i)+"to 2016-2019")
        s3_client.download_file('comment-extracted-reddit-files',Key=i,Filename=os.path.join(path,i))
        if count_2016_2019 == 0:
            df_2016_2019=pd.read_csv(os.path.join(path,i))
            count_2016_2019+=1
        else:
            df_2016_2019=pd.concat([df_2016_2019,pd.read_csv(os.path.join(path,i))],axis=0)      
    os.remove(os.path.join(path,i))        
    
df_2005_2010=df_2005_2010[df_2005_2010['context']!='[]'] 
df_2005_2010.dropna(inplace=True,axis=0)  
df_2011_2015=df_2011_2015[df_2011_2015['context']!='[]']
df_2011_2015.dropna(inplace=True,axis=0)  
df_2016_2019=df_2016_2019[df_2016_2019['context']!='[]']
df_2016_2019.dropna(inplace=True,axis=0)  

df_2005_2010.to_csv(os.path.join(path,"RS_2005_2010.csv"),index=False)
df_2011_2015.to_csv(os.path.join(path,"RS_2011_2015.csv"),index=False)
df_2016_2019.to_csv(os.path.join(path,"RS_2016_2019.csv"),index=False)
