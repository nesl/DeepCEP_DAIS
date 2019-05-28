import numpy as np

# function: convert index to one-hot encoding
def one_hot_id(dimension, idx):
    encoding = np.zeros(dimension)
    encoding[idx] =1
    return encoding

# creating event encoding dictionary
def event_encoding_dict(uniq_event):
#     uniq_event = sorted(set(event_info), key=event_info.index) # create a sorted unique event list
    uniq_event_num = len(uniq_event)
#     print('uniq_event_num: ',uniq_event_num)

    event_dict = {}

    for idx, event in enumerate(uniq_event):
        event_dict[event] = one_hot_id(uniq_event_num+1, idx)

    return event_dict


# define event to vec function for all incoming events
def event2vec(event_type, event_dict):
    if event_type in event_dict.keys():
        vec_event = event_dict[event_type]
    else:
        vec_event = one_hot_id(len(event_dict)+1, -1)
    return np.array(vec_event)