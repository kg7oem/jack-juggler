import sys

from jack_juggler.config import ConfigFile
from jack_juggler.connections import Connections

def main():
    config_file = ConfigFile(sys.argv[1])
    config_file.parse()

    connections = Connections()
    connections.load_file(config_file)

    connections.run()

if __name__ == "__main__":
    main()
