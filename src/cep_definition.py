import numpy as np
import pyparsing as pp

from src.cep_utils import *

def read_ce_def(ce_path):
    with open(ce_path, 'r') as f:
        x = f.readlines()
    ce_def=''
    for i in x:
        ce_def = ce_def+i
    return ce_def


def ce_def_parsing(ce_def):
    colon = ':'
    lb = pp.Literal('{')
    rb = pp.Literal('}')
    ###################################################
    # "!" is optional, used for pattern_without operation only
    event_element = pp.Combine(pp.Optional('!')
                            +pp.Word(pp.alphanums+'_')
                            +':'
                            +pp.Word(pp.alphanums+'_') )

    EventList = pp.OneOrMore( event_element )



    combination_format = (pp.Word('PATTERN'+'SEQ'+'ANY'+'PATTERN_WT') 
                      + colon 
                      + lb 
                      + pp.Group(EventList) 
                      + rb)

    ###################################################
    constraint_element = (pp.Word(pp.alphanums+'.')
                            +pp.Word('>'+'<'+'='+'>='+'<=')
                            +pp.Word(pp.alphanums+'.') )

    ConstraintList = pp.OneOrMore( constraint_element )


    constraint = (pp.Word('Constraints') 
                      + colon 
                      + lb 
                      + pp.Group(ConstraintList) 
                      + rb)

    ###################################################
    time = ( pp.Word('TIME') + colon + pp.Word(pp.nums) )

    # cep_query = combination_format + constraint + time
    cep_query =  combination_format + constraint + time

    ce_parse = cep_query.parseString(ce_def)
#     print( ce_parse )

    combine_format, events, constraints,time = ce_parse[0], ce_parse[3], ce_parse[8], ce_parse[12]

    print('\n==========Parsing result:==========')
    print('Combine Format: ',combine_format)
    print('Events: ',events)
    print('Constraints: ',constraints)
    print('Time: ',time)
    print('====================================\n')
    
    return combine_format, events, constraints, time


def seq_info_extraction(events):
    sequence_info = events
#     print(sequence_info)

    event_info = [i.split(':')[1].replace(' ', '') for i in sequence_info]
#     print(event_info)
    state_info = [i.split(':')[0].replace(' ', '') for i in sequence_info]
#     print(state_info)

    ## create event dictionary before filtering out the without'ed event
    # create event dictionary based on the order of unique events
    # the dont_care event is not in the dictionary, but it should be coded as [0 0 0 ... 1]
    # the pattern_without'ed event should be in the dictionary.
    uniq_event = sorted(set(event_info), key=event_info.index) # create a sorted unique event list
    event_dict = event_encoding_dict(uniq_event)
    
    # handle the operation for "PATTERN_Without"
    without_info = None # initial the return result
    pattern_without_flag = False
    for idx, event in enumerate(state_info):
        if '!'in event:
            pattern_without_flag = True
            without_idx = idx
            without_position = [idx-1, idx]
            print('No event ', event_info[without_idx],' at position: ',without_position)
        
    if pattern_without_flag == True:
        state_info.pop(without_idx)
        without_event = event_info.pop(without_idx)
        without_info = [without_event, without_position]
    #     print(event_info)
    #     print(state_info)
#         print("without_position is: ", without_position)
#         print("without_event is: ", without_event)

    state_num = event_number = len(state_info)
    
#     print('state_num: ',state_num)
    
    return event_info, state_info, state_num, uniq_event, event_dict, pattern_without_flag, without_info
