# nao-audio-video-recorder
Simple GUI for recording audio and video using Nao's cameras, microphones and sensors.

Sensor data is recorded on the local computer, to sensor_readings/...

Audio and video is recorded on the robot, into /home/nao/recordings


## system load
The load of the recorder is observable through naoqi-bin process:
* idle: %CPU 23, %MEM 25.8
* recording: %CPU 86, %MEM 26
* recording and streaming video through choregraphe:  %CPU 96, %MEM 26.2
* streaming video through choregraphe:  %CPU 35, %MEM 26.1

