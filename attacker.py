import socket, time, statistics, string
import matplotlib.pyplot as plt  # For Trial Sweep
SOCK_PATH = "/tmp/passwordchecker.sock"

"""TODO: This is the max amount if recommended trials.
In your lab report, talk about what will happen
if the trial count goes lower? What do you see?"""
TRIALS = 120

"""TODO: Fill in the alphabet"""
ALPHABET = string.ascii_letters + string.digits + string.punctuation


def measure(candid):
    """TODO"""
    def trimmed_mean_10(data):  # Helper function for removing outliers for more stable time measurements
        data = sorted(data)
        count = int(0.05*len(data))
        data = data[count:(len(data)-count)]
        
        return statistics.mean(data)
    

    round_trip = []

    for i in range(TRIALS):
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as a:
            a.connect(SOCK_PATH)

            begin = time.perf_counter_ns()
            a.sendall(candid)
            rec = a.recv(1)
            end = time.perf_counter_ns()

            diff = end - begin
            round_trip.append(diff)

    avg = trimmed_mean_10(round_trip)
    return avg


def recover(max_len=7):
    """TODO"""
    password = b""

    print(f"Password Recovery ({TRIALS} trials) is starting...")

    for i in range(max_len):
        time_count = 0

        for j in ALPHABET:
            candid = password + j.encode()
            rt_time = measure(candid)

            if rt_time > time_count:
                g_letter = j
                time_count = rt_time

        password += g_letter.encode()
        print(f"Recovery Progress (up to {i+1} character(s)): {password.decode()}")
    
    print(f"Finished Recovery! Password is {password.decode()}\n")

    return password


def plot(trial, rec_pass, real_pass):  # For Trial Sweep / Plot Success Rate vs. Number of Trials

    success_list = []

    for i in rec_pass:
        count = 0

        for j in range(len(i)):
            if i[j] == real_pass[j]:
                count += 1
        
        success_rate = (count/len(real_pass))*100
        success_list.append(success_rate)
    
    plt.figure(figsize=(8,5))
    plt.bar(trial, success_list)
    plt.xlabel("Amount of Trials")
    plt.ylabel("Success Rate (%)")
    plt.title("Password Recovery: Success Rate vs. Amount of Trials")
    plt.ylim(0, 110)
    plt.xticks(trial)
    plt.show()
    
        
if __name__=="__main__":
    run_more_trials = False  # For Trial Sweep / True for a multiple-trial run (with plots), False for a fixed 120-trial run

    if run_more_trials == True:  # Trial Sweep / Run multiple number of trials, and plot them
        pass_list = [] 
        trial_list = [30, 60, 90, 120]
        real_password = "S3cret!"

        for i in trial_list:
            TRIALS = i
            rec_pass = recover()
            pass_list.append(rec_pass.decode())
        
        plot(trial_list, pass_list, real_password)  # Plotting
        
    else:  # Normal recovery
        recover()
