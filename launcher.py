import subprocess
import webbrowser
import time
import os
import sys

def main():
    try:
        if getattr(sys, 'frozen', False):
            application_path = os.path.dirname(sys.executable)
        else:
            application_path = os.path.dirname(os.path.abspath(__file__))

        exe_path = os.path.join(application_path, 'CODEL-DATA-INTEGRATION.exe')
        print(f"Attempting to run: {exe_path}")

        if not os.path.exists(exe_path):
            print(f"Error: {exe_path} does not exist.")
            input("Press Enter to close...")
            return

        server_process = subprocess.Popen([exe_path],
                                          stdout=subprocess.PIPE,
                                          stderr=subprocess.PIPE,
                                          universal_newlines=True)

        time.sleep(5)

        webbrowser.open('http://127.0.0.1:5000')

        while True:
            output = server_process.stdout.readline()
            error = server_process.stderr.readline()
            if output == '' and error == '' and server_process.poll() is not None:
                break
            if output:
                print(output.strip())
            if error:
                print(f"Error: {error.strip()}", file=sys.stderr)

    except Exception as e:
        print(f"An error occurred: {str(e)}")

    input("Press Enter to close...")

if __name__ == '__main__':
    main()