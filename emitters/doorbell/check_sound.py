import simpleaudio

# set sound variable
sound = simpleaudio.WaveObject.from_wave_file('/home/pi/sounds/mixkit-home-standard-ding-dong-109.wav')

play_obj = sound.play()
play_obj.wait_done()