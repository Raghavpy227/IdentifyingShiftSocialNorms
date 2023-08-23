# -*- coding: utf-8 -*-
"""
Created on Sun Jul 23 18:11:12 2023

@author: sragh
This file will be used to tag the Comments and seperate them into ,
 context , final comment which broke the rule and the rule tagging
 
The rules which are identified so far are 
possible violations

1. Information leak? - When the @, or any other personal ID has been leaked with/without consent. Check the context column for that 

Example her @ is @kindacringygirlngl
the bully name is @ something
sharing personal ids Michelabj7@gmail.com


2 Incivility - Any abuse 
fuck off you dim witted crunt
3. Racial Slurs :

Gosh, I wonder why Clifton Hicks who has a well-documented history of making some problematic racial remarks - including calling some people "white coons" - is going around spamming multiple reddits with 

4. Homophobia - Those guys at star wars hq are fuckin faggot,gay lover,weirdo gamers who have never talked to a girl, awkard as fuck live in mothers basement, have nerdy ass lisp voices, clickbait trash at Battlefront faggots

5. Xenophobia -
Wait, science trusts Chinese data now?

6. self-harm - kill yourself?

7. Harrassment - Any NSFW rules

8. Spam

9 Trolling

If there are more than one violations try we will replicate the row upto the next violation and then tag it this will be treated as new observation(potentially repeating the data??
                                                                                                                                                    ) 
initially we will tag the data from regex and then read the data to rectify any possible changes
"""
#Importing all the necessary libraries

import pandas as pd 
import re
import os
from random import randrange
#filename which needs to be read and path to read the file
filename=''
path=r"C:\Users\sragh\OneDrive\Documents\Dissertation\Data\s3_submissions_downloads"
df= pd.read_csv(os.path.join(path,filename))
#df.drop(["Unnamed: 0"],axis=1,inplace=True)
df=df[df["context"] != '[]']
df=df.reset_index()

#Initializing Reddit Dict to tag depending upon phrases
regex_dict= {
        "racial_slur": [r"(?:nigga|nigger|uncle tom|negro|niggerhead|house slave|monkeyboy)"],
        "self_harm": [r"(?:kill yourself|commit suicide)"],
        "Homophobia":[r"(?:lesbo|faggot|fag)"],
        "Incivility":[r"(?:dickhead|twat|cunt|whore|fuck you|fuck u|retard|bitch|asshole|dimwit|bullshit|cocksucker|motherfuck)"],
        "harrassment":[r"(?:penis|pussy|tits|dick|sexy bitch|suck dick|moron)"]
    }
#"personal_id":[r"(?:[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,})"]
#"Spam": [r"(?:\(\S+\) \S+: .*(\S)(?: *\1){9,}.*)"


is_violation=[]
violation=[]
violation_sentence=[]
full_context=df["context"]
new_id=[]
subcontexts=[]
subreddit=[]
new_created=[]
counter_row=0
df.drop(["context"],axis=1,inplace=True)

# Splitting Context to generate a cleaner form of context
new_context=[]
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

# This for loop iterates through the context column and tags comments as per occurance using regex
for i in better_split:
    counter_context=0
    for j in i : 
        if j.lower() =="deleted" or j.lower() =='removed'  :
            del j
            continue
        check=0
        for k in regex_dict.keys(): 
            pattern = re.compile('|'.join(regex_dict[k]), re.IGNORECASE)
            matches = pattern.findall(j)
            if len(matches)>0: 
                violation.append(k)
                violation_sentence.append(j)
                subreddit.append(df["subreddit"][counter_row])
                new_created.append(df["created_date"][counter_row])
                new_id.append(df["id"][counter_row])
                subcontexts.append(i[0:counter_context])
                check=1
                is_violation.append("Yes")
            elif len(matches)==0:
                continue
                
        counter_context+=1     
        
            
    if check == 0:    #This block of code is used to generate two random Comments-context pairs from the comment tree if none of the comments violate any norm
        
        itr=0
        while itr<2:
            try: 
                
                rand_index=randrange(1,len(i),1) 
                violation.append("No Violations")
                violation_sentence.append(i[rand_index])
                subcontexts.append(i[0:rand_index])
                subreddit.append(df["subreddit"][counter_row])
                new_created.append(df["created_date"][counter_row])
                new_id.append(df["id"][counter_row])
                is_violation.append("No")
                itr+=1
            except:
                 itr=itr+1
                
                     
                    
            
    counter_row+=1     
                
                
df=pd.DataFrame()
df["id"]=new_id
df["subreddit"]=subreddit
df["created_date"]=new_created
df["context"]=subcontexts
df["is_violation"]=is_violation
df["violation"]=violation
df["sentence"]=violation_sentence
df['sentence']=df['sentence'].astype('str')

#filtering to remove small contexts and sentences , Then outputting the files
mask=df['sentence'].str.len() >15
df=df.loc[mask]
mask=df['context'].str.len() >5
df=df.loc[mask]
df.to_csv(os.path.join(path,filename),index=False)          
  

            
            
    
    
    
    
    







