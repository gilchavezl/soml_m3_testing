import numpy as np

ENDIANESS = 'MSB'           # either 'MSB' or 'LSB'
ADC_GAIN = [32, 32, 32, 32, 32, 32, 1, 1, 4, 32] # ADC sets gain to 32 for CH0-5, 1 for Analog and Digital Monitor, 4 for temp
ADC_VREF = 2500 # mV


def split_tic_data(res_list):
    """
    Takes a list containing the 40 byte response from the TIC and splits
    the data into sets of 4 bytes, where each set is a list within a list.
    """
    list_len = len(res_list)
    sets_num = int(list_len / 4)
    list_split = []
    index_start = 0
    for sets in range(sets_num):
        chunk = res_list[index_start:index_start+4]
        index_start +=4
        list_split.append(chunk)
    return list_split


def bytes_to_int(list_bin):
    """
    Merge 3 8-bit ints into a single 24-bit int.
    ENDIANESS  is defined as a constant in the file header.
    Input expected in the form of:
    If ENDIANESS is set to 'MSB':
        list_bin[0] -> MSB;
        list_bin[1] -> ...;
        list_bin[2] -> LSB;
    If ENDIANESS is set to 'LSB':
        list_bin[0] -> LSB;
        list_bin[1] -> ...;
        list_bin[2] -> MSB;
    """
    # if (list_bin[0] & 0x80 ):
    #     sign_byte = 0xFF000000
    # else:
    #     sign_byte = 0x00000000
    if ENDIANESS == 'MSB':
        upper_byte = list_bin[0] << 16
        middle_byte = list_bin[1] << 8
        lower_byte = list_bin[2] << 0
    if ENDIANESS == 'LSB':
        upper_byte = list_bin[2] << 16
        middle_byte = list_bin[1] << 8
        lower_byte = list_bin[0] << 0
    return ( upper_byte | middle_byte | lower_byte )
    

def twos_comp(val, bits):
    """
    Compute the two's complement of int value val, bits should be set to the 
    expected output's size (24).
    """
    if (val & (1 << (bits - 1))) != 0: # if sign bit is set e.g., 8bit: 128-255
        val = val - (1 << bits)        # compute negative value
    return val                         # return positive value as is


def get_adc_code(input_list):
    """
    Takes a list of lists containing the TIC output with the raw values split 
    into sets of 4 8-bit ints.
    Returns a list of the processed values obtained by merging the 3 data bytes 
    on each TIC channel.
    """
    list_int24 = []
    for list_channel in input_list:
        # merged_int24 = bytes_to_int(list_channel[:-1])
        merged_int24 = bytes_to_int(list_channel[1:])
        int_value = twos_comp(merged_int24, 24 )
        list_int24.append(int_value)
    return list_int24


def convert_to_volts(raw_adc_counts):
    """
    Get mV (or Volts by setting ADC_VREF to 2.5 instead of 2500) from the ADC 
    raw code (counts) value.
    From the ADS124S08 datasheet Section 9.5.2 pg.64:
        LSBsize = ( 2 * Vref / Gain ) / 2^24
    Vin = ADCcounts * LSBsize
    """
    adc_voltages = []
    for index, adc_counts in enumerate(raw_adc_counts):
        lsb_size = (( 2 * ADC_VREF ) / ADC_GAIN[index]) / (2**24)
        voltage = adc_counts * lsb_size
        # ADC_GAIN is set to 1 for ADC voltage monitors, but result is VALUE/4,
        # will do value*4 to get actual voltage value
        if(ADC_GAIN[index] == 1):
            voltage = voltage * 4
        adc_voltages.append(voltage)
    return adc_voltages


def hex_str_to_mv_str(hex_string):
    # print(f'Data received:\n{hex_string}')
    as_list_hex = hex_string.split()
    # print(f'Data as list:\n{as_list_hex}')
    int_list = [ int(x,16) for x in as_list_hex ]
    # print(f'Data as list of ints:\n{int_list}')
    data_split = split_tic_data(int_list)
    # print(f'Data splitted:\n{data_split}')
    values_int24 = get_adc_code(data_split)
    # print(f'Data as int24:\n{values_int24}')
    voltages = convert_to_volts(values_int24)
    # print(f'Data as voltages:\n{voltages}')
    voltages_r = list(np.round(voltages,4))
    # print(f'Data as voltages rounded:\n{voltages_r}')
    output_string = ' '.join(str(v) for v in voltages_r)
    # print(f'as string:\t{output_string}')
    return output_string
    

def main():    
    print(f'Main Function Call (should not happen when using as util)')


if __name__ == "__main__":
    main()