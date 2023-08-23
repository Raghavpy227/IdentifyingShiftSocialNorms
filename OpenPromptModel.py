# -*- coding: utf-8 -*-
"""
Created on Wed Jul 19 15:45:23 2023

@author: sragh

This code aims to generate, train and evaluate an OpenPrompt model to detect norm violation when the external context for the comment is provided. 
"""

#Importing all the necessary libraries and files
import pandas as pd
from openprompt.data_utils import InputExample
import torch
import os
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import balanced_accuracy_score,f1_score,classification_report
from sklearn.model_selection import train_test_split
from openprompt.config import get_config, save_config_to_yaml
from yacs.config import CfgNode
import redditcleaner
import pandarallel
from tqdm.contrib import tenumerate
path=r"C:\Users\py22715\OneDrive - University of Bristol\Documents\Python Scripts"
df=pd.read_csv(os.path.join(path,"RS_2021-07_violations.csv"))

df=df.reset_index()


# Defining possible of classes of norm violations

classes = [ 
    "racial_slur",
    "self_harm",
    "Homophobia",
    "Incivility",
    "harrassment",
    "No Violations"
]

#label encoding all norm violation types and printing the mapping for it
encoder = LabelEncoder()
df["label"]=encoder.fit_transform(df["violation"])

le_name_mapping = dict(zip(encoder.classes_, encoder.transform(encoder.classes_)))

print(le_name_mapping)

#Loading the pretrained model
from openprompt.plms import load_plm
from openprompt.lm_bff_trainer import LMBFFClassificationRunner,ClassificationRunner
plm, tokenizer, model_config, WrapperClass = load_plm("bert", "bert-base-cased")


#defining prompt template
from openprompt.prompts import ManualTemplate

promptTemplate = ManualTemplate(
    text = '{"placeholder":"text_a"} was the context for {"placeholder":"text_b"}, Which violation is it? {"mask"} ',
    tokenizer = tokenizer,
)

#Generating a dictionary for all the bad words and using it to generate a verbalizer
bad_words = {
    "racial_slur": ["nigga","nigger","uncle tom","negro","niggerhead","house slave","monkeyboy"],
    "self_harm": ["kill yourself", "commit suicide"],
    "Homophobia":["lesbo","faggot","fag",'cocksucker'],
    "Incivility":["dickhead","twat","cunt","whore","retard","bitch","asshole","dimwit","bullshit","fuck u","fuck you","motherfuck"],
    "harrassment":["penis","pussy","dick","tits","moron","suck dick","sexy bitch"],
    "No Violations":["clarify","Obama","car","engine","pasta","water"]
}
bad_set=set()
for k,v in bad_words.items():
    for i in bad_words[k]: 
        bad_set.add(i)
all_set=set()
for i in df["context"]:
   for k in i.split(' '):
       all_set.add(k.lower())
    
no_vio = all_set.difference(bad_set)  
no_vio=list(no_vio)
no_vio=no_vio[0:len(no_vio):5000]

    
 
from openprompt.prompts import ManualVerbalizer
promptVerbalizer = ManualVerbalizer(
    classes = classes,
    label_words = {
        "racial_slur": ["nigga","nigger","uncle tom","negro","niggerhead","house slave","monkeyboy"],
        "self_harm": ["kill yourself", "commit suicide"],
        "Homophobia":["lesbo","faggot","fag",'cocksucker'],
        "Incivility":["dickhead","twat","cunt","whore","retard","bitch","asshole","dimwit","bullshit","fuck u","fuck you","motherfuck"],
        "harrassment":["penis","pussy","dick","tits","moron","suck dick","sexy bitch"],
        "No Violations": no_vio
    },
    tokenizer = tokenizer,
)


        
#creating a model for norm violations
from openprompt import PromptForClassification
promptModel = PromptForClassification(
    template = promptTemplate,
    plm = plm,
    verbalizer = promptVerbalizer,
    freeze_plm=False,
    plm_eval_mode=False
)

#Splitting data and converting it into Input example objects, which will have the context and the query comment
print("Splitting Data")

