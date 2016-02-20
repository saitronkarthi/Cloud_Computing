#Karthikeyan Rajamani #UTA Id:1001267157
#CSE6331 -Cloud Computing
#Programming Assignment3 -AWS & S3
#references
#http://www.datasciencebytes.com/bytes/2015/02/24/running-a-flask-app-on-aws-ec2/
#boto3.readthedocs.org/en/latest/guide/migrations3.html#creating-a-bucket
#http://stackoverflow.com/questions/30249069/listing-contents-of-a-bucket-with-boto3
#http://blogs.aws.amazon.com/security/post/Tx3VRSWZ6B3SHAV/Writing-IAM-Policies-How-to-grant-access-to-an-Amazon-S3-bucket
from flask import Flask, render_template,request
import boto3,os
from boto3 import client
from boto3.session import Session
#AWS session with Credentials ID & Key removed for security
session = Session(aws_access_key_id ='xxxx',
                  aws_secret_access_key='xxxx',
                  region_name='us-west-2'
                  )

s3 = session.resource('s3')
s3c=session.client('s3')
userfile=os.path.dirname(__file__)+'/awsusers.txt'
ALLOWED_EXTENSIONS = ['jpg','png','jpeg']
filelist=[]
#upload file in s3 can be called if required
def createbucket():
    s3.create_bucket(Bucket='karasst3')
    for bucket in s3.buckets.all():
          print str(bucket.name)

#upload the permitted users file can be called if required
def uploadusers():
     userfile=os.path.dirname(__file__)+'/awsusers.txt' #for windows locally
     data=open(userfile,'rb')
     s3.Bucket('awsusers').put_object(Key='awsusers.txt', Body=data)
     print data
     with open(userfile) as f:
          lines = f.readlines()
          print lines[1] # for testing if the names from the file are read

app = Flask(__name__)

@app.route('/')
def hello_world():
      return render_template('login.html')

@app.route('/',methods=['GET', 'POST'])# authorize user, login in to upload page
def login():
    #pass
     if request.method== 'POST':
       c=0
       username= request.form['uname']
       f=s3.Object('awsusers','awsusers.txt').get()
       contents=f['Body'].read()
       names=contents.split()
       for name in names:
        if name==username:
         print 'Welcome %s!!'%name
         print name
         global user
         user=name
         c=c+1
       if (c>0):
        return render_template('upload.html',name=user)
        return user
       else:
        return render_template("login.html",loginstatus=username+ ' : not authorised')


@app.route('/upload',methods=['GET','POST']) # upload iamages
def upload():
    if request.method == 'POST':
        file = request.files['file']
        file_name=str(file.filename)
        contents=file.read()
        fileextension= file_name.split('.',1)[1]
        if (fileextension in ALLOWED_EXTENSIONS):
            s3.Bucket('karasst3').put_object(Key=file_name, Body=contents)
            return render_template('upload.html',name=user,extstatus=file_name+": has been uploaded to s3 bucket")
        else:
             return render_template('upload.html',name=user,extstatus="This file extension cannot be uploaded.")
    if request.method == 'GET':
        global user
        return render_template('upload.html',name=user)

@app.route('/view')
def view():
    filenames=[]
    filelist[:] = []
    for key in s3c.list_objects(Bucket='karasst3')['Contents']:
        filename=key['Key']
        fullpath=os.path.dirname(__file__)+'/static/downloads/'+filename# for EC2
        imgurl="https://s3.amazonaws.com/karasst3/"+filename # fetched from public policy set bucket
        filelist.append(imgurl)
        print filelist
        filenames.append(str(filename))
    return render_template("view.html",filelist=filelist,filename=filenames)

@app.route("/delete",methods=['GET', 'POST'])
def delete():
   if request.method == 'POST':
        selectedfid = request.form['mydata']
        s3.Object('karasst3', selectedfid).delete()

@app.route("/imgview/<fname>",methods=['GET', 'POST'])
def imgview(fname):
            filenames=[]
            filelist[:] = []
            for key in s3c.list_objects(Bucket='karasst3')['Contents']:
                file_name=key['Key']
                imgurl="https://s3.amazonaws.com/karasst3/"+file_name # fetched from public policy set bucket
                filelist.append(imgurl)
                print filelist
                filenames.append(str(file_name))
            imgview="https://s3.amazonaws.com/karasst3/"+fname
            return render_template("view.html",filelist=filelist,filename=filenames,imgview=imgview)



if __name__ == '__main__':
    app.run(debug=True)
