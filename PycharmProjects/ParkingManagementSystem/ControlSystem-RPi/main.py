import requests
import logging
import traceback
import sys
import os
from accessControlSystem import AccessControlSystem

def run_control_system(acs):
    while True:
        print('waiting for bluetooth signal')
        RXData = acs.bluetoothSerial.read().decode('utf-8').strip()
        if '1' in RXData:
            print("signal received, taking a photo")
            acs.take_photo()
            while True:
                try:
                    print('sending photo to plate recognizer')
                    response = acs.recognize_plate()
                    response_dict = response.json()

                    if len(response_dict['results']) > 0: # a car detected
                        candidates = [entry['plate'] for entry in response_dict['results'][0]['candidates']]
                        print(candidates)
                        # if any candidate plate number in the data base, open the gate
                        for licence in candidates:
                            if acs.enquiry(licence):
                                acs.gate_controller.signal_received()
                                print('gate open')
                                break # no need to check the rest of the candidates
                    else:
                        print('no car detected')
                    break
                except requests.Timeout as e:
                    print('Time out')
                    logging.error(str(e))
                    continue

                except requests.ConnectionError as e:
                    print('Connection error')
                    logging.error(str(e))
                    continue

if __name__ == '__main__':
    try:
        acs = AccessControlSystem()
        run_control_system(acs)
    except KeyboardInterrupt:
        print('Interrupt')
        acs.clean() # make sure clean up the pins, close the database, camera and close the gate
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
    except Exception:
        print('Access control system quit unexpectedly')
        logging.error(traceback.format_exc())
        acs.clean()  # make sure clean up the pins, close the database, camera and close the gate
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)