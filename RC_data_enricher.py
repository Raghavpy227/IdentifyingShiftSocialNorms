# -*- coding: utf-8 -*-
"""
Created on Fri Jul 14 23:44:00 2023

@author: sragh
THIS CODE IS DEPRECIATED
"""

import pandas as pd
import os
import praw
from praw.models import Comment, Submission
from praw.models.comment_forest import CommentForest
import datetime

path = r"C:\Users\sragh\OneDrive\Documents\Dissertation\Data\comments"
#Enter your Reddit credentials
username=""
password=""
secret=""
client_id=""

df=pd.read_csv(os.path.join(os.path.join(path,"RC_2005-12.csv")))
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
df=convertToDate(df)


def getCommentTree(df):
    context=[]
    count=0
    for i in df["id"]:
        try:
            comment = Comment(reddit,i)
            submission = Submission(reddit,comment._extract_submission_id())
            commentforest = CommentForest(submission) 
            tree= commentforest._gather_more_comments(submission.comments) 
            print(tree) 
            context.append(tree) 
            count=count+1 
            print(count)
        except:    
            context.append([])
            count=count+1 
            print(count)
    df["context"]=context  
df=getCommentTree(df)    
        
        
    
    
    
    
