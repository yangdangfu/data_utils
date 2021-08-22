# -*- coding: utf-8 -*-
import os
from typing import List
import pandas as pd
from ftp_downloader import FTPDownloader
import multiprocessing as mp
import datetime
import schedule
import time


def sync(sync_info_csv: str):
    sync_info = pd.read_csv(sync_info_csv)
    sync_info.fillna("", inplace=True)

    downloaders: List[FTPDownloader] = list()
    for item in sync_info.itertuples(index=False):
        host, user, passwd, cwd, local_root, file_reg = item

        print(host, user, passwd, cwd, local_root, file_reg)

        downloaders.append(
            FTPDownloader(host=host,
                          cwd=cwd,
                          local_root=local_root,
                          file_reg=file_reg,
                          user=str(user),
                          passwd=str(passwd)))

    # for downloader in downloaders:
    #     try:
    #         downloader.run()
    #     except KeyboardInterrupt:
    #         break  # stop the download if the `ctrl+c` is pressed
    #     except:
    #         print(f"Something wrong!")
    pool = mp.Pool(4)
    pools = [pool.apply_async(downloader.run) for downloader in downloaders]
    pool.close()
    for p in pools:
        try:
            p.get()
        except KeyboardInterrupt:
            break  # stop the download if the `ctrl+c` is pressed
        except:
            print(f"Something wrong!")


if __name__ == "__main__":
    import sys
    argv = sys.argv

    # Determine CSV file that the sync info come from
    csv = "default.csv"
    if len(argv) == 2:
        csv = argv[1]
    elif len(argv) != 1:
        assert os.path.exists(
            csv), f"Invalid input command line arguments {argv[1:]}."
    assert os.path.exists(csv), f"CSV file {csv} doesn't exist."

    # run the sync() for 1 time ahead
    sync(sync_info_csv=csv)
    # Try to run at 01:30 every day
    # schedule.every().day.at("01:30:00").do(sync, sync_info_csv=csv)
    # schedule.every().day.at("01:30:00").do(sync, sync_info_csv=csv)
    schedule.every().hour.do(sync, sync_info_csv=csv)

    while True:
        schedule.run_pending()
        time.sleep(10)