# data_utils
A data utility that will include the functions such as data download & upload & reconstruction & loading, etc..

---
## Features (Working in Progress)

- [x] Download
- [ ] Upload
- [ ] Reconstruction
- [x] Loading

---
## Download

### Automatic Download CLI
We implement an automatic file download class `FTPDownloader` in the module [ftp_downloader](ftp_downloader.py). Based on the module, the script [main_download_sync.py](main_download_sync.py) provides a high-level Command Line Interface (CLI) allowing users to simply download the specific files from remote FTP server's working directory to local machine. The specific files and the corresponding FTP server's login signature are provided in an user-defined CSV file that meet certain specification.

#### Usage
> Run `python main_download_sync.py --help` for help 

Arguments:

    CSV  CSV filepath  [required]

Options:

    --log-file PATH        Output Log filepath  [default: logs/download_log.log]
    --num-workers INTEGER  Number of workders  [default: 1]

Example:

```bash
python main_download_sync.py ncep_cpc.csv 
```
will download files specified in `ncep_cpc.csv` with default 1 worker (no parallel), and the logs will be output into the default log file `logs/download_log.log`
```bash
python main_download_sync.py default.csv --num-workders 4 --log-file logs/example.log
```
will download files specified in `default.csv` with 4 workers (in parallel), and the logs will be output into the default log file `logs/example.log`

About the CSV file format or specification, the user can refer to [The CSV file specification](#csv) for more details. 


### The CSV file specification <a name="csv"></a>
The CSV file provides the necessary information to the download, which includes the FTP server address and the corresponding login signature (`host, user, passwd`), as well as the user-defined behaviors such as where to look for files on the server (`cwd`), which files to download (`file_reg`), and where to put downloading files (`local_root`). The arguments showed in the parenthesis are

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
[ftp_downloader.py](ftp_downloader.py)

***A CSV example***
A CSV file is essentially a table, the following table is a real example that download FTP files from FTP server `ftp2.psl.noaa.gov`, assume the table is stored in a CSV file `example.csv`

| host              | user | passwd | cwd                                         | local_root                     | file_reg         |
| ----------------- | ---- | ------ | ------------------------------------------- | ------------------------------ | ---------------- |
| ftp2.psl.noaa.gov |      |        | Datasets/ncep.reanalysis.dailyavgs/pressure | /DATA/CPS_Data/ncep_reanalysis | ^air\.\d{4}\.nc$ |
| ftp2.psl.noaa.gov |      |        | Datasets/ncep.reanalysis.dailyavgs/surface  | /DATA/CPS_Data/ncep_reanalysis | ^slp\.\d{4}\.nc$ |

> **_Note_**: If the ftp file address is like `ftp://url.suburl.com/...` the FTP server host should be `url.suburl.com` without an `ftp://` prefix 

The 1st row in the above table is used to download files from addresses that have a pattern `ftp://ftp2.psl.noaa.gov/Datasets/ncep.reanalysis.dailyavgs/pressure/air.{year}.nc`, where `year` is a 4 digits number such as 1979, 2020, etc. Instead the 2nd row in the table is to match the file addresses like `ftp://ftp2.psl.noaa.gov/Datasets/ncep.reanalysis.dailyavgs/surface/air.{year}.nc`. Our downloader (run `python main_sync.py example.csv`) will download all the matched files `air.{year}.nc` and `slp.{year}.nc` into the local directories `/DATA/CPS_Data/ncep_reanalysis/Datasets/ncep.reanalysis.diilyavgs/pressure` and `/DATA/CPS_Data/ncep_reanalysis/Datasets/ncep.reanalysis.diilyavgs/surface`, respectively.

In some cases, the files in `cwd` can be divided into either several different rows using different `file_reg`s, or just one row using one more general `file_reg`. In real applications, the two choices would lead to same result, but the former may be faster since the downloader uses a multiprocess mechanism to handle different downloads in different rows in parellel. However, the real situation may be complex up to your local network speed and remote connection limit. 

---
## Upload
(WIP)

---
## Reconstruction
(WIP)

---
## Loading
(WIP)
