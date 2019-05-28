import socket
import threading
import time
import sys

import pickle

import numpy as np

from src.cep_definition import *
from src.cep_es_stack import *
from src.cep_FSM import *
from src.cep_utils import *

def socket_service():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # check if port is taken（socket.error: [Errno 98] Address already in use）
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(('127.0.0.1', 6666))
        s.listen(10)
    except socket.error as msg:
        print(msg)
        sys.exit(1)
    print ('Waiting connection...')

    ## read in CEP query and create CEP model
    print ('Reading Complex Event definition...')
    ce_path = 'car_disappear.txt'
    ce_def = read_ce_def(ce_path)
    combine_format, events, constraints, time_win = ce_def_parsing(ce_def)
    
    event_info, state_info, state_num = seq_info_extraction(events)
    
    # need to inject initial state 'e0' to state_info
    #  add initial state e0 to the state_info.
    state_info.insert(0, 'e0')
    state_num = state_num+1
    
    
    print("event_info: ",event_info)
    print("state_info: ",state_info)
    print("state_num: ",state_num)

    if combine_format == 'SEQ':
        pattern_detect_model = create_FSM_problog(state_info, event_info, consecutive = True)
        seq_flag = True
    elif combine_format == 'PATTERN':
        pattern_detect_model = create_FSM_problog(state_info, event_info, consecutive = False)
        seq_flag = False 

        
    print('Sequence flag: ', seq_flag)
    print('\nProbLog model: \n')
    print(pattern_detect_model)
    
    ## create event dictionary based on the order of unique events
    # the dont_care event is not in the dictionary, 
    # but it should be coded as [0 0 0 ... 1]
    event_dict = event_encoding_dict(event_info)

    
    ## create run-time event stack
    ## stact update rule is associated with stack 
    stored_e_num = 10
    event_stack = create_event_stack(state_num, stored_e_num)
    print('event_stack_shape: ',event_stack.shape)
    print(event_stack)
    
    while True:
        conn, addr = s.accept()
        t = threading.Thread(target=deal_data, 
                             args=(conn, addr, 
                                   state_num, event_dict, 
                                   pattern_detect_model,
                                   state_info, event_info))
        t.start()

        
        
def deal_data(conn, addr, 
              state_num, event_dict, 
              pattern_detect_model, 
              state_info, event_info):
    
    print ('Accept new connection from {0}'.format(addr) )
    # send welcome msg to the client side.
    conn.send('Hi, Welcome to the server!'.encode()) 
    
    # initialization:
    # create ce_buffer to store all the K events
    # the ce_buffer is updated as queue:  append(new_e), and pop(0)
    ce_buffer = [None for i in range(stored_e_num)]
    current_state = one_hot_id(state_num, 0) # initial state is zero state(final state)
    print('ce_buffer: ',ce_buffer)
    print("current_state: ",current_state)
    
    
    
    # keep listening to data from device, and perform CEP
    while True:
        data = conn.recv(1024)
        data = pickle.loads(data) # decode data
        print ('Receiving data from: {0}'.format(addr, data ) )
        print('Event_type \t Sensor_ID \t Event_time\t')
        print('%s \t\t %d \t\t %2f \n' %(data[0], data[1], data[2]))

        # encode event
        current_input = event2vec(data[0], event_dict)
        
        # update event buffer:
        ce_buffer.pop(0)
        ce_buffer.append(data)
        
        # update the event stack: move the event states left for 1 timestep
        # keep the first init event states
        update_stack(event_stack,seq_flag = seq_flag)

        current_states = event_stack[:, -2]

        event_stack[:, -1] = states_update(pattern_detect_model, 
                                           state_info, event_info,
                                           current_states, current_input,
                                           seq_flag = seq_flag,
                                           overlap_flag = True)
        # the overlapping flag is controlled in the state_update process
        # overlap_flag = True by default
        
        print('\nThe updated event states stack: ')
        print(event_stack)
        
        # if CE detected :
        if event_stack[-1, -1] != 0:
            print("Finding the satisfied sequences...")
            ce_candidate_idx = sequence_search(event_stack)
            # print the path and index of events
            print(ce_candidate_idx)
            print(ce_buffer)
            for path_i in ce_candidate_idx:
                for path_i_idx_i in path_i:
                    print(ce_buffer[int(path_i_idx_i-1)])
                    
        ######################### add selector model here ####################
        
        
        
        
        
                    
        
#         # -- Adding Complex Event Processing module.
#         # store the received events into a buffer.
#         # implement CEP detection use CEP engine.
#         current_input = event2vec(data[0], event_dict)

#         ################################### done!
#         next_state, ce_flag = FSM_core(pattern_detect_model, state_info, event_info, 
#                                        current_state, current_input,
#                                        diagnose = 0)
        
#         ################################### done
#         # saving current event to CE buffer:
#         current_state = next_state
        
#         # store the event as order. (e_1 in state 1, position 1)
#         ce_buffer[(current_state.argmax()-1)%state_num] = [data[0], data[1], data[2]]
        
        
        
#         # If pattern match, check other constraints:
#         if ce_flag ==1:
#             print("========Complex Event detected!========")
#             CE_name = 'car_disappear.txt'
#             print("=======  Event:"+CE_name.split('.')[0]+"  =========")
#             print("=======================================")
#             ce_buffer_np = np.array(ce_buffer)
#             event_time = ce_buffer_np[:,2].astype(float)
#             print("=======Time: ", event_time, ' =======\n')

################################### add selector model here
#         # If pattern match, check other constraints:
#         if ce_flag ==1:
#             ce_buffer_np = np.array(ce_buffer)
#             event_time = ce_buffer_np[:,2].astype(float)
#             event_value = ce_buffer_np[:,1].astype(int)
            
#             ce_event_flag = Selector(event_time, event_value, diagnose = 0)
# #             print(ce_flag, ce_event_flag)
#             if ce_event_flag == 1:
#                 print("========Complex Event detected!========")
#                 print("============== Event: ABC =============")
#                 print("Time: %2f, %2f, %2f." 
#                       %(event_time[0], event_time[1], event_time[2]))
#                 print("Subject ID: %d" %event_value[0])
#                 print("=======================================\n")
                
                
                

    # closing connection.
        #time.sleep(1)
        if data == 'exit' or not data:
            print ('{0} connection close'.format(addr) )
            conn.send('Connection closed!'.encode())
            break

    conn.close()


if __name__ == '__main__':
    socket_service()

    
    
    
from cep import *
ce_path = 'car_disappear.txt'
ce_def = read_ce_def(ce_path)
ce_def_parsing(ce_def)
