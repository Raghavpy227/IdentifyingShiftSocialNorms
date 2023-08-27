# -*- coding: utf-8 -*-
"""
Created on Sun Aug 20 14:06:52 2023

@author: sragh
The Aim of this code is to randomly pick 5 files and select the first 10-20 submissions  and generate a golden set which would be manually tagged
"""

import os
import sys
import boto3
import redditcleaner
import pandas as pd
from random import randrange

path = r"C:\Users\sragh\OneDrive\Documents\Dissertation\Data\s3_submissions_downloads"
s3_client = boto3.Session(aws_access_key_id='AKIA6IIIHUJETGQMT54O',aws_secret_access_key='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')
s3=s3_client.resource('s3')
s3_bucket=s3.Bucket('csv-extracted-files')
s3_bucket_processed=s3.Bucket('comment-extracted-reddit-files')
all_objects=s3_bucket_processed.objects.all()
all_csv=[]
for i in all_objects:
    all_csv.append(i.key)
    
all_comments_csv=[]

for i in all_csv:
    if i[len(i)-4:len(i)]==".csv":
        all_comments_csv.append(i)

itr=0
random_files=[]
index_selected=[]
while itr<5: 
    rand_index=randrange(0,len(all_comments_csv)-24,1)
    if rand_index in index_selected:
        continue
    else:
        index_selected.append(rand_index)
        random_files.append(all_comments_csv[rand_index])
        itr=itr+1
        
s3_client = boto3.client('s3',aws_access_key_id='AKIA6IIIHUJEZKQH5NEZ',aws_secret_access_key='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')        
# Creating golden set from Random files
df=pd.DataFrame()

for i in random_files: 
    s3_client.download_file('comment-extracted-reddit-files',i,os.path.join(path,i))
    df_new=pd.read_csv(os.path.join(path,i))
    df_new=df_new[df_new["num_comments"]==min(df_new['num_comments'])]
    if len(df_new["num_comments"]) <= 10:
        df=pd.concat([df,df_new],axis=0)
    else:
        df_new=df_new.head(10)
        df=pd.concat([df,df_new],axis=0)
    os.remove(os.path.join(path,i))    
        
df.to_csv(os.path.join(path,"golden_set.csv"),index=False)    
      
    
    
