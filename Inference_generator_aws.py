# -*- coding: utf-8 -*-
"""
Created on Thu Aug 17 11:28:13 2023

@author: py22715
The aim of this code is to download data loader from AWS bucket and the pre-trained OpenPrompt Models(2005,2011) 

Generate Inference and then upload it to AWS bucket as a Pytorch checkpoint. 
"""

#Importing all the necessary libraries
import pandas as pd
import os
from multiprocessing import Pool
import boto3
import torch
from tqdm.contrib import tenumerate

#loading the pretrained models
path = r"C:\Users\py22715\OneDrive - University of Bristol\Documents\Python Scripts"
chkpt_2005=torch.load(os.path.join(path,"PromptModel2005.pt"))
chkpt_2011=torch.load(os.path.join(path,"PromptModel2011.pt"))
promptModel2005=chkpt_2005["model"]
promptModel2011=chkpt_2011["model"]
#Setting up a client session
s3_client = boto3.Session(aws_access_key_id='AKIA6IIIHUJETGQMT54O',aws_secret_access_key='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')
s3=s3_client.resource('s3')
s3_bucket=s3.Bucket('comment-extracted-reddit-files')

all_objects=s3_bucket.objects.all()
all_csv=[]

# Getting all name of all objects present in the bucket
for i in all_objects:
    all_csv.append(i.key)

all_pt_2005=[] 
all_pt_2011=[]  
all_processed=[]
#Creating a list for dataloaders for which Inference is already generated.
for i in all_csv:
    if i[len(i)-4:len(i)-3] == "e":
        all_processed.append(i[12:21])
        
       
#creates a list that needs to be processed by different OpenPromptModels, If the user aims to rewrite the already made inference then comment the first If block.   
for i in all_csv:
    if i[12:21] in all_processed:
        continue
    if i[len(i)-2:len(i)] == "pt" and i[12:16]=="2005":
        all_pt_2005.append(i)
    if i[len(i)-2:len(i)] == "pt" and i[12:16]=="2011":
        all_pt_2011.append(i)   
#Creating a S3_Client        
s3_client = boto3.client('s3',aws_access_key_id='AKIA6IIIHUJEZKQH5NEZ',aws_secret_access_key='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')
#This function downloads the checkpoint files and generates the inference and uploads them
def inference_generator(promptModel,files):
    for i in files:
        print("Generating Inference for "+i)
        s3_client.download_file('comment-extracted-reddit-files',Key=i,Filename=os.path.join(path,i))
        dataLoader_chkpt=torch.load(os.path.join(path,i))
        dataloader=dataLoader_chkpt["Data_loader"]
        use_cuda=True
        allpreds=[]
        for step, inputs in tenumerate(dataloader):
            if use_cuda:
                inputs = inputs.cuda()
            logits = promptModel(inputs)
            allpreds.extend(torch.argmax(logits, dim=-1).cpu().tolist())
        torch.save({"Data_loader":dataLoader_chkpt["Data_loader"],
                     "date":dataLoader_chkpt["date"],"predictions":allpreds},os.path.join(path,i[0:len(i)-3]+"inference.pt"))    
        s3_client.upload_file(os.path.join(path,i[0:len(i)-3]+"inference.pt"),'comment-extracted-reddit-files',i[0:len(i)-3]+"inference.pt")
        os.remove(os.path.join(path,i))
        os.remove(os.path.join(path,i[0:len(i)-3]+"inference.pt"))
inference_generator(promptModel2005, all_pt_2005) 
inference_generator(promptModel2011, all_pt_2011)        
   
