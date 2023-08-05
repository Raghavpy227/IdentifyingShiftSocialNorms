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

import pandas as pd 
import re
import os

path=r"C:\Users\sragh\OneDrive\Documents\Dissertation\Data\submissions"
df= pd.read_csv(os.path.join(path,"RS_2021-07.csv"))
#df.drop(["Unnamed: 0"],axis=1,inplace=True)

regex_dict= {
        "racial_slur": [r"(?:nigga|nigger|uncle tom|negro|niggerhead|house slave|monkeyboy)"],
        "self_harm": [r"(?:kill yourself|commit suicide)"],
        "Homophobia":[r"(?:lesbo|faggot|fag)"],
        "Incivility":[r"(?:dickhead|twat|cunt|whore|fuck you|fuck u|retard|bitch|asshole|dimwit|bullshit|cocksucker|motherfuck)"],
        "harrassment":[r"(?:penis|pussy|tits|dick|sexy bitch|suck dick)"]
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
        inter.append(re.split(diff_sp,j))
    else:
        inter.append(j)
    better_split.append(inter)    
        
        
count=0    
df["context"]  = better_split

for i in better_split:
    counter_context=0
    for j in i :
        for m in j: 
            mini_context=0
            check=0 
            for k in regex_dict.keys(): 
                pattern = re.compile('|'.join(regex_dict[k]), re.IGNORECASE)
                matches = pattern.findall(m)
                if len(matches)>0: 
                    violation.append(k)
                    violation_sentence.append(m)
                    subreddit.append(df["subreddit"][counter_row])
                    new_created.append(df["created_date"][counter_row])
                    new_id.append(df["id"][counter_row])
                    t=[]
                    t.append(i[0:counter_context])
                    t.append(j[0:mini_context])
                    subcontexts.append(t)
                    check=1
                    is_violation.append("Yes")
                elif len(matches)==0:
                    continue
                mini_context+=1
        counter_context+=1     
        
            
    if check == 0: 
        violation.append("No Violations")
        violation_sentence.append(" ")
        subreddit.append(df["subreddit"][counter_row])
        new_created.append(df["created_date"][counter_row])
        new_id.append(df["id"][counter_row])
        subcontexts.append(j)
        is_violation.append("No")
                     
                    
            
    counter_row+=1     
                
                
df=pd.DataFrame()
df["id"]=new_id
df["subreddit"]=subreddit
df["created_date"]=new_created
df["context"]=subcontexts
df["is_violation"]=is_violation
df["violation"]=violation
df["violation sentence"]=violation_sentence   


df.to_csv(os.path.join(path,"RS_2012-03_violations.csv"),index=False)          
    

            
            
    
    
    
    
    







