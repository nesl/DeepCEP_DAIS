import numpy as np
import pyparsing as pp

from problog.program import PrologString
from problog import get_evaluatable



    
# generate transition
def problog_transition_generator(state_t, input_t, state_info, event_info, consecutive = True, prob_t = 1):
    # state_info contains the K states + 1 initial state
    
    transition = 'prob_t::n_state(state_next):- t_state(state_t), t_in(input_t).'
    
    transition = transition.replace('state_t',str(state_t))
    transition = transition.replace('input_t',str(input_t))

    transition = transition.replace('prob_t',str(prob_t))
    
    # initialize forward-flag. State push forward only when it's true
    forward_flag = False
    
    ## finding the next state based on rules:
    
    # if the input is dont_care:
    if (not(input_t in event_info)):
        forward_flag = False
    # if the input is important event:
    else:
        state_idx = state_info.index(state_t)   # take care of repetitive events
        if event_info[state_idx] == input_t:
#         if state_idx==event_idx:
            forward_flag = True
   
    # update the next state
    if forward_flag:
        # for both seq or pattern, push forward
        state_next = state_info[state_idx+1]      
    else:
        # whether it's sequence or pattern
        if consecutive:
            state_next = state_info[0]
        else:
            state_next = state_t

    transition = transition.replace('state_next',str(state_next))
    
    return transition

# # generate output definition
# def problog_fsm_output_generator(state_info, event_info, prob_t = 1):
#     fsm_output = '''1::n_out(1):- n_state(init_state), t_state(last_state), t_in(last_input).
# 1::n_out(0):- n_state(init_state), \+(t_state(last_state), t_in(last_input)).
# '''
    
#     fsm_output = fsm_output.replace('init_state',str(state_info[-1]))
#     fsm_output = fsm_output.replace('last_state',str(state_info[-2]))
#     fsm_output = fsm_output.replace('last_input',str(event_info[-1]))
    
#     for i in range(len(state_info)-1):
#         state_i = state_info[i]
#         fsm_output = fsm_output + '1::n_out(0):- n_state(state_i).\n'.replace('state_i', str(state_i) )

#     return fsm_output


# creating FSM model in ProbLog code
def create_FSM_problog(state_info, event_info, org_uniq_event, consecutive = True):
    
    problog_model = """"""
    uniq_event = sorted(set(event_info), key=event_info.index) # create a sorted unique event list for the events in the desired sequence only

    # writing states predicate ############################################################
    # in total K+1 states(number of events + initial state)
    states_predicate = ''
    
    for idx, state_i in enumerate(state_info):
        states_predicate = states_predicate + 'p_s_'+state_i+'_' + '::' + 't_state('+state_i+')'
        if idx != len(state_info)-1:
            states_predicate = states_predicate+'; '
        else:
            states_predicate = states_predicate+'.\n'
#     print(states_predicate)


    # writing events predicate ############################################################
    # in total E+1 events predicates (E is unique Event number, 1 is dont_care)
    events_predicate = ''

    for idx, event_i in enumerate(org_uniq_event):
        events_predicate = events_predicate + 'p_e_'+event_i+'_' + '::' + 't_in('+event_i+')'
        if idx != len(org_uniq_event)-1:
            events_predicate = events_predicate+'; '
        else:
            events_predicate = events_predicate+'; '
            events_predicate = events_predicate + 'p_e_dont_care_' + '::' + 't_in(dont_care).\n'
#     print(events_predicate)


    # writing transition ############################################################
    fsm_transition = ''

    for state_i in state_info[0:-1]: # e_final is the termination state, no transition needed.
        for event_i in uniq_event:
            trans_i = problog_transition_generator(state_i, event_i, state_info, event_info, consecutive ,prob_t = 1)
            fsm_transition = fsm_transition + trans_i+'\n'
            
        # adding event of dont'care
        trans_i = problog_transition_generator(state_i, 'dont_care', state_info, event_info, consecutive , prob_t = 1)
        fsm_transition = fsm_transition + trans_i+'\n'
        
        fsm_transition = fsm_transition +'\n'
#     print(fsm_transition)

    
    # don't need to have other output, the only output is next state.
#     # writing output definition ############################################################
#     fsm_output = ''
#     fsm_output = fsm_output + problog_fsm_output_generator(state_info, event_info, prob_t = 1)
#     # print(fsm_output)


    # writing queries for next states and output #############################################
    all_query = ''
    all_query = all_query+ 'query(n_state(_)).\n'
    # print(all_query)

    problog_model = (states_predicate + '\n' 
                    + events_predicate + '\n' 
                    +fsm_transition 
                    +all_query)

#     print(problog_model)
    
    return problog_model


def FSM_core(pattern_detect_model, state_info, org_uniq_event, 
             current_state, current_input, 
             diagnose = 0):
    
#     org_uniq_event = set(event_info)
    
    # definition of FSM model
    problog_model = pattern_detect_model
    
    # naive way of assign prob
    for idx, state_i in enumerate(state_info):
        problog_model= problog_model.replace(('p_s_'+str(state_i)+'_'), 
                                             str(current_state[idx] ) )
    for idx, event_i in enumerate(org_uniq_event):
        problog_model= problog_model.replace(('p_e_'+str(event_i)+'_'), 
                                             str(current_input[idx]) )
    # change prob for dont_care
    problog_model= problog_model.replace(('p_e_dont_care_'), str(current_input[-1]) )
    
#     print(problog_model)
    

    
    result = get_evaluatable().create_from(PrologString(problog_model)).evaluate()
    
    # naive way of getting ProbLog inference result
    py_result={}
    for i in result:
        py_result[str(i)] = result[i]

    next_state = np.array([py_result['n_state('+str(state_i)+')'] for state_i in state_info])
    
    if diagnose:
#         print(problog_model, '\n')
        print('============= Diagnose Mode =================')
#         print(result, '\n')
        print('Current state: \t',current_state, state_info,
              '\nInput: \t', current_input, uniq_event)
        # print the reuslt:
        print('Next state: \t',next_state)
        print('\n')
    return next_state