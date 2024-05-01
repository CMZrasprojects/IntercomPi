#!/bin/sh
# script loop2jack : création et connections des liaisons AlsaLoopback <> Carte son utilisée par Jackd

# loop client creation
/usr/bin/alsa_out -j ploop -dploop -q 1 2>&1 1> /dev/null &
/usr/bin/alsa_in -j  cloop -dcloop -q 1 2>&1 1> /dev/null &

# give it some time before connecting to system ports
sleep 1

# cloop ports -> jack output ports
jack_connect cloop:capture_1 system:playback_1
jack_connect cloop:capture_2 system:playback_2


# system microphone (RME analog input 3) to "ploop" ports
jack_connect system:capture_1 ploop:playback_1
jack_connect system:capture_2 ploop:playback_2

# done
exit 0
