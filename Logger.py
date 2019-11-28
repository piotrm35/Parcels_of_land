"""
/***************************************************************************
  Logger.py

  An Logger for road_inspection_viewer QGIS plugin.
  --------------------------------------
  version : 0.1.3
  Date : 21-01-2018
  Copyright: (C) 2018 by Piotr Michałowski
  Email: piotrm35@hotmail.com
/***************************************************************************
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License version 2 as published
 * by the Free Software Foundation.
 *
 ***************************************************************************/
"""

import logging, os
from logging.handlers import RotatingFileHandler


class Logger:

    def __init__(self, path_to_log_file, max_bytes, backup_count, logger_name):
        log_format = logging.Formatter('%(asctime)s - %(levelname)s -> %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        my_handler = RotatingFileHandler(filename=path_to_log_file, maxBytes=max_bytes, backupCount=backup_count)
        my_handler.setFormatter(log_format)
        self.app_log = logging.getLogger(logger_name)
        self.app_log.addHandler(my_handler)
        self.app_log.setLevel(logging.INFO)
        self.app_log.info("------------------------------------------------------------------------------------------------------------------")
        self.app_log.info("Logger(" + logger_name + ").__init__ - OK.")

    def write_INFO_log(self, text):
        self.app_log.info(text)

    def write_WARNING_log(self, text):
        self.app_log.warning(text)

    def write_ERROR_log(self, text):
        self.app_log.error(text)

    def write_CRITICAL_log(self, text):
        self.app_log.critical(text)

#==================================================================================================================

def test():
    logger = Logger("test.log", 4*1024, 2, "test_log")
    for i in range(20):
        logger.write_INFO_log('write_INFO_log, i = ' + str(i))
        logger.write_WARNING_log('write_WARNING_log, i = ' + str(i))
        logger.write_ERROR_log('write_ERROR_log, i = ' + str(i))
        logger.write_CRITICAL_log('write_CRITICAL_log, i = ' + str(i))
    del logger

def merge_log_files(path_to_log_file_1, path_to_log_file_2, path_to_result_log_file, n_tabs):
    log_file_1 = open(path_to_log_file_1, 'r')
    raw_file_1_data_list = log_file_1.read().split('\n')
    log_file_1.close()
    log_file_2 = open(path_to_log_file_2, 'r')
    raw_file_2_data_list = log_file_2.read().split('\n')
    log_file_2.close()
    
    log_file_1_data_list = []
    log_file_1_data_time_stamp_float_list = []
    log_file_2_data_list = []
    log_file_2_data_time_stamp_float_list = []
    for line in raw_file_1_data_list:
        try:
            data_line = line.split(' -> ')[1].strip()
            time_stamp_str = data_line.split(' ')[0].strip()
            time_stamp_float = float(time_stamp_str)
            log_file_1_data_time_stamp_float_list.append(time_stamp_float)
            log_file_1_data_list.append(data_line)
        except:
            pass
    for line in raw_file_2_data_list:
        try:
            data_line = line.split(' -> ')[1].strip()
            time_stamp_str = data_line.split(' ')[0].strip()
            time_stamp_float = float(time_stamp_str)
            log_file_2_data_time_stamp_float_list.append(time_stamp_float)
            log_file_2_data_list.append(data_line)
        except:
            pass
    
    result_log_file = open(path_to_result_log_file, 'w')
    result_log_file.write(os.path.basename(path_to_log_file_1) + '\n')
    result_log_file.write(n_tabs * '\t' + os.path.basename(path_to_log_file_2) + '\n')
    result_log_file.write('\n')
    log_file_2_data_idx = 0
    log_file_2_data_max_idx = len(log_file_2_data_list) - 1
    last_time_stamp_float = None
    for log_file_1_data_idx in range(len(log_file_1_data_list)):
        while True:
            if log_file_2_data_idx <= log_file_2_data_max_idx:
                if log_file_1_data_time_stamp_float_list[log_file_1_data_idx] < log_file_2_data_time_stamp_float_list[log_file_2_data_idx]:
                    last_period_str = _get_last_period_str(log_file_1_data_time_stamp_float_list[log_file_1_data_idx], last_time_stamp_float)
                    last_time_stamp_float = log_file_1_data_time_stamp_float_list[log_file_1_data_idx]
                    result_log_file.write(last_period_str + log_file_1_data_list[log_file_1_data_idx] + '\n')
                    break
                else:
                    last_period_str = _get_last_period_str(log_file_2_data_time_stamp_float_list[log_file_2_data_idx], last_time_stamp_float)
                    last_time_stamp_float = log_file_2_data_time_stamp_float_list[log_file_2_data_idx]
                    result_log_file.write(n_tabs * '\t' + last_period_str + log_file_2_data_list[log_file_2_data_idx] + '\n')
                    log_file_2_data_idx += 1
            else:
                last_period_str = _get_last_period_str(log_file_1_data_time_stamp_float_list[log_file_1_data_idx], last_time_stamp_float)
                last_time_stamp_float = log_file_1_data_time_stamp_float_list[log_file_1_data_idx]
                result_log_file.write(last_period_str + log_file_1_data_list[log_file_1_data_idx] + '\n')
                break
    while True:
        if log_file_2_data_idx <= log_file_2_data_max_idx:
            last_period_str = _get_last_period_str(log_file_2_data_time_stamp_float_list[log_file_2_data_idx], last_time_stamp_float)
            last_time_stamp_float = log_file_2_data_time_stamp_float_list[log_file_2_data_idx]
            result_log_file.write(n_tabs * '\t' + last_period_str + log_file_2_data_list[log_file_2_data_idx] + '\n')
            log_file_2_data_idx += 1
        else:
            break
    result_log_file.close()

def _get_last_period_str(current_time_stamp_float, last_time_stamp_float):
    if last_time_stamp_float is not None:
        return ' [ ' + str(current_time_stamp_float - last_time_stamp_float) + ' ] '
    else:
        return ' [ START ] '

#------------------------------------------------------------------------------------------------------------------

if __name__ == "__main__":
    pass
    #test()
    #merge_log_files(os.path.join('log', 'road_inspection_viewer.log'), os.path.join('log', 'images_preload_thread.log'), os.path.join('log', 'result.log'), 4)
    
    
