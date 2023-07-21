# -*- coding: utf-8 -*-
"""
Created on Tue Jul 18 14:11:37 2023

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
username="theredditapienjoyer"
password="Thakurji@2002"
secret="pkvNaeebVm700GggCqouig_cZuvt6Q"
client_id="4lUm-oVC66Bh1z3veqM9Bw"

reddit = praw.Reddit(
    client_id=client_id,
    client_secret=secret,
    password=password,
    user_agent="Comment Extraction (by u/USERNAME)",
    username=username,
)

df = pd.read_csv(os.path.join(path,"RS_2021-07.csv"))
df=df[df["num_comments"] >=10]




def getSubmission(id):
    
    tree=[]
    try: 
         print("in functo")
         tree=Submission(reddit,id).comments._comments
    except:
         tree=[]
        
    return tree   
 
def convertToDate(df):
    created_date=[]
    for i in df["created_utc"]:
        created_date.append(datetime.datetime.fromtimestamp(int(i)))
    df.drop(["created_utc"],axis=1,inplace=True)    
    df["created_date"] = created_date   
    return df

if __name__ == '__main__':
    df=convertToDate(df)
    count=0
    print("hi")
    p=Pool()
    comments=p.map(getSubmission,df["id"])
    p.close()
    p.join()
    df["comments"]=comments   
    df.to_csv(os.path.join(path,"RS_2021-07.csv"))