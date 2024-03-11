# -*- coding: utf-8 -*-
""" A script to check if the given .csv file is correct (can fetch the remote file wanted) """
from pathlib import Path
from typing import Union

import pandas as pd
import typer
from ftp_downloader import FTPDownloader


def main(csv_path: Union[Path, str] = typer.Argument(..., help="CSV filepath")):
    sync_info_df = pd.read_csv(csv_path)
    sync_info_df.fillna("", inplace=True)

    # downloaders: List[FTPDownloader] = list()
    for item in sync_info_df.itertuples(index=False):
        host, user, passwd, cwd, local_root, file_reg = item

        # print(host, user, passwd, cwd, local_root, file_reg)
        downloader = FTPDownloader(
            host=host,
            cwd=cwd,
            local_root=local_root,
            file_reg=file_reg,
            user=str(user),
            passwd=str(passwd),
        )
        try:
            print("===========  File list to sync: ===========")
            for file in downloader.files_to_sync():
                print(file)

            print("=========== File list to update: ===========")
            for file in downloader.files_to_update():
                print(file)
        except Exception as e:
            print("Exception happens. Exception msg: ")
            print(e)
        else:
            print("Done!")


if __name__ == "__main__":
    typer.run(main)
