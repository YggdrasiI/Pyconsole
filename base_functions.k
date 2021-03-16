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

# Name = like name in Midi Port Enabler, i.e 'in 1'
function enable_input(name){
	if( Machine == "linux" || Machine == "unix" ){
		inports = midi("input", "list")
		t = "input"
		bfound = 0
		for( p in inports ){
			if( inports[p] == name ){
				bfound = 1
				if ( midi(t,"isopen",p) ){
					print("MIDI "+t+" "+string(p)+" was already open.")
				}else{
					print("Open MIDI "+t+" "+string(p)+"")
					midi(t,"open",p)
				}
				break;
			}
		}
		if( bfound == 0){
			print("Input name not found. Available are:")
			print(inports)
		}
	}else{
		print("Function had no effect on "+Machine)
	}
}

function test_rec()
{
	RUN_TEST = 1
	# Merge = 0  # Do not propagate midi input to midi output
	print("Loop started")
	while (RUN_TEST) {
		bNewData = 0
		for( note in Recorded ){
			time_offset = note.time
			bNewData = 1
			break; # Abort after first note. I just need the earliest. 
		}
		if( bNewData ){
			ph = Recorded
			Recorded = ''  # Clears recording

			# TODO: Made a distinction if this should be a NOTEON or NOTEOFF ...
			if( 1 ){
				# ph.time -= time_offset
				ph.time = 0
				ph.type = NOTEOFF
				print(ph)
				realtime(ph, Now)
				realtime('do4v120', Now)  # Just for debugging...
			}
		}
		sleeptill(Now+1)
	}
	print("Loop quited")
}