data_train_val , data_test = train_test_split(df,train_size=0.8,random_state=2018,stratify=df['label'])
data_train,data_val = train_test_split(data_train_val,train_size=0.25,random_state=2018,stratify=data_train_val['label'])

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
data_train=InputExampleConverter(data_train.reset_index())
data_val=InputExampleConverter(data_val.reset_index())
data_test=InputExampleConverter(data_test.reset_index())    

        

#creating data loaders for cleaned and splitted data 
from openprompt import PromptDataLoader
data_loader_train = PromptDataLoader(
    dataset = data_train,
    tokenizer = tokenizer,
    template = promptTemplate,
    tokenizer_wrapper_class=WrapperClass,
    shuffle=True
)

data_loader_val = PromptDataLoader(
    dataset = data_val,
    tokenizer = tokenizer,
    template = promptTemplate,
    tokenizer_wrapper_class=WrapperClass,
    shuffle=True
)

data_loader_test = PromptDataLoader(
    dataset = data_test,
    tokenizer = tokenizer,
    template = promptTemplate,
    tokenizer_wrapper_class=WrapperClass,
    shuffle=True
)



predictions=[]

use_cuda = True
if use_cuda:
    promptModel=  promptModel.cuda()
device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
# Now the training is standard
from transformers import  AdamW, get_linear_schedule_with_warmup
loss_func = torch.nn.CrossEntropyLoss()
no_decay = ['bias', 'LayerNorm.weight']
# it's always good practice to set no decay to biase and LayerNorm parameters
optimizer_grouped_parameters = [
    {'params': [p for n, p in promptModel.named_parameters() if not any(nd in n for nd in no_decay)], 'weight_decay': 0.01},
    {'params': [p for n, p in promptModel.named_parameters() if any(nd in n for nd in no_decay)], 'weight_decay': 0.0}
]

#uncomment if you want to save data loaders saved.
#torch.save({"train":data_loader_train,"test":data_loader_test,"val":data_loader_val},os.path.join(path,"DataLoaders8020.pt"))
#print("Saved Loaders")

#Uncomment if you want to load saved dataloaders
'''
data_loaders=torch.load(os.path.join(path,'DataLoaders8020.pt'))
data_loader_test=data_loaders['test']
data_loader_train=data_loaders['train']
data_loader_val=data_loaders['val']
'''
#uncomment if you want to load a preiously trained dataloader
#checkpt = torch.load(os.path.join(path,"violation_type_model_chkpt.pt"))
#promptModel.load_state_dict(checkpt["model_state_dict"])

#e=checkpt["epoch"]

#initializing Data loaders
optimizer = AdamW(promptModel.parameters(), lr=1e-5)
#optimizer.load_state_dict(checkpt['optimizer_state_dict'])
#loss=checkpt['loss']
#loss.backward()


#code for Training the model

for epoch in range(9):
    tot_loss = 0
    prev_score=0
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

            'loss': loss,

            },os.path.join(path,"violation_type_model_chkpt.pt"))
                
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
    current=f1_score(alllabels,allpreds,average="micro" )      
    if prev_score < current:
        prev_score=current
        torch.save(promptModel,os.path.join(path,"violation_detector.pt")) 
    allpreds = []
    alllabels = []
    print("getting validation score after epoch "+ str(epoch))
    for step, inputs in tenumerate(data_loader_val):
        if use_cuda:
           inputs = inputs.cuda()
        logits = promptModel(inputs)
        labels = inputs['label']
        alllabels.extend(labels.cpu().tolist())
        allpreds.extend(torch.argmax(logits, dim=-1).cpu().tolist())
        print(f1_score(alllabels,allpreds,average="micro" ))
        print(classification_report(alllabels,allpreds))     
    
            
torch.save(promptModel,os.path.join(path,"violation_detector.pt"))   
allpreds = []
alllabels = []
for step, inputs in tenumerate(data_loader_test):
    if use_cuda:
        inputs = inputs.cuda()
    logits = promptModel(inputs)
    labels = inputs['label']
    alllabels.extend(labels.cpu().tolist())
    allpreds.extend(torch.argmax(logits, dim=-1).cpu().tolist())

print(f1_score(alllabels,allpreds,average="micro" ))
print(classification_report(alllabels,allpreds))      
torch.save(promptModel,os.path.join(path,"violation_detector.pt"))     

       
#print(balanced_accuracy_score(df["violation"],predictions ))
