#Karthikeyan Rajamani #UTA Id:1001267157
#CSE6331 -Cloud Computing
#Programming Assignment2
#references
##http://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world
##http://python-cloudant.readthedocs.org/en/latest/getting_started.html#getting-started
##http://stackoverflow.com/questions/20007721/parsing-returned-html-from-jquery-ajax-request
##http://stackoverflow.com/questions/21626048/unable-to-pass-jinja2-variables-into-javascript-snippet
#bleumix url of the assignment2:http://karthikasst2.mybluemix.net/
from flask import Flask,render_template,request,send_file
import hashlib,json
import os.path,time,datetime
from cloudant.account import Cloudant
import gnupg
import StringIO
#cloudant credentials
username='888fc0a5-23cb-4864-9f64-b0dec80c60c4-bluemix'
password='xxxxxx'
urlx='https://888fc0a5-23cb-4864-9f64-b0dec80c60c4-bluemix:d2f6c6f2ee1cef7a8855205869364eaf48ca8d305d4f0bf198a413d6f5e50e79@888fc0a5-23cb-4864-9f64-b0dec80c60c4-bluemix.cloudant.com'
client = Cloudant(username, password, url=urlx)
client.connect()
filelist=[]
fid=[]
# 1.#initializatins-values from BlueMix environmental variables
import swiftclient
import keystoneclient
import urllib3
import certifi
import gnupg
import os
auth_url='https://identity.open.softlayer.com'+ '/v3'
password="yx/sOzF7ZJ332-TK"
project_id='51810f8c4088469c88cccb30990c7ec2'
user_id='27581762cff64e2482e7aa05ec8dff7b'
region_name='dallas'
print 'Connection parameters initialized..'

#2.set connection parameters
conn=swiftclient.Connection(key=password,
                            authurl=auth_url,
                            auth_version='3',
                            os_options={"project_id":project_id,
                                        "user_id":user_id,
                                        "region_name":region_name})
print 'Connected to bluemix with swiftclient..'

# generate the file list from cloudant
def list():
    filelist[:]=[]
    fid[:]=[]
    try:
        my_database = client['my_database'] # open my_database if it exists
        #return 'Database opened'
    except KeyError:
        pass
    for document in my_database:
        filelist.append(document['filename']+'-Ver'+str(document['version']))
        fid.append(document['_id'])
    return filelist,fid
#save the file name, contents, version in cloudant     
def save(filename,version,hashvalue,contents,moddate):
    filelist[:]=[]
    fid[:]=[]
    #return "Connected.."
    try:
        my_database = client['my_database'] # open my_database if it exists
        #return 'Database opened'
    except KeyError:
        my_database = client.create_database('my_database') #create my_database if it does not exist
        #return 'Database created'
    if my_database.exists(): # check if database exists
        #return 'DataBase Exists'
        pass
    #return 'Values inserted'
    status='Warning: file already exists'
    difffile=True
    diffhash=True
    for document in my_database:
        filelist.append(document['filename'])
        fid.append(document['_id'])
        if document['filename']==filename:
            difffile=False
        if document['hashvalue']==hashvalue:
            diffhash=False
    if (difffile==True or diffhash==True or(difffile==True and diffhash==True)):
        if (difffile==False and  diffhash==True):
            version=document['version']+1
        data={'filename':filename,
          'version':version,
          'hashvalue':hashvalue,
          'modifieddate':moddate,
          'contents':contents
          }
        my_document = my_database.create_document(data)
        status='is Saved'
        #return json.dumps({'html':'<span>All fields good !!</span>'})
    #return filelist[2]
        list()
    return render_template('index.html',status= 'File: '+
                           filename+':'+status,filelist=filelist,fid=fid,i=0)

#dlf='.\\static\\downloads\\' # for local windows
dlf='./static/downloads/' # for bluemix
#dlf=app.config[dlf]

app = Flask(__name__)
port = int(os.getenv('VCAP_APP_PORT', 8080))

# create the downloadfile in server & pass the full path to the browser for download
@app.route("/download", methods=['GET', 'POST'])  
def download():
    if request.method == 'POST':
        selectedfidd = request.form['dlid']
        my_database = client['my_database']
        my_document = my_database[selectedfidd]
        dlfilename=my_document['filename']
        contents=my_document['contents']
        return contents.readlines()
        fullpath=dlf+dlfilename
        dfile=open(fullpath,'w')
        dfile.write(str(contents))
        dfile.close()

        gpg=gnupg.GPG(gnupghome =  os.getcwd()+'/.gnupg')
        file=open(fullpath,'rb')
        filecontents=file.read()
        file.close()
        decrypted_data=gpg.decrypt(filecontents,passphrase='cloudpass')
        file=open(fullpath,'w')
        file.write(str(decrypted_data))
        file.close()
        return  fullpath

#Delete with jquery Ajax
@app.route("/ajax", methods=['GET', 'POST'])  
def js():
    if request.method == 'POST':
        selectedfid = request.form['mydata']
        # First retrieve the document
        my_database = client['my_database'] 
        my_document = my_database[selectedfid]
        # Delete the document
        my_document.delete()
        list()
        return render_template('index.html',filelist=filelist,fid=fid)
        #return selectedfid

# root with file list & upload
@app.route("/")
def start():
    list()
    return render_template('login.html')
    return render_template('index.html',filelist=filelist,fid=fid)
user=''
# prepare the file & call save to store in cloudant
@app.route("/",methods=['GET', 'POST'])    
def upload():
    # if request.method == 'POST':
    #     file = request.files['file']
    #     file_name=str(file.filename)
    #     #file=open(file)
    #     filecontents=file.read()
    #     conn.put_object(
    #             'Mystore',
    #             file_name,
    #             contents=filecontents,
    #             content_type='text/plain'
    #             )

        file_name='users.txt'
        dfileref=conn.get_object('Mystore',file_name)
        writefile=os.path.dirname(__file__)+'\\'+file_name # file downloaded
        dfile=open(writefile,'w')
        dfile.write(dfileref[1])
        dfile.close()
        names=[]
        with open(writefile) as f:
          lines = f.readlines()
          for line in lines:
              lines1=line.split(',')[:1]
              names.append(lines1)
          #return lines[1]
        c=0
        username= request.form['uname']
        #return str(names)
        for name in names:
         #return  name[0]
         if name[0]==username:
          #return name[0]
          print 'Welcome %s!!'%name
          #print name
          global user
          user=name
          c=c+1
        #return str(c)
        #c=10
        if (c>0):
         return render_template('index.html',name=user)
         return user
        else:
         return render_template("login.html",loginstatus=username+ ' : not authorised')
    #     file = request.files['file']
    #     file_name=str(file.filename)
    #     readcontents=file.read().decode('utf-8')
    #     hash_value=hashlib.md5(readcontents).hexdigest()
    #     modifieddate=str(datetime.datetime.now())
    #     ver=1
    #     return save(file_name,ver,hash_value,readcontents,modifieddate)
    #     #return file_name+':'+str(hashvalue)+':'+contents+':'+modifieddate
    # if request.method == 'GET':
    #     return 'Get called'
       
#test for dubugging  
@app.route("/test", methods=['GET','POST'])
def test1():
    if request.method == 'POST':
        filename = request.form['dfilename']
        return filename
    if request.method == 'GET':
         return 'Get called'
           
if __name__ == "__main__":
    app.run(debug=True)    # for local windows
    #app.run(host='0.0.0.0', port=port) # for bluemix

