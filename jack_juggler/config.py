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
        result = re.match("^([^\s]+)\s+(.*)", line)

        if not result:
            self.raise_parse_error("Invalid section line")

        return { "port_type": result.group(1), "port_match": result.group(2), "connections": [] }

    def parse_rule(self, line):
        result = re.match("^\s+([^\s]+)\s+(.*)", line)

        if not result:
            self.raise_parse_error("Invalid policy line")

        return [ result.group(1), result.group(2) ]
