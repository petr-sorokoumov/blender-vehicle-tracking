import math

# discrete Fourier transform
def dft(x, inverse = False) :
    N = len(x)
    inv = -1 if not inverse else 1
    twiddles = [math.e**(inv*2j*math.pi*k/N) for k in range(N)]
    X =[0] * N
    for k in range(N) :
        for n in range(N) :
            X[k] += x[n] * twiddles[n * k % N]
        if inverse :
            X[k] /= N
    return X

# get from signal [[time,value]] only frequences from start_freq to end_freq
# !!! Now works only if grabbing period is constant
def afc_crop(signal, lower_frq, higher_frq):
    signal_length = len(signal)
    if signal_length < 2:
        return signal
    # check if lower_freq <= higher_freq
    if lower_frq > higher_frq:
        tmfrq = lower_frq
        lower_frq = higher_frq
        higher_frq = tmfrq
    # get only function values from signal
    raw_signal = [dat[1] for dat in signal]
    total_signal_time = signal[-1][0] - signal[0][0]
    # highest frequency after ft
    highest_frq_ft = signal_length/total_signal_time
    # lowest frequency after ft
    lowest_frq_ft = 1/total_signal_time
    # position of start measure to get for answer (lowest freq)
    start_frq_index = ceil(lower_frq * total_signal_time - 1)
    # position of end measure to get for answer (highest freq)
    end_frq_index = ceil(higher_frq * total_signal_time - 1)
    #
    print("Frequencies in signal are from ", lowest_frq_ft, " to ", highest_frq_ft)
    print("Target frequencies are from ", lower_frq, "(", start_frq_index,") to ", higher_frq, " (", end_frq_index,")")
    #
    # frequencies are out of fft filtering abilities --- return zeros
    if end_frq_index < 0 or start_frq_index > signal_length:
        print("Fourier filtering result is zero signal")
        return [[dat[0],0] for dat in signal]
    #
    if end_frq_index > signal_length:
        end_frq_index = signal_length
    if start_frq_index < 0:
        start_frq_index = 0
    #
    # direct Fourier transform
    dir_res = dft(raw_signal)
    # reset values not in interval
    for i in range(0,start_frq_index):
        dir_res[i]=0
    for i in range(end_frq_index,signal_length):
        dir_res[i]=0
    results = dft(dir_res, inverse=True)
    return [[signal[i][0], results[i].real] for i in range (signal_length)]
    
# moving average filter
def sm_avg(signal,filter_size):
    if len(signal)<filter_size:
        return signal[:]
    curr_sum = sum([elem[1] for elem in signal[:filter_size]])
    res = [[signal[0][0],curr_sum/filter_size]]
    for curr in range(1,len(signal)-filter_size):
        curr_sum = curr_sum - signal[curr][1] + signal[curr+filter_size][1]
        res.append([signal[curr][0],curr_sum/filter_size])
    return res

# set lower and upper borders for signal
def chop_signal(signal, lower_b, higher_b):
    res = []
    for val in signal:
        curr = val[:]
        if val[1]<lower_b:
            curr[1] = lower_b
        if val[1]>higher_b:
            curr[1] = higher_b
        res.append(curr)
    return res

# set lower and upper borders for signal
def supress_low_values(signal, average_value, noise_level):
    res = []
    for val in signal:
        curr = val[:]
        if val[1]<(average_value + noise_level) and val[1]>(average_value - noise_level):
            curr[1] = average_value
        res.append(curr)
    return res


# set given average for signal
def set_average(signal, window, given_avg):
    res = []
    d =ceil(len(signal)/window)
    current_window_size = window
    for i in range(d):
        window_sum = sum([m[1] for m in signal[i*window:(i+1)*window]])
        if i == d-1:
            current_window_size = len(signal)%window
        window_avg = window_sum/current_window_size - given_avg
        for val in signal[i*window:(i+1)*window]:
            res.append([val[0],val[1]-window_avg])                   
    return res
