# -*- coding: utf-8 -*-
"""
Created on Fri Aug 18 09:58:32 2023

@author: py22715
This code is used to collate inference data to generate stats for the each violation type
"""

import pandas as pd
import os
from multiprocessing import Pool
import boto3
import torch
from tqdm.contrib import tenumerate
path = r"C:\Users\py22715\OneDrive - University of Bristol\Documents\Python Scripts"
s3_client = boto3.Session(aws_access_key_id='AKIA6IIIHUJETGQMT54O',aws_secret_access_key='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')
s3=s3_client.resource('s3')
s3_bucket=s3.Bucket('comment-extracted-reddit-files')
s3_client = boto3.client('s3',aws_access_key_id='AKIA6IIIHUJEZKQH5NEZ',aws_secret_access_key='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')
all_objects=s3_bucket.objects.all()
all_csv=[]
all_inference=[]
all_years=[]
for i in all_objects:
    all_csv.append(i.key)

df_dict=dict()
for i in all_csv:
    if i[len(i)-4:len(i)-3] == "e":
        all_inference.append(i)
        all_years.append(i[12:16])

for i in all_inference: 
    print("Processing :" + i)       
    s3_client.download_file('comment-extracted-reddit-files',Key=i,Filename=os.path.join(path,i))
    dataLoader_chkpt=torch.load(os.path.join(path,i))
    df=pd.DataFrame()
    df["date"]=dataLoader_chkpt["date"]
    df["predictions"]=dataLoader_chkpt["predictions"]
    if i[12:16] not in df_dict.keys():
        df_dict[i[12:16]]=df
    else:
        print("duplicate")
        df_dict[i[12:16]]=pd.concat([df_dict[i[12:16]],df],axis=0)
    os.remove(os.path.join(path,i))    
    print("Processed "+ i)    
                              
df_2005_10 = df_dict["2005"].reset_index()
df_2011_15=df_dict["2011"].reset_index()                            

df_2005_inference = df_2005_10[df_2005_10["date"].str[0:4] == "2005"]
df_2006_inference = df_2005_10[df_2005_10["date"].str[0:4] == "2006"]
df_2007_inference = df_2005_10[df_2005_10["date"].str[0:4] == "2007"]
df_2008_inference = df_2005_10[df_2005_10["date"].str[0:4] == "2008"]
df_2009_inference = df_2005_10[df_2005_10["date"].str[0:4] == "2009"]
df_2010_inference = df_2005_10[df_2005_10["date"].str[0:4] == "2010"]
df_2011_inference = df_2011_15[df_2011_15["date"].str[0:4] == "2011"]
df_2012_inference = df_2011_15[df_2011_15["date"].str[0:4] == "2012"]
df_2013_inference = df_2011_15[df_2011_15["date"].str[0:4] == "2013"]
df_2014_inference = df_2011_15[df_2011_15["date"].str[0:4] == "2014"]
df_2015_inference = df_2011_15[df_2011_15["date"].str[0:4] == "2015"]


df_2005_inference=df_2005_inference[df_2005_inference["predictions"]!=2]
df_2006_inference=df_2006_inference[df_2006_inference["predictions"]!=2]
df_2007_inference=df_2007_inference[df_2007_inference["predictions"]!=2]
df_2008_inference=df_2008_inference[df_2008_inference["predictions"]!=2]
df_2009_inference=df_2009_inference[df_2009_inference["predictions"]!=2]
df_2010_inference=df_2010_inference[df_2010_inference["predictions"]!=2]
df_2011_inference=df_2011_inference[df_2011_inference["predictions"]!=2]
df_2012_inference=df_2012_inference[df_2012_inference["predictions"]!=2]
df_2013_inference=df_2013_inference[df_2013_inference["predictions"]!=2]
df_2014_inference=df_2014_inference[df_2014_inference["predictions"]!=2]
df_2015_inference=df_2015_inference[df_2015_inference["predictions"]!=2]
df_inferences=[df_2005_inference,df_2006_inference,df_2007_inference,
               df_2008_inference,df_2009_inference,df_2010_inference,
               df_2011_inference,df_2012_inference,df_2013_inference,
               df_2014_inference,df_2015_inference]
years=[i for i in range(2005,2016)]
homophobia=[]
Incivility=[]
harrassment=[]
self_harm=[]
racial_slur=[]
df_stats=pd.DataFrame()

#counts the number of instances of each norm violation type. The Numbers are from label encoder and mapped accordingly
def stats_extracter(df): 
    predictions=list(df["predictions"])
    print(type(predictions))
    print(predictions) 
    homophobia.append(predictions.count(0))
    Incivility.append(predictions.count(1))
    harrassment.append(predictions.count(3))
    racial_slur.append(predictions.count(4))
    self_harm.append(predictions.count(5))

stats_extracter(df_2005_inference)
stats_extracter(df_2006_inference)
stats_extracter(df_2007_inference)
stats_extracter(df_2008_inference)
stats_extracter(df_2009_inference)
stats_extracter(df_2010_inference)
stats_extracter(df_2011_inference)
stats_extracter(df_2012_inference)
stats_extracter(df_2013_inference)
stats_extracter(df_2014_inference)
stats_extracter(df_2015_inference)


df_stats["year"]=years
df_stats["homophobia"]=homophobia
df_stats["incivility"]=Incivility
df_stats["self_harm"]=self_harm
df_stats["racial_slur"]=racial_slur
df_stats["harrassment"]=  harrassment

df_stats.to_csv(os.path.join(path,"Violation_stats.csv"),index=False)

  



                            
        
        
        
        
