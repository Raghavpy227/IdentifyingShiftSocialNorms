# -*- coding: utf-8 -*-
"""
Created on Wed Aug 16 15:24:25 2023

@author: py22715
"""

import pandas as pd
from openprompt.data_utils import InputExample
import torch
import os
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import balanced_accuracy_score,f1_score,classification_report
from sklearn.model_selection import train_test_split
import time
import re
from openprompt.plms import load_plm
from openprompt import PromptDataLoader
import boto3
from tqdm.contrib import tenumerate

path=r"C:\Users\py22715\OneDrive - University of Bristol\Documents\Python Scripts"

df_2005=pd.read_csv(os.path.join(path,"RS_2005_10_training_data_tagged.csv"))
df_2011=pd.read_csv(os.path.join(path,"RS_2011_15_training_data_tagged.csv"))
model_chkpt=torch.load(os.path.join(path,"violation_type_context_model_chkpt.pt"))
promptModel_2005=model_chkpt['model']
promptModel_2011=model_chkpt['model']

encoder = LabelEncoder()
df_2005["label"]=encoder.fit_transform(df_2005["violation"])
df_2011["label"]=encoder.fit_transform(df_2011["violation"])

training_val_2005,test_2005=train_test_split(df_2005, train_size=0.8,
                                             stratify=df_2005['label'])
training_2005,val_2005=train_test_split(training_val_2005, train_size=0.8,
                                        stratify=training_val_2005['label'])

training_val_2011,test_2011=train_test_split(df_2011, train_size=0.8,
                                             stratify=df_2011['label'])
training_2011,val_2011=train_test_split(training_val_2011, train_size=0.8,
                                        stratify=training_val_2011['label'])


from openprompt.prompts import ManualTemplate

from openprompt.plms import load_plm
from openprompt.lm_bff_trainer import LMBFFClassificationRunner,ClassificationRunner
plm, tokenizer, model_config, WrapperClass = load_plm("bert", "bert-base-cased")


promptTemplate = ManualTemplate(
    text = '{"placeholder":"text_a"} was the context for {"placeholder":"text_b"}, Which violation is it? {"mask"} ',
    tokenizer = tokenizer,
)


def InputExampleConverter(df): 
    dataset=[]
    count=0
    violation_sentence = df["sentence"]
    label=df["label"]
    print(label)
    context=df["context"]
    print("Creating Dataset")     
    for i in violation_sentence: 
        dataset.append(InputExample(guid=count,text_a=context[count],text_b=i,label=label[count]))
        count=count+1
    return(dataset)

training_2005=InputExampleConverter(training_2005.reset_index())
val_2005=InputExampleConverter(val_2005.reset_index())
test_2005=InputExampleConverter(test_2005.reset_index())    


training_2011=InputExampleConverter(training_2011.reset_index())
val_2011=InputExampleConverter(val_2011.reset_index())
test_2011=InputExampleConverter(test_2011.reset_index())   

from openprompt import PromptDataLoader
data_loader_train_2005 = PromptDataLoader(
    dataset = training_2005,
    tokenizer = tokenizer,
    template = promptTemplate,
    tokenizer_wrapper_class=WrapperClass,
    shuffle=True
)

data_loader_val_2005 = PromptDataLoader(
    dataset = val_2005,
    tokenizer = tokenizer,
    template = promptTemplate,
    tokenizer_wrapper_class=WrapperClass,
    shuffle=True
)

data_loader_test_2005 = PromptDataLoader(
    dataset = test_2005,
    tokenizer = tokenizer,
    template = promptTemplate,
    tokenizer_wrapper_class=WrapperClass,
    shuffle=True
) 

data_loader_train_2011 = PromptDataLoader(
    dataset = training_2011,
    tokenizer = tokenizer,
    template = promptTemplate,
    tokenizer_wrapper_class=WrapperClass,
    shuffle=True
)

data_loader_val_2011 = PromptDataLoader(
    dataset = val_2011,
    tokenizer = tokenizer,
    template = promptTemplate,
    tokenizer_wrapper_class=WrapperClass,
    shuffle=True
)

data_loader_test_2011 = PromptDataLoader(
    dataset = test_2011,
    tokenizer = tokenizer,
    template = promptTemplate,
    tokenizer_wrapper_class=WrapperClass,
    shuffle=True
) 


use_cuda = True
if use_cuda:
    promptModel_2005=  promptModel_2005.cuda()
    promptModel_2011=  promptModel_2011.cuda()
device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
# Now the training is standard
from transformers import  AdamW, get_linear_schedule_with_warmup
loss_func = torch.nn.CrossEntropyLoss()


def trainer(promptModel,data_loader_train,data_loader_val,data_loader_test,name):
 optimizer = AdamW(promptModel.parameters(), lr=1e-5)   
 for epoch in range(2):
     prev_score=0
     tot_loss=0
     val_score=[]
     test_score=[]
     for step, inputs in tenumerate(data_loader_train): 
         if use_cuda: 
             inputs = inputs.to(device) 
        #print(step)    
         logits = promptModel(inputs)
         logits=logits.to(device)
         labels = inputs['label']
         labels=labels.to(device)
         loss = loss_func(logits,labels.type(torch.LongTensor).to(device))
         loss.backward()
         tot_loss += loss.item()
         optimizer.step()
         optimizer.zero_grad()
         if step %5000 ==1: 
             print("Epoch {}, average loss: {}".format(epoch, tot_loss/(step+1)), flush=True)
             try: 
                torch.save({ 
                    'epoch': epoch,
                    'model_state_dict': promptModel.state_dict(), 
                    'optimizer_state_dict': optimizer.state_dict(),
                    'loss': loss 
                    },os.path.join(path,name))
                
             except:
                continue
     allpreds = []
     alllabels = []
     print("getting Test score after epoch "+ str(epoch))
     for step, inputs in tenumerate(data_loader_test): 
         if use_cuda: 
             inputs = inputs.cuda()
         logits = promptModel(inputs)
         labels = inputs['label']
         alllabels.extend(labels.cpu().tolist())
         allpreds.extend(torch.argmax(logits, dim=-1).cpu().tolist())

     print(f1_score(alllabels,allpreds,average="micro" ))
     print(classification_report(alllabels,allpreds))   
trainer(promptModel_2005,data_loader_train_2005,data_loader_val_2005,
        data_loader_test_2005,"PromptModel2005.pt")

trainer(promptModel_2011,data_loader_train_2011,data_loader_val_2011,
        data_loader_test_2011,"PromptModel2011.pt")
