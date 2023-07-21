# -*- coding: utf-8 -*-
"""
Created on Sat Jul 15 14:34:39 2023

@author: sragh
"""

import pandas as pd
import os
import praw
from praw.models import Comment, Submission
from praw.models.comment_forest import CommentForest
import datetime
from multiprocessing import Pool


path = r"C:\Users\sragh\OneDrive\Documents\Dissertation\Data\submissions"
all_csv=os.listdir(path)
dataframes=dict()
username="theredditapienjoyer"
password="Thakurji@2002"
secret="pkvNaeebVm700GggCqouig_cZuvt6Q"
client_id="4lUm-oVC66Bh1z3veqM9Bw"

for i in all_csv:
    if i[-1]=='v':
        df=pd.read_csv(os.path.join(path,i))
        df=df[df["num_comments"]>=20]
        if len(df["id"]) >0: 
            dataframes[i]=df

reddit = praw.Reddit(
    client_id=client_id,
    client_secret=secret,
    password=password,
    user_agent="Comment Extraction (by u/USERNAME)",
    username=username,
)
def convertToDate(df):
    created_date=[]
    for i in df["created_utc"]:
        created_date.append(datetime.datetime.fromtimestamp(int(i)))
    df.drop(["created_utc"],axis=1,inplace=True)    
    df["created_date"] = created_date   
    return df

def getSubmission(id):
    return Submission(reddit,id)

def getCommentTree(df):
    context=[]
    count=0
    submissions=[]
    for i in df["id"]:
        try:
            submission = Submission(reddit,i)
            tree= submission.comments._comments
            all_comments=[]
          
            for i in tree:
                comment= i.body
                all_comments.append(comment)
         
            context.append(all_comments) 
            count=count+1
            print(count) 
    
        except:  
            print("except")
            context.append([])
            count=count+1
            
        
    df["context"]=context
    return df
count=0

for k,v in dataframes.items():
    if "context" in v.columns:
        count=count+1
        print("File number "+str(count))
        continue
    df=convertToDate(v)
    df=getCommentTree(df)
    df.to_csv(os.path.join(path,k))
    count=count+1
    print(count)
    
    