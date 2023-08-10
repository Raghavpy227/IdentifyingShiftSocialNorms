import pandas as pd
from openprompt.data_utils import InputExample
import torch
import os
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import balanced_accuracy_score,f1_score
from sklearn.model_selection import train_test_split
from openprompt.config import get_config, save_config_to_yaml
from yacs.config import CfgNode


#os.environ['CUDA_LAUNCH_BLOCKING'] = "1"

path=r"C:\Users\py22715\OneDrive - University of Bristol\Documents\Python Scripts"
path_check=r"C:\Users\py22715\OneDrive - University of Bristol\Documents\Python Scripts\Checkpoints_detector"
df=pd.read_csv(os.path.join(path,"RS_2012-03_violations.csv"))
#df=df.iloc[0:300,:]

classes = [ # There are two classes in Sentiment Analysis, one for negative and one for positive
    "Yes","No"
]

encoder = LabelEncoder()
df["label"]=encoder.fit_transform(df["is_violation"])

from openprompt.plms import load_plm
from openprompt.lm_bff_trainer import LMBFFClassificationRunner,ClassificationRunner
plm, tokenizer, model_config, WrapperClass = load_plm("bert", "bert-base-cased")



#from transformers import BertConfig

#config = BertConfig()
#print(dir(config))

from openprompt.prompts import ManualTemplate

promptTemplate = ManualTemplate(
    text = '{"placeholder":"text_a"} are all the comments, Do they contain some violation? {"mask"} ',
    tokenizer = tokenizer,
)

from openprompt.prompts import ManualVerbalizer
promptVerbalizer = ManualVerbalizer(
    classes = classes,
    label_words = {
        "Yes":["nigga","nigger","coon","uncle tom","negro","niggerhead","house slave","monkeyboy","kill yourself", "commit suicide",
               "lesbo","faggot","fag","cocksucker","dickhead","twat","cunt","whore","retard","bitch","asshole","dimwit","bullshit"
               "penis","pussy","dick","tits"]
        ,"No":["Hi","That is good", "Where was it?"]
       
    },
    tokenizer = tokenizer,
)

from openprompt import PromptForClassification
promptModel = PromptForClassification(
    template = promptTemplate,
    plm = plm,
    verbalizer = promptVerbalizer,
    freeze_plm=False
)

dataset=[]
count=0
violation_sentence = df["violation sentence"]
label=df["label"]
context=df["context"]

for i in violation_sentence:
    dataset.append(InputExample(guid=count,text_a=context[count],label=label[count]))
    count=count+1

data_train_val , data_test = train_test_split(dataset,train_size=0.8)
data_train,data_val = train_test_split(data_train_val,train_size=0.2)


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

#runner = LMBFFClassificationRunner(data_train,data_val,data_test,promptVerbalizer,promptTemplate,model_config)
#res=runner.run()

predictions=[]

use_cuda = True
if use_cuda:
    promptModel=  promptModel.cuda()
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
# Now the training is standard
from transformers import  AdamW, get_linear_schedule_with_warmup
loss_func = torch.nn.CrossEntropyLoss()
no_decay = ['bias', 'LayerNorm.weight']
# it's always good practice to set no decay to biase and LayerNorm parameters
optimizer_grouped_parameters = [
    {'params': [p for n, p in promptModel.named_parameters() if not any(nd in n for nd in no_decay)], 'weight_decay': 0.01},
    {'params': [p for n, p in promptModel.named_parameters() if any(nd in n for nd in no_decay)], 'weight_decay': 0.0}
]

# Look aty the data loader for this identify line number  135 train and then evaluate the model
optimizer = AdamW(promptModel.parameters(), lr=1e-9)

for epoch in range(5):
    tot_loss = 0
    for step, inputs in enumerate(data_loader_train):
        if use_cuda:
            inputs = inputs.to(device)
        logits = promptModel(inputs)
        logits=logits.to(device)
        labels = inputs['label']
        labels=labels.to(device)
        loss = loss_func(logits,labels.type(torch.LongTensor).to(device))
        loss.backward()
        tot_loss += loss.item()
        optimizer.step()
        optimizer.zero_grad()
        if step %1000 ==1:
            print("Epoch {}, average loss: {}".format(epoch, tot_loss/(step+1)), flush=True)
            torch.save({

            'epoch': epoch,

            'model_state_dict': promptModel.state_dict(),

            'optimizer_state_dict': optimizer.state_dict(),

            'loss': loss,

            }, os.path.join(path,"violation_detector_model_chkpt.pt"))


allpreds = []
alllabels = []
for step, inputs in enumerate(data_loader_val):
    if use_cuda:
        inputs = inputs.cuda()
    logits = promptModel(inputs)
    labels = inputs['label']
    alllabels.extend(labels.cpu().tolist())
    allpreds.extend(torch.argmax(logits, dim=-1).cpu().tolist())

print(f1_score(alllabels,allpreds,average="micro" )) 