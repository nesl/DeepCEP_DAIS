import numpy as np

from src.cep_utils import *
from src.cep_FSM import *

def create_event_stack(states_num, events_num):
    """
    create event states stack for storing the states info of nearest K events
    """
    es_stack = np.zeros((states_num , events_num +1)) # add 1 for initial state
    es_stack[0,:] = 1
    return es_stack



def update_stack(event_stack, seq_flag = False):
    """
    updating event states stack:
    1. slide the stack for 1 timestep
    2. update the stack by following the rules:
        if Pattern: 1,2,3 or 0
        if Sequence: 1(only s_0),2 or 0
            if overlapping: 
            if non-overlapping: equal or less than one 1 in each states set
    
    After udpate, the last column is invalid.(need refill from new event)
    """
    states_num, events_num = event_stack.shape
    
    # moving stack:
    for i in range(1, events_num-1):
        event_stack[:,i] = event_stack[:,i+1] 
    
    # updating stack: 
    # if it's Pattern 
    if not seq_flag:
        for i in range(1, events_num-1):
            for j in range(1, states_num):

                if event_stack[j,i] == 1:
                    if event_stack[j,i-1]==0:
                        event_stack[j,i] = 0

                elif event_stack[j,i] == 2:
                    if event_stack[j-1,i-1]==0:
                        event_stack[j,i] = 0

                elif event_stack[j,i] == 3:
                    if (event_stack[j-1,i-1]==0) and (event_stack[j,i-1]==0):
                        event_stack[j,i] = 0
                    elif (event_stack[j-1,i-1]==0) and (event_stack[j,i-1]!=0):
                        event_stack[j,i] = 1
                    elif (event_stack[j-1,i-1]!=0) and (event_stack[j,i-1]==0):
                        event_stack[j,i] = 2
    else:
        # if it's Sequence
        for i in range(1, events_num-1):
            for j in range(1, states_num):

                if event_stack[j,i] == 2:
                    if event_stack[j-1,i-1]==0:
                        event_stack[j,i] = 0
    
    return event_stack



def states_update(pattern_detect_model, state_info, org_uniq_event, 
                  current_states, current_event, 
                  seq_flag = False, overlap_flag = True):
    """
    use defined fsm_model to propagate the states set
    state_num: is a global variable defined in main program
    
    state update rule is different for sequence and pattern:
    
    For pattern: For n-th entry in next states, look at n and n-1 th entry in current states.  (0, 1, 2, 3)
    For sequence:  (only 0, 1, 2. -- actually only 2 is possible. No 3!)
        If overlapping: same as pattern, but n-th state is always 0.
        If non-overlapping: 
    
    """
    state_num = len(state_info)
    
    
    new_states = np.zeros_like(current_states)
    
    # if pattern: state inherit; If sequence: dont inherit
    if not seq_flag:
        new_states[current_states != 0] = 1
        new_states[-1] = 0  # final states keeps empty
    else:
        # keep the first initial state active(1)
        new_states[0] = 1
    
#     print(new_states)
    for i in range(state_num-1):
    # dont need to calculate the 'next state' of final state.
        
# #         print(new_states)
        #     encode state to one-hot
        if current_states[i]!=0:
            current_state =  one_hot_id(state_num, i)  # convert state index into one-hot
            
            next_state = FSM_core(pattern_detect_model, state_info, org_uniq_event, 
                               current_state, current_event,
                               diagnose = 0)
#             print(current_state, current_event, next_state)

            # dependency check
            n_state_idx = next_state.argmax()
            # if state doesn't push forward, do nothing; else:
#             print(current_state,next_state )
            if (current_state != next_state).any():
                if (current_states[n_state_idx]!=0) and (current_states[n_state_idx-1]!=0):
                    new_states[n_state_idx] = 3
                elif (current_states[n_state_idx]!=0) and (current_states[n_state_idx-1]==0):
                    new_states[n_state_idx] = 1
                elif (current_states[n_state_idx]==0) and (current_states[n_state_idx-1]!=0):
                    new_states[n_state_idx] = 2
                else:
                    raise ValueError('??? with FSM: ',
                                     current_states,
                                     current_event,
                                     new_state)
