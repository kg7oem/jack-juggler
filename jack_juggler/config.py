import re

class ConfigFile:

    def __init__(self, path):
        self.path = path
        self.current_line = 0

        self.sections = []

    def parse(self):
        with open(self.path) as file:
            current_section = None

            for line in file:
                self.current_line += 1
                line = line.rstrip()

                if re.search("^\s*#", line):
                    print("skipping comment:", line)
                    continue

                if re.search("^\s*$", line):
                    print("skipping only whitespace")
                    continue

                if not re.search("^\s+", line):
                    current_section = self.parse_section(line)
                    self.sections.append(current_section)
                else:
                    if not current_section:
                        self.raise_parse_error("no current section defined at")

                    current_section["connections"].append(self.parse_rule(line))

        self.current_line = 0

    def raise_parse_error(self, message):
        raise RuntimeError(message, self.path, self.current_line)

    def parse_section(self, line):
        parts = line.split()

        if len(parts) != 2:
            self.raise_parse_error("Expected two parts for section line")

        return { "port_type": parts[0], "port_match": parts[1], "connections": [] }

    def parse_rule(self, line):
        parts = line.split()

        if len(parts) != 2:
            self.raise_parse_error("Expected 2 parts for rule line")

        return parts
