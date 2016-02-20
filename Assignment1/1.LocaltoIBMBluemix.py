#Karthikeyan Rajamani #UTA Id:1001267157
#CSE6331 -Cloud Computing
#Programming Assignment1
#ref:https://pythonhosted.org/python-gnupg/
#ref:http://stackoverflow.com/questions/23459323/how-do-i-do-symmetric-encryption-with-the-python-gnupg-module-vers-1-2-5
# a file localtoblueoriginal.txt is created in the current directory
#IBM bluemix app Environmental variables of the app.
import swiftclient
import keystoneclient
import urllib3
import certifi
import gnupg
import os
# 1.#initializatins-values from BlueMix environmental variables
auth_url='https://identity.open.softlayer.com'+ '/v3'
password="xxxxxxx"
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

#3. Create container named Mystore in bluemix
ContainerName = 'Mystore'
conn.put_container(ContainerName)
print '%s Container created in Bluemix cloud..'% ContainerName

#3.gpg generate key
gpg=gnupg.GPG(gnupghome =  os.getcwd()+'/.gnupg')
input_data=gpg.gen_key_input(key_type="RSA",key_length=1024,
                             passphrase='cloudpass')
key=gpg.gen_key(input_data)

#4.gpg encrypt file with public key & store locally
originalfilename='localtoblueoriginal.txt' # source file from current local folder
encryptedfilename='localtoblueencrypted.txt'
with open(originalfilename,'rb') as f:
    status= gpg.encrypt_file(f,None,passphrase='cloudpass',
                             symmetric='AES256',output=encryptedfilename)
print 'Source file %s encrpted & saved as %s in current directory..'%(originalfilename,encryptedfilename)

#5. upload the encrypted file to bluemix
option=raw_input('Do you want to store in encrpted(1)/plain(2)')
# print originalfilename
# print encryptedfilename
# print ContainerName1
# print ContainerName2
if option=='1':
    print '1'
    ContainerName='encrypted'
    filename=encryptedfilename
if option=='2':
    ContainerName='plain'
    filename=originalfilename
file=open(encryptedfilename)
filecontents=file.read()
conn.put_object(
                ContainerName,
                encryptedfilename,
                contents=filecontents,
                content_type='text/plain'
                )
print '%s uploaded to bluemix %s container..'%(encryptedfilename,ContainerName)

#6. Download the file from bluemix
downloadoption=raw_input('Do you want to download the encrypted file from Bluemix Y/N:')
if(downloadoption=='y' or downloadoption=='Y' ):
    downloadfilename=encryptedfilename # file stored in bluemix
    dfileref=conn.get_object(ContainerName,downloadfilename)
    writefile=downloadfilename+'-downloaded.txt' # file downloaded
    dfile=open(writefile,'w')
    dfile.write(dfileref[1])
    dfile.close()
    print " File %s downloaded in local folder.." %writefile
    
#7. Encrypt the downloaded file locally
file=open(encryptedfilename)
filecontents=file.read()
decrypted_data=gpg.decrypt(filecontents,passphrase='cloudpass')
printdata=raw_input( 'Do you want to print the data from the decrypted file Y/N:')
decryptedfilename=encryptedfilename+'-decrypted.txt'
decfile=open(decryptedfilename,'w')
decfile.write(str(decrypted_data))
decfile.close()
print 'File decrypted & stored as %s'%decryptedfilename
if (printdata=='y' or printdata=='Y'):
    print 'Reading decrypted contents of the file'
    print decrypted_data

#8.list objects from bluemix
listobjects=raw_input("Do you want to list the objects from bluemix? Y/N:")
if (listobjects=='y' or listobjects=='Y'):
    for data in conn.get_account()[1]:
        for data in conn.get_container(ContainerName)[1]:
            print 'object:{0}\t size:{1}\t date {2}'.format(data['name'],data['bytes'],data['last_modified'])

#9.Delete file from bluemix
Deletefile=raw_input("Do you want to delete LtoBlueEncrypt.txt from Bluemix? Y/N:")
if (Deletefile=='y' or Deletefile=='Y'):
    conn.delete_object(ContainerName,'LtoBlueEncrypt.txt')
    print ('File ''LtoBlueEncrypt.txt'' deleted from %s in bluemix'%ContainerName)

print 'Exited the program..'


    
        
    
    
    
