import multiprocessing
import subprocess
import argparse
import time
import os
from pyvirtualdisplay import Display

def get_keyword(site):
    return site.split('://')[-1].split('/')[0]

def check_and_kill_chrome():
    # Check if any Chrome processes are running
    process_list = os.popen('ps aux').read()
    chrome_processes = [line for line in process_list.splitlines() if 'chrome' in line]
    
    if chrome_processes:
        print("Chrome processes found. Waiting for 10 seconds...")
        time.sleep(10)
        
        # Kill all Chrome processes
        os.system('pkill -f brave-browser-nightly')
        print("Killed all Chrome processes.")
    else:
        print("No Chrome processes found.")

def worker(args):
    """Function to execute a.py with given arguments and capture output"""
    arg1, arg2, arg3, arg4, arg5, arg6 = args
    
    try:
        # Execute the script with arguments
        result = subprocess.run(
            ['npm', 'run', 'crawl', '--', str(arg1), str(arg2), str(arg3), str(arg4), str(arg5), str(arg6)],
            capture_output=True,
            text=True,
            check=True
        )
        
        # Capture stdout and stderr
        stdout = result.stdout
        stderr = result.stderr
        
        return (stdout, stderr)
    except subprocess.CalledProcessError as e:
        return (e.stdout, e.stderr)
    except Exception as e:
        return (e.stdout, e.stderr)

def main(extn, url):
    # Arguments to pass to the script a.py
    # URL = 'https://www.geeksforgeeks.org/deletion-in-linked-list/'
    arguments = [(f'-o=./data/{extn}/{get_keyword(url)}/', f'-u={url}', f'-b=/usr/bin/brave-browser-nightly', f'-t=20', f'--extensions-path={extn}', '--screenshot') for i in range(5)]
    
    try:
        # Create a pool of worker processes
        with multiprocessing.Pool(processes=5) as pool:
            # Map the worker function to the arguments
            results = pool.map(worker, arguments)
        # subprocess.run([(f'-o={extn}/{get_keyword(url)}', f'-u={url}', f'-b=/usr/bin/brave-browser-nightly', f'-t=10', f'--extensions-path={extn}', '--screenshot'])
        # Print the results
        # print('results: ', url, results)
        for i, (stdout, stderr) in enumerate(results):
            print(f'Result from worker {i}:')
            print('stdout:', stdout)
            print('stderr:', stderr)
    except Exception as e:
        print(e)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run crawlers in parallel')
    parser.add_argument('--url', type=str, default=None)
    args = parser.parse_args()

    xvfb_args = [
        '-maxclients', '2048'
    ]
    vdisplay = Display(backend='xvfb', size=(1920, 1280), extra_args=xvfb_args)
    vdisplay.start()
    display = vdisplay.display
    os.environ['DISPLAY'] = f':{display}'

    extns = ['control', 'ublock']
    # extns = ['control']
    jobs = []

    for extn in extns:
        subprocess.call(['mkdir', '-p', f'data/{extn}/{get_keyword(args.url)}'])

        p = multiprocessing.Process(target=main, args=(extn, args.url))
        jobs.append(p)
    for job in jobs:
        job.start()

    TIMEOUT = 180
    start = time.time()
    for job in jobs:
        print(f"joining {job}")
        job.join(timeout = 60)

        while time.time() - start <= TIMEOUT:
            if job.is_alive():
                time.sleep(5)
            else:
                break
            
        if job.is_alive():
            print('timeout exceeded... terminating job')
            job.terminate()
        

    # check_and_kill_chrome()

    vdisplay.stop()
    print('exiting this code peacefully!')