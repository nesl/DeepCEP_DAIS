import numpy as np
import pyparsing as pp

from problog.program import PrologString
from problog import get_evaluatable


# creating ANY model in ProbLog code
def create_ANY_problog(org_uniq_event):
    
    prob = 1
    
    problog_model = """"""

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
    ce_definition = ''
    
    for event_i in org_uniq_event:
        
        def_i = 'prob_t::complex_event :-t_in(event_i).'
        def_i = def_i.replace('event_i', str(event_i))
        def_i = def_i.replace('prob_t', str(prob))
        ce_definition = ce_definition + def_i+'\n'
        
    ce_definition = ce_definition +'\n'
#     print(fsm_transition)

    # writing queries for next states and output #############################################
    all_query = ''
    all_query = all_query+ 'query(complex_event).\n'
    # print(all_query)

    problog_model = (events_predicate + '\n' 
                    +ce_definition 
                    +all_query)

#     print(problog_model)
    
    return problog_model


def ANY_core(pattern_detect_model, org_uniq_event, current_input, 
             diagnose = 0):
    
#     org_uniq_event = set(event_info)
    
    # definition of FSM model
    problog_model = pattern_detect_model
    
    # naive way of assign prob
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
    
    CE_prob = py_result['complex_event']
    
    if diagnose:
#         print(problog_model, '\n')
        print('============= Diagnose Mode =================')
#         print(result, '\n')
        print('Unique events: \t',org_uniq_event,
              '\nInput: \t', current_input)
        # print the reuslt:
        print('CE probability: \t',CE_prob)
        print('\n')
    return CE_prob