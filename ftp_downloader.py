# -*- coding: utf-8 -*-
""" A module for FTPDownloader class implementation and test"""
import logging
import os
import re
import shutil
import timeit
from ftplib import FTP
from typing import List


class FTPDownloader:
    """A class to sync the local folder from the remote FTP directory. A regular expression can be used only to sync the files that the filename matches the given pattern.

    Note the syncer only support downloading files from remote to local
    """

    def __init__(
        self,
        host: str,
        cwd: str,
        local_root: str,
        file_reg: str = ".+",
        user: str = "",
        passwd: str = "",
    ):
        """Initialize the `FTPDownloader` class

        Args:
            host (str): FTP server address, such as "ftp2.psl.noaa.gov". Note the address has no prefix "ftp://"
            cwd (str): the remote directory, such as "Datasets/cpc_global_precip", use / to connect the path
            local_root (str): the local root directory that remote FTP files will download to, make sure the path is valid, the directory will be created if it does not exist
            file_reg (str, optional): A regular expression to match the files that is going to sync. Defaults to ".+", means to sync all files in the remote to local.
            user (str, optional): username to connect the FTP server, Defaults to ""
            passwd (str, optional): password to connect the FTP server, Defaults to ""
        """
        self.host = host
        self.user = user
        self.passwd = passwd
        self.cwd = cwd
        self.file_reg = file_reg
        self.local_root = local_root

    def files_to_sync(
        self,
    ) -> List[str]:
        """Return the files that match the given pattern and are going to sync. The function can be used to check if the provided class initialization arguments meet the requirements that sync the right files

        Returns:
            List[str]: matched_files The list of files that are going to sync
        """
        matched_files = []
        with FTP(host=self.host) as ftp:
            ftp.login(user=self.user, passwd=self.passwd)
            ftp.cwd(self.cwd)
            files = ftp.nlst()
            for file in files:
                match = re.fullmatch(self.file_reg, file)  # match
                if match:
                    matched_files.append(file)
        return matched_files

    def files_to_update(self, sync_mode: str = "auto") -> List[str]:
        """Return the files that match the given pattern and are going to download. Compared to the `file_to_sync` function, this function also do the size check to return only the files that have different size between remote and local

        Args:
            sync_mode (str): See `sync_mode` argument in function `run`

        Returns:
            List[str]: matched_files The list of files that are going to download
        """
        matched_files = list()
        assert sync_mode in [
            "auto",
            "override",
            "no_override",
        ], f"The input argument must be one of 'auto', 'override' and 'no_override'."

        with FTP(self.host) as ftp:
            ftp.login(user=self.user, passwd=self.passwd)
            ftp.cwd(self.cwd)
            files = ftp.nlst()  # list the files on remote server

            for file in files:
                match = re.fullmatch(self.file_reg, file)  # match
                if match:  # if filename match the given regular expression
                    filepath = os.path.join(self.local_root, file)
                    if os.path.exists(filepath):  # file exists
                        if sync_mode == "no_override":
                            continue
                        if sync_mode == "auto":
                            if os.stat(filepath).st_size == ftp.size(file):  # check if the file size is equal
                                continue
                    matched_files.append(file)
        return matched_files

    def run(self, sync_mode: str = "auto") -> None:
        """
        Start to sync files that match given regular pattern in the remote FTP directory ioto the local folder

        Use "ctrl-c" to stop the running syncer

        Args:
            sync_mode (str, optional): Sync mode can be "auto", "override", "no_override". Defaults to "auto".
            - if it is "auto", the syncer will automatically check the file sizes on both remote and local, download and override the local file only if they are different.
            - if it is "override", the syncer will override the local file without file size check.
            - if it is "no_override", the syncer will never override the exsiting file.
        """
        assert sync_mode in [
            "auto",
            "override",
            "no_override",
        ], f"The input argument must be one of 'auto', 'override' and 'no_override'."
        os.makedirs(self.local_root, exist_ok=True)  # create local directory if it is not exists

        ftp = FTP(self.host)
        ftp.login(user=self.user, passwd=self.passwd)
        ftp.cwd(self.cwd)
        files = ftp.nlst()  # list the files on remote server

        for file in files:
            match = re.fullmatch(self.file_reg, file)  # match
            if match:  # if filename match the given regular expression
                filepath = os.path.join(self.local_root, file)
                filepath_cache = os.path.join(self.local_root, file + ".1")
                if os.path.exists(filepath):  # file exists
                    if sync_mode == "no_override":
                        logging.info(f"{filepath} already exists and won't be update in `no_override` mode.")
                        continue
                    if (sync_mode == "auto") and (os.stat(filepath).st_size == ftp.size(file)):
                        # the mode is 'auto' and the file size is equal, no need to update
                        # logging.info(f"{filepath} already up to date.")
                        continue
                logging.info(f"Downloading file {file} to {filepath} ...")
                try:
                    start = timeit.default_timer()
                    ftp.retrbinary("RETR " + file, open(filepath_cache, "wb").write)
                    if os.path.exists(filepath):
                        os.remove(filepath)
                    shutil.move(src=filepath_cache, dst=filepath)
                    stop = timeit.default_timer()
                    logging.info(f"Time used {stop - start:.0f}s for downloading file {file}")
                except Exception as e:
                    # re-login
                    ftp.close()
                    ftp = FTP(self.host)
                    ftp.login(user=self.user, passwd=self.passwd)
                    ftp.cwd(self.cwd)
                    logging.info(f"Exception happens when download {file} to {filepath}\n {e}")
                    logging.info(f"Time used {stop - start:.0f}s for downloading file {filepath_cache}")


if __name__ == "__main__":
    _server = "ftp2.psl.noaa.gov"  # server
    _cwd = "Datasets/cpc_global_precip"  # current working directory
    _file_reg = "^precip\.\d{4}\.nc$"
    _local = "/DATA/CPS_Data/ncep_reanalysis"
    cpc_precip_syncer = FTPDownloader(host=_server, cwd=_cwd, file_reg=_file_reg, local_root=_local)

    _cwd = "Datasets/cpc_global_temp"  # current working directory
    _file_reg = "^tmax\.\d{4}\.nc$"

    cpc_tmax_syncer = FTPDownloader(host=_server, cwd=_cwd, file_reg=".+", local_root=_local, user="", passwd="")

    # matched files
    print(cpc_precip_syncer.files_to_sync())
    print(cpc_tmax_syncer.files_to_sync())
    # uncomment the following lines two sync
    # cpc_precip_syncer.run()
    # cpc_tmax_syncer.run()
