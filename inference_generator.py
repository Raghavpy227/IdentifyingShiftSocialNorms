# -*- coding: utf-8 -*-
"""
Created on Sun Aug  6 20:56:14 2023

@author: py22715
THIS CODE IS DEPRECIATED - Please check the AWS Enabled version of it
"""

import pandas as pd
from openprompt.data_utils import InputExample
import torch
import os
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import balanced_accuracy_score,f1_score,classification_report
from sklearn.model_selection import train_test_split
from openprompt.config import get_config, save_config_to_yaml
from yacs.config import CfgNode

path=r"C:\Users\py22715\OneDrive - University of Bristol\Documents\Python Scripts"
df=pd.read_csv(os.path.join(path,"RS_2012-03_violations2.csv"))

trained_model = torch.load(os.path.join(path,"violation_detector.pt"))



dataset=[]
count=0
violation_sentence = df["sentence"]
label=df["label"]
context=df["context"]

for i in violation_sentence:
    dataset.append(InputExample(guid=count,text_a=context[count],text_b=i,label=label[count]))
    count=count+1

data_train_val , data_test = train_test_split(dataset,train_size=0.8)
data_train,data_val = train_test_split(data_train_val,train_size=0.5)


from openprompt import PromptDataLoader
data_loader_train = PromptDataLoader(
    dataset = data_train,
    tokenizer = tokenizer,
    template = promptTemplate,
    tokenizer_wrapper_class=WrapperClass,
)

data_loader_val = PromptDataLoader(
    dataset = data_val,
    tokenizer = tokenizer,
    template = promptTemplate,
    tokenizer_wrapper_class=WrapperClass,
)

data_loader_test = PromptDataLoader(
    dataset = data_test,
    tokenizer = tokenizer,
    template = promptTemplate,
    tokenizer_wrapper_class=WrapperClass,
)

use_cuda=True
allpreds = []
alllabels = []
for step, inputs in enumerate(data_loader_val):
    if use_cuda:
        inputs = inputs.cuda()
    logits = trained_model(inputs)
    labels = inputs['label']
    alllabels.extend(labels.cpu().tolist())
    allpreds.extend(torch.argmax(logits, dim=-1).cpu().tolist())
print(f1_score(alllabels,allpreds,average="micro" ))
print(classification_report(alllabels,allpreds))    
    
