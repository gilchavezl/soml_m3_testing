"""
@brief CCHM serial debug interface simple logger script
@author Gilberto Chavez
@date 2024/06/20

Test script to log serial debug messages from the CCHM.

This script opens a serial port and reads data coming through it, logs to a csv file under ./log folder.
"""


import serial, os, logging
import time
from datetime import datetime


# logging config
logging.basicConfig(
    level=logging.INFO,
    format="{asctime} {levelname:<8} {message}",
    style='{'
)
# Logging levels:
# CRITICAL  50
# ERROR		40
# WARNING	30
# INFO      20
# DEBUG		10
# NOTSET	0


# port = '/dev/ttyACM0'
# port = 'COM4'
ports = ['COM4','/dev/ttyACM0','/dev/ttyACM1']
baudrate = 115200
bytesize = 8
parity = 'N'
stopbits = 1
timeout = 10


try:
    dt = datetime.now()
    log_file = dt.strftime("./log/serial_log_%Y%m%d%H%M.csv")
    headers = 'time,category,subcategory,tic,data\n'

    file = open(log_file, "w")  # write mode
    file.write(headers)
    file.close()
    logging.info(f'Success creating log file with filename <{log_file}>')
except Exception as e:
    logging.critical(f'Could not create or open file.\nError reported:\n{e}')
    exit(0)


def get_cat(data):
    try:
        split_list = data.split()
        logging.debug(split_list)
        token = split_list[0]
        logging.debug(token)
        start = token[:3]
        logging.debug(start)
        category = ''
        sub_category = ''
        tic = ''
        data_dump = ''
        if( start == 'NTP' ):
            # this is a CCHM DEBUG MSG with NTP update data
            category = 'NTP DEBUG MSG'
            sub_category = 'NTP'
            tic = 'NA'
            data_dump = data
        elif( start == 'TIC' ):
            # this is a TIC DEBUG MSG
            category = 'TIC DEBUG MSG'
            tic = token
            if( split_list[1] == 'RX:'):
                sub_category = 'READ'
                # this is a message with TIC data
                sub_split = data.split(': ')
                data_dump = sub_split[1]
            else:
                sub_category = 'OTHER'
                data_dump = data
        elif( start == '171'):
            # this is a CCHM DEBUG MSG for publishing
            category = 'CCHM DEBUG MSG'
            sub_category = 'PUB'
            tic = 'NA'
            data_dump = data
        else:
            # unknown category
            category = 'UNKNOWN'
            sub_category = 'UNKNOWN'
            tic = 'NA'
            data_dump = data
        logging.debug(f'CAT:\t{category}')
        logging.debug(f'SUBCAT:\t{sub_category}')
        logging.debug(f'TIC:\t{tic}')
        logging.debug(f'DATA:\t{data_dump}')
        output = [category, sub_category, tic, data_dump]
    except Exception as e:
        logging.error(f'Could not parse data.\nError reported:\n{e}')
        output = None
    return output


def log_to_csv(timestamp, data):
    """ append text to a file """
    try:
        new_row = f'{timestamp:.2f},{data[0]},{data[1]},{data[2]},{data[3]}\n'
        fileid = open(log_file, "a")  # append mode
        fileid.write(new_row)
        fileid.close()
    except Exception as e:
        logging.error(f'Could not log data to file.\nError reported:\n')


def main():
    output = 'x'
    no_port = True
    for port in ports:
        try:
            ser = serial.Serial(port, baudrate, bytesize, parity, stopbits, timeout)
            logging.info(f'Success opening port {port}')
            no_port = False
            break
        except Exception as e:
            logging.warning(f'Could not open port {port}')
    if(no_port):
        logging.critical(f'No devices found on ports listed, exiting.')
        exit(0)
    run = True
    try:    
        while run:
            logging.info(f'Start reading port')
            while output != '':
                output = ser.readline()
                timestamp = time.time()
                # if( len(output) > 0 ):
                #     get_cat(output)
                if( output != b'\r\n' ):
                    data_str = output[:-2].decode("utf-8")
                    logging.debug(data_str)
                    data_to_log = get_cat(data_str)
                    if data_to_log is not None:
                        log_to_csv(timestamp, data_to_log)
            output = ""
    except KeyboardInterrupt:
        logging.info("Execution stopped by user. Stopping...")
        run = False


if __name__ == "__main__":
    main()