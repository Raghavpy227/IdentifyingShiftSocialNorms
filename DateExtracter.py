# -*- coding: utf-8 -*-
"""
Created on Mon Jul 10 14:36:56 2023

@author: sragh
"""
# NOTE - THIS CODE IS DEPRECIATED
import pandas as pd
import praw
from praw.models import Comment, Submission
import os
import datetime
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

path=r"C:\Users\sragh\OneDrive\Documents\Dissertation\Code"

df_train = pd.read_csv(os.path.join(path,"train_extracted.csv"))
df_dev = pd.read_csv(os.path.join(path,"dev_extracted.csv"))
df_test = pd.read_csv(os.path.join(path,"test_extracted.csv"))
print("dataset imported")

def commentDateExtractor(df):
    comment_date=[]
    nonecounter=0
    normcounter=0
    for i in df["comment_id"]:
        try:
            normcounter=normcounter+1
            comment=Comment(reddit,i)
            comment_date.append(datetime.datetime.fromtimestamp(int(comment.created)))
            print("norm counter"+str(normcounter))
        except:
            nonecounter=nonecounter+1
            print(nonecounter)
            comment_date.append(" ")
            continue
    print(nonecounter/len(df["comment_id"]))    
    df["comment_date"]=comment_date 
    return df

def convDateExtractor(df):
    conv_date=[]
    nonecounter=0
    normcounter=0
    for i in df["conv_id"]:
        t=i.split('~')
        try:
            normcounter=normcounter+1
            sub=Submission(reddit,t[0])
            conv_date.append(datetime.datetime.fromtimestamp(int(sub.created)))
            print("norm counter"+str(normcounter))
        except:
            nonecounter=nonecounter+1
            print(nonecounter)
            conv_date.append(" ")
            continue
    print(nonecounter/len(df["conv_date"]))    
    df["conv_date"]=conv_date 
    return df

print("Extracting Comments date for Train")
df_train=commentDateExtractor(df_train)
print("Extracting Comments date for Test") 
df_test=commentDateExtractor(df_test)
print("Extracting Comments date for Dev") 
df_dev=commentDateExtractor(df_dev)   

print("outputting the files")

df_train.to_csv(os.path.join(path,"train_extracted.csv"),index=False)
df_test.to_csv(os.path.join(path,"test_extracted.csv"),index=False)
df_dev.to_csv(os.path.join(path,"dev_extracted.csv"),index=False)

print("Extracting submission date for Train")
df_train=convDateExtractor(df_train)
print("Extracting submission date for Test") 
df_test=convDateExtractor(df_test)
print("Extracting submission date for Dev") 
df_dev=convDateExtractor(df_dev)  

print("outputting the files")

df_train.to_csv(os.path.join(path,"train_extracted.csv"),index=False)
df_test.to_csv(os.path.join(path,"test_extracted.csv"),index=False)
df_dev.to_csv(os.path.join(path,"dev_extracted.csv"),index=False)
    

    
    
