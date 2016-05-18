from naoqi import ALProxy
import time
import Tkinter as tk
import tkFont


class MainWindow(tk.Frame):
    ''' Main Window '''

    def __init__(self, master):
        self.master = master

        # initialize tk frame
        tk.Frame.__init__(self, master)
        
        # initialize variables
        self.isRecordingVideo = False
        self.isRecordingAudio = False
        self.isRecordingSonar = False
        self.isRecordingTactile = False
        self.recordTactile = tk.IntVar()
        self.recordSonar = tk.IntVar()
        self.isConnected = False
        self.ip = tk.StringVar(value='leclerc.local')
        self.port = tk.IntVar(value=9559)
        self.video_label = tk.StringVar()
        self.additional_label = ""
        self.camera_dict = {0: 'Top', 1: 'Bottom'}
        self.audio_dict = {0: '.wav', 1:'.ogg'}
        self.audio_id = 0
        self.time_start = 0

        # create GUI
        self.initializeGUI()

        # create naoqi proxies
        self.videoRecorderProxy = []
        self.audioRecorderProxy = []
        self.sonarProxy = []
        self.memoryProxy = []


    def initializeGUI(self):
        ''' Initializes GUI'''
        
        self.master.title('NAO audio video recorder')
        self.pack(fill=tk.BOTH, expand=True)

        # frame for robot network configuration
        frame_robot_config = tk.Frame(self)
        frame_robot_config.pack(fill=tk.X)
        tk.Button(frame_robot_config, text="Connect", command=self.connect).pack(side=tk.RIGHT, padx=5, pady=5)
        input_font = tkFont.Font(family="Arial",size=10)
        port = tk.Entry(frame_robot_config, width=6, font=input_font, textvariable=self.port)
        port.pack(side=tk.RIGHT, padx=5, pady=5)
        tk.Label(frame_robot_config, text="PORT").pack(side=tk.RIGHT, padx=5, pady=5)
        ip = tk.Entry(frame_robot_config, width=16, font=input_font, textvariable=self.ip)
        ip.pack(side=tk.RIGHT, padx=5, pady=5)
        tk.Label(frame_robot_config, text="IP").pack(side=tk.RIGHT, padx=5, pady=5)

        # frame for camera and audio format selection
        frame_camera_config = tk.Frame(self)
        frame_camera_config.pack(fill=tk.X)
        self.camera_label = tk.Label(frame_camera_config, text="Top", width = 8)
        self.camera_label.pack(side=tk.RIGHT, padx=5, pady=5)
        tk.Button(frame_camera_config, text="Switch camera", command=self.switchCamera).pack(side=tk.RIGHT, padx=5, pady=5)
        self.audio_label = tk.Label(frame_camera_config, text = ".wav")
        self.audio_label.pack(side=tk.RIGHT, padx=5, pady=5)
        tk.Button(frame_camera_config, text="Switch audio", command=self.switchAudio).pack(side=tk.RIGHT, padx=5, pady=5)       
        
        # additional video label selection
        frame_video_label = tk.Frame(self)
        frame_video_label.pack(fill=tk.X)
        tk.Button(frame_video_label, text='Clear', command=self.clear_label, width = 10).pack(side=tk.RIGHT, padx=5, pady=5)
        tk.Entry(frame_video_label, width=20, font=input_font, textvariable=self.video_label).pack(side=tk.RIGHT, padx=5, pady=5)
        tk.Label(frame_video_label, text="Video label").pack(side=tk.RIGHT, padx=5, pady=5)

        # checkboxes for sonar and tactile sensors readings
        frame_checkboxes = tk.Frame(self)
        frame_checkboxes.pack(fill=tk.X)
        tactile = tk.Checkbutton(frame_checkboxes, text="Record tactile sensors", variable=self.recordTactile).pack(side=tk.RIGHT, padx=5, pady=5)
        sonar = tk.Checkbutton(frame_checkboxes, text="Record sonar readings", variable=self.recordSonar).pack(side=tk.RIGHT, padx=5, pady=5)

        # frame for record and stop buttons
        frame_buttons = tk.Frame(self)
        frame_buttons.pack(fill=tk.X)
        start_button = tk.Button(frame_buttons, text='Start recording', command=self.start)
        stop_button = tk.Button(frame_buttons, text='Stop recording', command=self.stop)
        close_button = tk.Button(frame_buttons, text='Close', command=self.close, width = 10)
        close_button.grid(row=0, column=2, padx=5, pady=5)
        stop_button.grid(row=0, column=1, padx=5, pady=5)
        start_button.grid(row=0, column=0, padx=5, pady=5)

        # frame for status display
        frame_label = tk.Frame(self)
        frame_label.pack(fill=tk.X)
        self.label = tk.Label(frame_label, text="Not connected")
        self.label.pack(fill=tk.X)

    def clear_label(self):
        self.video_label.set("")
        
    def connect(self):
        ''' Connect with the robot '''
        
        # try to establish a connection
        try:        
            self.videoRecorderProxy = ALProxy("ALVideoRecorder", self.ip.get(), self.port.get())
            self.videoRecorderProxy.setResolution(2)
            self.videoRecorderProxy.setFrameRate(30)
            self.videoRecorderProxy.setVideoFormat("MJPG")
            self.videoRecorderProxy.setCameraID(0)
            self.audioRecorderProxy = ALProxy("ALAudioDevice", self.ip.get(), self.port.get())
            self.memoryProxy = ALProxy("ALMemory", self.ip.get(), self.port.get())
            self.sonarProxy = ALProxy("ALSonar", self.ip.get(), self.port.get())
            self.isConnected = True
            self.label.config(text='Ready')
        # connecting with robot failed
        except:
            self.isConnected = False
            self.label.config(text='Not connected')

    def switchCamera(self):
        ''' Change the recording device on the robot '''
        
        # switch camera if connected
        if self.isConnected and not self.isRecordingVideo:
            self.videoRecorderProxy.setCameraID(1 - self.videoRecorderProxy.getCameraID())
            self.camera_label.config(text=self.camera_dict[self.videoRecorderProxy.getCameraID()])

    def switchAudio(self):
        ''' Change the format of audio recording
            .ogg is a single channel recording from the front microphone
            .wav (default) is a 4-channel recording from all microphones
        '''
        if not self.isRecordingAudio:
            self.audio_id = 1 - self.audio_id
            self.audio_label.config(text=self.audio_dict[self.audio_id])

    def start(self):
        ''' Start recording if connected'''
        if not self.isConnected:
            self.label.config(text='Not connected')
            return
        
        # use timestamped filenames
        filename = time.strftime("%Y%m%d_%H%M%S")+"_"+self.video_label.get()
        filename_audio = filename+self.audio_dict[self.audio_id]

        # start recording
        self.videoRecorderProxy.startRecording("/home/nao/recordings/", filename)
        self.isRecordingVideo = True
        self.audioRecorderProxy.startMicrophonesRecording("/home/nao/recordings/"+filename_audio)
        self.isRecordingAudio = True
        self.label.config(text='Recording')
        if self.recordSonar.get():
            self.log_sonar = open('./sensor_readings/'+filename+'_sonar.txt', 'w')
            self.isRecordingSonar = True
            self.sonarProxy.subscribe("myApp")
        if self.recordTactile.get():
            self.isRecordingTactile = True
            self.log_tactile = open('./sensor_readings/'+filename+'_tactile.txt', 'w')
        self.time_start = time.time()


    def stop(self):
        ''' Stop recording if connected and already recording '''
        
        if not self.isConnected:
            self.label.config(text='Not connected')
            return
        if self.isRecordingVideo:
            video_info = self.videoRecorderProxy.stopRecording()
            self.isRecordingVideo = False
        if self.isRecordingAudio:
            audio_info = self.audioRecorderProxy.stopMicrophonesRecording()
            self.isRecordingAudio = False
        if not self.isRecordingAudio and not self.isRecordingVideo:
            self.label.config(text='Recording stopped')
        if self.isRecordingSonar:
            self.isRecordingSonar = False
            self.log_sonar.close()
            self.sonarProxy.unsubscribe("myApp")
        if self.isRecordingTactile:
            self.isRecordingTactile = False
            self.log_tactile.close()

    def close(self):
        ''' Stop recording and close the program '''

        if self.isRecordingVideo:
            self.videoRecorderProxy.stopRecording()
        if self.isRecordingAudio:
            self.audioRecorderProxy.stopMicrophonesRecording()
        self.master.destroy()

    def to_do(self):
        time_stamp = time.time()-self.time_start
        if self.isRecordingSonar:
            val_left = self.memoryProxy.getData("Device/SubDeviceList/US/Left/Sensor/Value")
            val_right = self.memoryProxy.getData("Device/SubDeviceList/US/Right/Sensor/Value")
            self.log_sonar.write(str(time_stamp)+','+str(val_right)+','+str(val_left)+'\n')
        if self.isRecordingTactile:
            val_left1 = str(self.memoryProxy.getData("HandRightLeftTouched"))
            val_left2 = str(self.memoryProxy.getData("HandRightBackTouched"))
            val_left3 = str(self.memoryProxy.getData("HandRightRightTouched"))
            val_right1 = str(self.memoryProxy.getData("HandLeftLeftTouched"))
            val_right2 = str(self.memoryProxy.getData("HandLeftBackTouched"))
            val_right3 = str(self.memoryProxy.getData("HandLeftRightTouched"))
            self.log_tactile.write(str(time_stamp)+','+val_left1+','+val_left2+','+val_left3+','+val_right1+','+val_right2+','+val_right3+'\n')
        self.master.after(10, self.to_do)

def main():
    ''' Main function '''
    
    # create tkinter window
    root = tk.Tk()
    main_window = MainWindow(root)
    main_window.to_do()
    # enter tk loop
    root.mainloop()

if __name__ == "__main__":
    main()

