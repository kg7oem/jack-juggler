import jack
import re
import sys
import threading

class Connections:
    def __init__(self):
        self.always_rules = {}

        self.started = False
        self.done_event = threading.Event()

        self.client = jack.Client("jack-juggler", True)
        self.client.set_port_registration_callback(self.jack_port_registration_callback)
        self.client.set_port_connect_callback(self.jack_port_connect_callback)
        self.client.set_shutdown_callback(self.jack_shutdown_callback)

    def jack_shutdown_callback(self, status, reason):
        print('JACK shutdown; status: ' + status, "; reason " + reason)
        self.done_event.set()

    def jack_port_registration_callback(self, port, registered):
        if registered:
            print("Register", port.name)
        else:
            print("Unregister", port.name)

        if not registered or not port.is_output:
            return

        for output_port_rule in self.always_rules.keys():
            if re.search(output_port_rule, port.name):
                for input_port_name in self.always_rules[output_port_rule]:
                    print("Always", port.name, input_port_name)

                    try:
                        self.client.connect(port, input_port_name)
                    except jack.JackError:
                        print("Could not connect", port.name, input_port_name)

    def jack_port_connect_callback(self, output, input, connected):
        if connected:
            print("Connect", output, input)
        else:
            print("Disconnect", output, input)

        # not monitoring ports that need to be disconnected
        if connected:
            return

        if output.name not in self.always_rules:
            return

        always_list = self.always_rules[output.name]

        for rule in always_list:
            if re.search(rule, output.name):
                print("Always", output.name, input.name)
                self.client.connect(output, input)

    def start(self):
        assert(self.started == False)

        self.client.activate()

    def run(self):
        if not self.started:
            self.start()
            self.started = True

        try:
            self.done_event.wait()
        except KeyboardInterrupt:
            self.shutdown()

    def shutdown(self):
        sys.exit(0)

    def add_always(self, match, input_port_list):
        if match not in self.always_rules:
            self.always_rules[match] = []

        always_list = self.always_rules[match]

        for input_port in input_port_list:
            always_list.append(input_port)
