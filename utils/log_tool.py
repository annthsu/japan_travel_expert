"""To Log

Log use method.
"""

import os
import sys
from typing import Optional, Union

from loguru import logger
from loguru._logger import Logger as LoguruLogger

logger.remove()


class Log(object):
    """
    A class to Log

    Attributes
    ----------
    log_path : str
        Save path of log file

    Methods
    -------
    ```
    setup_logger(name: str, log_file: str, level: Optional[Union[str, int]] = LOG_CONFIG.get('level'))
        設定你需要的記錄器
    ```
    """

    LOG_CONFIG = {
        "level": 'INFO'
    }

    def __init__(self, log_path: str) -> None:
        """
        Parameters
        ----------
        log_path : str
            Save path of log file
        """
        self.log_path = log_path

    def setup_logger(self,
                     name: str,
                     log_file: str,
                     level: Optional[Union[str, int]] = LOG_CONFIG.get('level')) -> LoguruLogger:
        """To setup as many loggers as you want

        Parameters
        ----------
        name : str
            logger名稱，同樣名稱的logger會把log資料記錄在一起
        log_file : str
            日誌檔案名稱，例如：example.log
        level : str or int, optional
            日誌紀錄的最低等級 (預設是INFO)

        Returns
        -------
        logger
            設定完成的記錄器

        Examples
        --------
        >>> Log().setup_logger('example', 'example.log', level='INFO')
        <loguru.logger handlers=[(id=1, level=10, sink=<stdout>),
                                 (id=2, level=20, sink='/home/rdadmin/crawler/log/example.log')]>
        """
        logger.add(
            sys.stdout,
            filter=lambda record: record.get('extra').get('name') == name
        )
        logger.add(
            os.path.join(self.log_path, log_file),
            level=level,
            filter=lambda record: record.get('extra').get('name') == name
        )

        return logger.bind(name=name)
