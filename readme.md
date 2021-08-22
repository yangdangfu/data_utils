# data_utils
A data utility that will include the functions such as data download & upload & reconstruction & loading, etc..

## Features (Working in Progress)

- [x] Download
- [ ] Upload
- [ ] Reconstruction
- [ ] Loading

## Download

### How to use

#### Automatic file download

***Example***
Run 

```bash
python main_sync.py
```

to sync files from FTP server to local directory using the information provided in file `default.csv`. About the CSV file, the user can refer to [About the CSV file](#csv) for more. 

---

Run 

```bash
python main_sync.py file.csv
```

to sync files from FTP server to local directory using the information provided in file `file.csv`

### About the CSV file<a name="csv"></a>
The CSV file defines a specification of the download. The specification includes the FTP server address and the corresponding login signature (`host, user, passwd`), as well as the user-defined behaviors such as where to look for files on the server (`cwd`), which files to download (`file_reg`), and where to put downloading files (`local_root`). The arguments showed in the parenthesis are

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

## Upload
(WIP)

## Reconstruction
(WIP)

## Loading
(WIP)
