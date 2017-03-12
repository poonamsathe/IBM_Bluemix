import swiftclient
import keystoneclient
import gnupg
from flask import Flask, render_template,request
import os

app = Flask(__name__)

HOST = str(os.getenv('VCAP_APP_HOST','localhost'))
PORT = int(os.getenv('VCAP_APP_PORT', '5050'))

auth_url = " "+ '/v3'
password = " "
project_id = ""
user_id = ""
region_name = ""

conn = swiftclient.Connection(key=password, 
	authurl= auth_url ,
	auth_version='3', 
	os_options={"project_id": project_id, 
				"user_id": user_id, 
				"region_name": region_name})
				
				
cont_name = "containerN"
conn.put_container(cont_name)

print "Container %s created successfully" %(cont_name)


				
@app.route("/")
def main():
     return render_template('form.html')

@app.route('/upload', methods=['POST'])
def upload():

###encryption
	gpg = gnupg.GPG()

### generating RSA key 
	input_data = gpg.gen_key_input(key_type="RSA",
									key_length = 1024, 
									passphrase = 'xxxxx')
	key = gpg.gen_key(input_data)
	print key

#file_name = "file1.txt"
	file_name = request.files['file']
	print(file_name)

	with open(file_name,'rb') as f:
		print f.read()
		status= gpg.encrypt_file(f,'FFD6AA6BCF4E8756')
		print "encrypted"
	
	encrypt_data = str(status)
	encrypted_file = "enc.txt"
	with open(encrypted_file,'w') as data:
		data.write(encrypt_data)
	
	
### uploading the file
	with open(file_name, 'r') as upload_file:
		if(len(file.read())<(1*1024)):
			conn.put_object(cont_name, file_name, encrypt_data, content_type = 'text/plain')
	return render_template('upload.html')
	print file_name
	
	
#list files
@app.route('/lists', methods = ['POST'])	
def lists():
# List objects in a container, and prints out each object name, the file size, and last modified date
	print ("nObject List:")
	for container in conn.get_account()[1]:
		for data in conn.get_container(container['name'])[1]:
			print 'object: {0}t size: {1}t date: {2}'.format(data['name'], data['bytes'], data['last_modified'])
			    
	return render_template('index.html')


### downloading the file
@app.route('/download', methods=['POST'])
def download():
other_file="download.txt"
f_file = "final.txt"
file_name = request.form['downloads']
obj=conn.get_object(cont_name, file_name)
with open(other_file, 'w') as f:
	f.write(obj[1])
print "downloaded"	
status = gpg.decrypt_file(f, passphrase='my passphrase')
#decrypting the file
with open(other_file, 'rb') as d:
	decrypted_data = gpg.decrypt_file(d,passphrase='my_passphrase') 
fdata = str(decrypted_data)
with open(f_file,'w') as data:
	data.write(fdata)
print "decrypted"


### deleting the file 
@app.route('/delete',methods=['POST'])
def delete():
file_name = request.form['deleteFile']
conn.delete_object(cont_name, file_name)
print "deleted" 
return "deleted"



if __name__ == "__main__":
    app.run(host=HOST, port=PORT)
	
	
