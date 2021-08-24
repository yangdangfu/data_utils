# -*- coding: utf-8 -*-
import typer
from pathlib import Path
import os
from typing import List
import pandas as pd
from ftp_downloader import FTPDownloader
import multiprocessing as mp
import sys
import schedule
import time
import logging
from logging import handlers


def sync(sync_info: pd.DataFrame, num_workers: int):
    logging.info("Scheduled sync start...")

    downloaders: List[FTPDownloader] = list()
    for item in sync_info.itertuples(index=False):
        host, user, passwd, cwd, local_root, file_reg = item

        # print(host, user, passwd, cwd, local_root, file_reg)

        downloaders.append(
            FTPDownloader(
                host=host,
                cwd=cwd,
                local_root=local_root,
                file_reg=file_reg,
                user=str(user),
                passwd=str(passwd),
            ))

    # for downloader in downloaders:
    #     try:
    #         downloader.run()
    #     except KeyboardInterrupt:
    #         break  # stop the download if the `ctrl+c` is pressed
    #     except:
    #         print(f"Something wrong!")
    pool = mp.Pool(num_workers)
    pools = [pool.apply_async(downloader.run) for downloader in downloaders]
    pool.close()
    for p in pools:
        p.get()

    logging.info("Scheduled sync complete.")


def main(csv: Path = typer.Argument(..., help="CSV filepath"),
         log_file: Path = typer.Option("logs/download_log.log",
                                       help="Output Log filepath"),
         num_workers: int = typer.Option(1, help="Number of workders")):
    """Start the downloader with given CSV file and other options 

    run `python main_download_sync.py --help` for help 

    Arguments:
        CSV  CSV filepath  [required]

    Options:
        --log-file PATH        Output Log filepath  [default: logs/download_log.log]
        --num-workers INTEGER  Number of workders  [default: 1]
    
    Example: 
        python main_download_sync.py ncep_cpc.csv 
            will download files specified in ncep_cpc.csv with default 1 worker (no parallel), and the logs will be output into the default log file logs/download_log.log

        python main_download_sync.py default.csv --num-workders 4 --log-file logs/example.log
            will download files specified in ncep_cpc.csv with 4 workers (in parallel), and the logs will be output into the default log file logs/example.log
    """
    # ANCHOR Configuration for logger
    handler_list = list()
    stream_handler = logging.StreamHandler()
    handler_list.append(stream_handler)
    if log_file is not None:
        log_dir = os.path.dirname(log_file)
        if log_dir != "":
            os.makedirs(log_dir, exist_ok=True)
        file_handler = handlers.RotatingFileHandler(filename=log_file,
                                                    maxBytes=20480,
                                                    backupCount=5)
        handler_list.append(file_handler)
    logging.basicConfig(
        handlers=handler_list,
        format="%(asctime)s %(message)s",
        level=logging.INFO,
    )

    # ANCHOR handle command line arguments
    assert os.path.exists(csv), f"CSV file {csv} doesn't exist."

    logging.info(f"Sync files specified in {csv}")

    # ANCHOR load informations and set schedule
    sync_info_df = pd.read_csv(csv)
    sync_info_df.fillna("", inplace=True)
    # logging.info(f"File information: \n {sync_info_df}")
    schedule.every().day.at("00:00").do(sync,
                                        sync_info=sync_info_df,
                                        num_workers=num_workers)
    # schedule.every().minute.do(sync,
    #                            sync_info=sync_info_df,
    #                            num_workers=num_workers)  # FOR DEBUG

    while True:
        try:
            schedule.run_pending()
            time.sleep(3600)
        except KeyboardInterrupt:
            logging.exception("ctrl-c is pressed.")
            sys.exit()  # stop the program if the `ctrl+c` is pressed
        except:
            logging.exception("Something wrong!")


if __name__ == "__main__":
    typer.run(main)
