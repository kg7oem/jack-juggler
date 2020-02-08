import jack
from queue import Queue
import re
import sys
import threading

class Connections:
    def __init__(self):
        self.always_rules = {}
        self.started = False
        self.notification_queue = Queue()

        self.client = jack.Client("jack-juggler", True)
        self.client.set_port_registration_callback(self.jack_port_registration_callback)
        self.client.set_shutdown_callback(self.jack_shutdown_callback)

    def jack_shutdown_callback(self, status, reason):
        print('JACK shutdown; status: ' + status, "; reason " + reason)
        self.shutdown()

    def jack_port_registration_callback(self, port, registered):
        if registered:
            self.notification_queue.put([ "register", port ])
        else:
            self.notification_queue.put([ "unregister", port ])

    def check_output_port(self, port):
        for output_port_rule in self.always_rules.keys():
            if re.search(output_port_rule, port.name):
                for input_port_name in self.always_rules[output_port_rule]:
                    print("Always", port.name, input_port_name)

                    try:
                        self.client.connect(port, input_port_name)
                    except jack.JackError:
                        print("Could not connect jack ports", port.name, input_port_name)

    def check_queue(self):
        while True:
            notification = self.notification_queue.get(True)
            notification_type = notification[0]

            if notification_type == "register":
                port = notification[1]

                print("Register", port.name)
                self.check_output_port(port)
            elif notification_type == "unregister":
                port = notification[1]
                print("Unregister", port.name)
            else:
                print("Unknown", notification)

    def run(self):
        if not self.started:
            self.client.activate()
            self.started = True

        try:
            self.check_queue()
        except KeyboardInterrupt:
            self.shutdown()

    def shutdown(self):
        self.client.deactivate()
        self.client.close()

    def add_always(self, match, input_port_name):
        if match not in self.always_rules:
            self.always_rules[match] = []

        always_list = self.always_rules[match]
        always_list.append(input_port_name)
