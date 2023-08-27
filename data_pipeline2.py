import pandas as pd
from openprompt.data_utils import InputExample
import torch
import os
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import balanced_accuracy_score,f1_score,classification_report
from sklearn.model_selection import train_test_split
from openprompt.config import get_config, save_config_to_yaml

import time

import re

from openprompt.plms import load_plm

from openprompt import PromptDataLoader
import boto3
 



path =  r"C:\Users\py22715\OneDrive - University of Bristol\Documents\Python Scripts"

df=pd.read_csv(os.path.join(path,"RS_2011_15_inference_data.csv"))
s3_client = boto3.client('s3',aws_access_key_id='AKIA6IIIHUJEZKQH5NEZ',aws_secret_access_key='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')

t_start=time.time()

new_context=[]

full_context=df['context']

for i in full_context:

    new_context.append(i.split("',"))

counter=0

better_split=[]

diff_sp='",'

for i in new_context:

    inter=[]

    for j in i:

 

 

     if diff_sp in j:

        #print("Hi")

        inter.extend(re.split(diff_sp,j))

    else:

        inter.append(j)

    better_split.append(inter)    
count=0    
df["context"]  = better_split
dataset=[]
count=0
date_count=0
date=df["created_date"]
new_date=[]
for i in df["context"]:
    subcontext=i[0:6]
    future_comments=i[6:len(i)]
    for c in future_comments:
        dataset.append(InputExample(guid=count,text_a=str(subcontext),text_b=c))
        subcontext.extend(c)
        new_date.append(date[date_count])
        count=count+1
    date_count+=1    


plm, tokenizer, model_config, WrapperClass = load_plm("bert", "bert-base-cased")
from openprompt.prompts import ManualTemplate
promptTemplate = ManualTemplate(
    text = '{"placeholder":"text_a"} was the context for {"placeholder":"text_b"}, Which violation is it? {"mask"} ',
    tokenizer = tokenizer,

)
prev=0
count=0
ds=0
nd=0
i=0
while i < len(dataset):
    if i + 20000 >= len(dataset):
        ds=dataset[prev:len(dataset)]
        nd=new_date[prev:len(dataset)]
    else:  
        ds=dataset[prev:i+1]
        nd=new_date[prev:i+1]    
    data_loader = PromptDataLoader(
    dataset = ds,
    tokenizer = tokenizer,
    template = promptTemplate,
    tokenizer_wrapper_class=WrapperClass)
    torch.save({"Data_loader":data_loader,"date":nd},os.path.join(path,"data_loader_2011_15_"+str(count)+".pt"))
    s3_client.upload_file(os.path.join(path,"data_loader_2011_15_"+str(count)+".pt"),'comment-extracted-reddit-files',"data_loader_2011_15_"+str(count)+".pt")
    print("uploaded dataloader")
    os.remove(os.path.join(path,"data_loader_2011_15_"+str(count)+".pt"))
    print("file Deleted")
    prev=i
    i=i+20000
    count=count+1  
