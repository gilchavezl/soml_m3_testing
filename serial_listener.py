import serial, string
import time
from datetime import datetime


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
except Exception as e:
    print(f'Could not create or open file.\nError reported:\n{e}')
    exit(0)


def get_cat(data):
    try:
        split_list = data.split()
        print(split_list)
        token = split_list[0]
        print(token)
        start = token[:3]
        print(start)
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
        print(f'CAT:\t{category}')
        print(f'SUBCAT:\t{sub_category}')
        print(f'TIC:\t{tic}')
        print(f'DATA:\t{data_dump}')
        output = [category, sub_category, tic, data_dump]
    except Exception as e:
        print(f'Could not parse data.\nError reported:\n{e}')
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
        print(f'Could not log data to file.\nError reported:\n')



def main():
    output = 'x'
    for port in ports:
        try:
            ser = serial.Serial(port, baudrate, bytesize, parity, stopbits, timeout)
            print(f'Success opening port {port}')
            break
        except Exception as e:
            print(f'Could not open port {port}')
    run = True
    try:    
        while run:
            print(f'Start reading port')
            while output != '':
                output = ser.readline()
                timestamp = time.time()
                # if( len(output) > 0 ):
                #     get_cat(output)
                if( output != b'\r\n' ):
                    # print(output)
                    data_str = output[:-2].decode("utf-8")
                    # print(output[:-2].decode("utf-8"))
                    print(data_str)
                    # print('.')
                    data_to_log = get_cat(data_str)
                    if data_to_log is not None:
                        log_to_csv(timestamp, data_to_log)
            output = ""
    except KeyboardInterrupt:
        print("Execution stopped by user. Stopping...")
        run = False


if __name__ == "__main__":
    main()