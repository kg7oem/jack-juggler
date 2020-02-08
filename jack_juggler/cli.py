from jack_juggler.connections import Connections

def main():
    connections = Connections()

    connections.add_always("^rig-play:out_0$", "system:playback_1")

    connections.run()

if __name__ == "__main__":
    main()
