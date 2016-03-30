#define elif else if

# Setup a ALSA connection
# Adapt connect_alsa.sh on your environment if ness.
function enable_output(){

	if( Machine == "linux" || Machine == "unix" ){
		outalsa = outport(1)
		mapport(0,outalsa)
		system("${GRID_MUSIC_ROOT}/scripts/connect_alsa.sh")
	}
}
