This is a simple console line interface, which can backup a folder(which doesn't contain any subfolder) to dropbox "securely" and it also can restore the directory. This tool has a lot of limitation, so it's mostly just another example how you can use the dropbox api with python.

## How it works?
 * backup:
1. Makes a configuration file, which contains the paths for every file and also store every file's uuid.
2. Encrypt every file in the folder.
3. Archives the encrypted files.
4. Uploads to dropbox.

 * restore:
1. Download archive and unpack it.
2. Decrypt every archived file.
3. Restore the files based on the file paths inside the configuration file. File's uuid is used to identify every file in the archived file.

* listing backups: simply use a dropbox api call.

## How to use?

Get a token key from dropbox by registering a dropbox app and insert the token in the dropboxbackend.py file.
``` 
$ git clone https://github.com/StrykerKKD/dropbox-backup.git

$ cd dropbox-backup

$ source activate [your_virtualenviroment_name]

$ pip install -e . 

$ dropboxbackup
```

## Coding Style
I avoided using OOP and tried to write the code in a functional way. The code also has typing information for almost every function.