#         print(new_states)

    # keep the first initial state active(1)
    new_states[0] = 1
    
    # for sequence, replace all 3 into 2.
    if seq_flag:
        new_states[new_states == 3] = 2
        
    # for non-overlapping case:
    # if the final state is reached,
    # abandon all the other activated states
    if overlap_flag == False:
        if new_states[-1] !=0:
            for i in range(1, state_num-1):
                new_states[i] = 0

    print("Current_states: ", current_states, 
          "\nCurrent_event: ", current_event, 
          "\nNew_states: ", new_states)
    
    return new_states



def sequence_search(event_stack):
    """
    find all the sequences satisfying the given pattern/sequence
    Input: event_state_stack
    Output: a m x n numpy array, where m is the number of unique paths, n is the state_num
    In the ouput matrix, index of path point is stored.
    """
    
    # initialize
    state_num, stack_size = event_stack.shape
    
    sequence_path = np.zeros([1, (state_num-1)])
    # the length is state_num-1, initial state is not included
    pointer_save = np.zeros([1,2])
    
    pointer = np.array([state_num-1, stack_size-1]) #(states, events)
    pointer_save[0,:] = pointer
    
#     define path finding function for path_i
    def find_path(sequence_path, path_idx, pointer_save):
        
        sequence_path_i = sequence_path[path_idx,:].reshape((1,(state_num-1)))
        pointer = pointer_save[path_idx,:]
        
        down_counter = 0

        # while the inital state is not reached, move the pointer    
        while pointer[0]>0:
            value = event_stack[int(pointer[0]), int(pointer[1]) ]

            if value == 1:
                pointer[1] = pointer[1]-1
            elif value == 2:
                sequence_path_i[0,int(pointer[0]-1)] = pointer[1]
                pointer = pointer-1
            elif value ==3:
                if down_counter == 0:
                    sequence_path_i[0,int(pointer[0]-1)] = pointer[1]
                    pointer = pointer-1
                else:
                    sequence_path = np.concatenate([sequence_path, sequence_path_i]) 
                    saved_point = pointer
                    pointer_save = np.concatenate([pointer_save, saved_point.reshape((1,2))])     
                    pointer[1] = pointer[1]-1
            else:
                raise ValueError('??? with path-finding: ',es_test_new, pointer)  
            
            down_counter = down_counter+1
                
            sequence_path[path_idx,:] = sequence_path_i
            
        return sequence_path, pointer_save
        
    # first do one scan when the truning_point list is empty
    path_idx = 0
    sequence_path, pointer_save = find_path(sequence_path, path_idx, pointer_save)
    
    # then if the path_id is not pointing to the last path, continue find path
    while ((sequence_path.shape[0]-1)!= path_idx):
        path_idx = path_idx+1
        seq_path_i = sequence_path[path_idx,:]
        pointer = np.array([np.where(seq_path_i!=0)[0][0]+1, 
                            sequence_path[path_idx, np.where(seq_path_i!=0)[0][0]]])
        sequence_path, pointer_save = find_path(sequence_path, path_idx, pointer_save)
        
    # return the event_index+1 for all sequence path.
    return sequence_path



def check_pattern_without(ce_buffer, path_i, without_info):
    ce_flag = True
    if without_info == None:
        return ce_flag
    
    without_event, without_location = without_info
    idx = int(path_i[without_location[0]]-1)
    idy = int(path_i[without_location[1]])
    for i in range( idx, idy ):
        if ce_buffer[i][0] == without_event:
            ce_flag = False
            print('Not satisfied: ', path_i)
            break
    
    return ce_flag