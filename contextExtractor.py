# -*- coding: utf-8 -*-
"""
Created on Thu Jul  6 15:20:59 2023

@author: sragh

THIS CODE IS DEPRICIATED AND NOT PART OF THE FLOW
"""

import pandas as pd 
import os 

path=r"C:\Users\sragh\OneDrive\Documents\Dissertation\Models\New folder\Norm VIO private"
df_dev = pd.read_json(os.path.join(path,"dev.jsonl"),lines=True)
df_train = pd.read_json(os.path.join(path,"train.jsonl"),lines=True)
df_test = pd.read_json(os.path.join(path,"test.jsonl"),lines=True)

def contextExtracter(df):
    context=df["context"]
    context_comments = []
    for i in context:
        comment_list=[]
        for j in i : 
            context_dict=j
            comment_list.append(context_dict["tokens"])
        context_comments.append(comment_list)
    df["comment_context"]= context_comments
    return df
def finalCommentExtracter(df):
    final_comment=df["final_comment"]
    final_comm=[]
    for i in final_comment:
        final_dict=i
        final_comm.append(final_dict["tokens"])
    df["final_comments"]=final_comm
    return df
        
        
    
df_dev=contextExtracter(df_dev)
df_test=contextExtracter(df_test)
df_train=contextExtracter(df_train)    

df_dev=finalCommentExtracter(df_dev)
df_test=finalCommentExtracter(df_test)
df_train=finalCommentExtracter(df_train)  


df_dev.to_csv("dev_extracted.csv",index=False)
df_test.to_csv("test_extracted.csv",index=False)
df_train.to_csv("train_extracted.csv",index=False)  
    
