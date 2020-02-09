import jack
from queue import Queue
import fnmatch
import sys
import threading

class Connections:
    def __init__(self):
        self.output_rules = []
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

    def port_is_connected(self, port_a, port_b):
        for connected_port in self.client.get_all_connections(port_b):
            if (port_a == connected_port):
                return True

        return False

    def check_port(self, check_port):
        if check_port.is_output:
            for output_port_rule in self.output_rules:
                if fnmatch.fnmatchcase(check_port.name, output_port_rule["match"]):
                    for connection in output_port_rule["connections"]:
                        policy = connection[0]

                        if policy == "always":
                            try:
                                input_port = self.client.get_port_by_name(connection[1])

                                if not self.port_is_connected(check_port, input_port):
                                    print("Always", check_port.name, input_port.name)
                                    self.client.connect(check_port, input_port)
                                elif policy == "never":
                                    for input_port in self.client.get_all_connections(check_port):
                                        if self.port_is_connected(check_port, input_port):
                                            print("Never", check_port.name, input_port.name)
                                            self.client.disconnect(check_port, input_port)
                            except jack.JackError:
                                print("JackAudio error")

    def get_all_output_ports(self):
        return self.client.get_ports(".", True, False, False, True)

    def get_all_input_ports(self):
        return self.client.get_ports(".", True, False, True, False)

    def check_existing(self):
        for output_port in self.get_all_output_ports():
            self.check_port(output_port)

        for input_port in self.get_all_input_ports():
            self.check_port(input_port)

    def check_queue(self):
        while True:
            notification = self.notification_queue.get(True)
            notification_type = notification[0]

            if notification_type == "register":
                port = notification[1]

                print("Register", port.name)
                # FIXME gross workaround for not connecting everything together at startup
                # or when a new port is registered
                self.check_existing()
            elif notification_type == "unregister":
                port = notification[1]
                print("Unregister", port.name)
            else:
                print("Unknown", notification)

    def run(self):
        if not self.started:
            self.check_existing()
            self.client.activate()

            self.started = True

        try:
            self.check_queue()
        except KeyboardInterrupt:
            self.shutdown()

    def shutdown(self):
        self.client.deactivate()
        self.client.close()

    def add_output_rule(self, match, rule, input_port_name):
        for output_rule in self.output_rules:
            if output_rule["match"] == match:
                output_rule["connections"].append([rule, input_port_name])
                return

        self.output_rules.append({ "match": match, "connections": [ [ rule, input_port_name] ] })

    def load_file(self, config_file):
        for section in config_file.sections:

            if section["port_type"] == "output":
                for connection in section["connections"]:
                    self.add_output_rule(section["port_match"], connection[0], connection[1])
            else:
                raise RuntimeError("can not handle port type: ", section["port_type"])
