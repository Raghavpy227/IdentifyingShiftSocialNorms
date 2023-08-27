'''
The Aim of this code is to extract the comment tree and upload the new csv to AWS Bucket
'''

#importing all the necessary libraries
import pandas as pd
import os
import praw
from praw.models import Comment, Submission
from praw.models.comment_forest import CommentForest
import datetime
from multiprocessing import Pool
import boto3

 

 
#Initializing a working path and a S3_client
path = r"C:\Users\sragh\OneDrive\Documents\Dissertation\Data\s3_submissions_downloads"
s3_client = boto3.Session(aws_access_key_id='AKIA6IIIHUJETGQMT54O',aws_secret_access_key='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')
s3=s3_client.resource('s3')
s3_bucket=s3.Bucket('csv-extracted-files')
s3_bucket_processed=s3.Bucket('comment-extracted-reddit-files')

 

 
#getting all the objects in the bucket
all_objects=s3_bucket.objects.all()
all_csv=[]
 

for i in all_objects:
    all_csv.append(i.key)
#Getting all the processed file names
already_processed_objects=s3_bucket_processed.objects.all()
processed_csv=[]

for i in already_processed_objects: 
    processed_csv.append(i.key)    

#getting the file names which needs to be processed
to_process_csv=[]
for i in all_csv:
    if i not in processed_csv:
        to_process_csv.append(i)

 
#This section contains all the Reddit credentials needed to get the comment tree. User needs to fill them
username=""
password=""
secret=""
client_id=""
#generating S3 client 
s3_client = boto3.client('s3',aws_access_key_id='AKIA6IIIHUJEZKQH5NEZ',aws_secret_access_key='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')

#generating the reddit instance to query submission ID

reddit = praw.Reddit(
    client_id=client_id,
    client_secret=secret,
    password=password,
    user_agent="Comment Extraction (by u/USERNAME)",
    username=username,
)
#converting date to yyyy-mm-dd
def convertToDate(df):
    created_date=[]
    for i in df["created_utc"]:
        created_date.append(datetime.datetime.fromtimestamp(int(i)))
    df.drop(["created_utc"],axis=1,inplace=True)    
    df["created_date"] = created_date   
    return df

#Function to get the Submission Object based on the ID
def getSubmission(id):
    return Submission(reddit,id)

 

 
#function to get the comment tree based on the submission ID. The function has the exception handling which handles any 404 related errors
def getCommentTree(df):
    context=[]
    count=0
    submissions=[]
    for i in df["id"]:
        try:
            submission = Submission(reddit,i)
            tree= submission.comments._comments
            all_comments=[]

 

            for i in tree:
                comment= i.body
                all_comments.append(comment)

 

            context.append(all_comments) 
            count=count+1
            print(count/len(df["id"]))

 

        except:  
            print("except")
            context.append([])
            count=count+1

 

 

    df["context"]=context    
    return df
count=0

#It Downloads the file from the csv-extracted-files bucket and then executes the get dates and the get comment tree method. 
#The below piece of code is used to regulate the file size by taking top 20000 most populated submissions for the file
#Once the file is created it is uploaded to AWS S3 and deleted from local machine
num_of_comments=25
for i in to_process_csv: 
    print(i)
    s3_client.download_file('csv-extracted-files',Key=i,Filename=os.path.join(path,i))
    df=pd.read_csv(os.path.join(path,i))
    if "context" in df.columns:
        os.remove(os.path.join(path,i))
        continue
    while len(df["num_comments"]) >= 20000: 
        df=df[df["num_comments"]>= num_of_comments]
        num_of_comments+=25
    print("number of sumbissions" +str(len(df["num_comments"])))
    df=convertToDate(df)
    df=getCommentTree(df)
    count=count+1
    print("File Number "+str(count)+" completed")
    df.to_csv(os.path.join(path,i),index=False)
    s3_client.upload_file(os.path.join(path,i),'comment-extracted-reddit-files',i)
    os.remove(os.path.join(path,i))
    print("File Number "+str(count)+" uploaded")
