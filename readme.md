# data_utils
A data utility that will include the functions such as data download & upload & reconstruction & loading, etc..


## Features
- [x] Download
- [ ] Upload
- [ ] Reconstruction
- [ ] Loading

## How to use
### Automatical file download
***Example***
Run 
```bash
python main_sync.py
```
to sync files from FTP server to local directory using the infomation provided in file `default.csv`

---
Run 
```bash
python main_sync.py file.csv
```
to sync files from FTP server to local directory using the infomation provided in file `file.csv`

## About the CSV file
The CSV file currently should contain 6 columns, which is  
```
host,user,passwd,cwd,local_root,file_reg 
```
- `host`: the host address of the FTP server
- `user`: username to login the FTP server, leave it blank if use an anonymous login
- `passwd`: passwd to login the FTP server, leave it blank if use an anonymous login
- `cwd`: current working directory in the FTP server
- `local_root`: local root directory the remote files will download to, subdirectory will be created automatically to coincide with the `cwd`
- `file_reg`: regular expression to match the files in the remote directory `cwd`

See an example in [default.csv](default.csv)

More details can be read in the python script's docstring
[python script](ftp_downloader.py)