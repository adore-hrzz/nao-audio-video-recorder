from naoqi import ALProxy
import time
import Tkinter as tk
import tkFont


class MainWindow(tk.Frame):
    ''' Main Window '''

    def __init__(self, master):
        self.master = master

        # initialize tk frame
        tk.Frame.__init__(self, master, width=380, height=100)
        
        # initialize variables
        self.isRecordingVideo = False
        self.isRecordingAudio = False
        self.isConnected = False
        self.ip = tk.StringVar()
        self.port = tk.IntVar()

        # create GUI
        self.initializeGUI()

        # create naoqi proxies
        self.videoRecorderProxy = []
        self.audioRecorderProxy = []


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
        
        # frame for record, stop and close buttons
        frame_buttons = tk.Frame(self)
        frame_buttons.pack(fill=tk.X)
        start_button = tk.Button(frame_buttons, text='Start recording', command=self.start, width = 12)
        stop_button = tk.Button(frame_buttons, text='Stop recording', command=self.stop, width = 12)
        close_button = tk.Button(frame_buttons, text='Close', command=self.close, width = 12)
        close_button.pack(side=tk.RIGHT, padx=5, pady=5)
        stop_button.pack(side=tk.RIGHT, padx=5, pady=5)
        start_button.pack(side=tk.RIGHT, padx=5, pady=5)

        # frame for status display
        frame_label = tk.Frame(self)
        frame_label.pack(fill=tk.X)
        self.label = tk.Label(frame_label, text="Not connected")
        self.label.pack(fill=tk.X)

    def connect(self):
        ''' Connect with the robot '''
        
        # try to establish a connection
        try:        
            self.videoRecorderProxy = ALProxy("ALVideoRecorder", self.ip.get(), self.port.get())
            self.videoRecorderProxy.setResolution(2)
            self.videoRecorderProxy.setFrameRate(30)
            self.videoRecorderProxy.setVideoFormat("MJPG")
            self.audioRecorderProxy = ALProxy("ALAudioDevice", self.ip.get(), self.port.get())
            self.isConnected = True
            self.label.config(text='Ready')
        # connecting with robot failed
        except:
            self.isConnected = False
            self.label.config(text='Not connected')           


    def start(self):
        ''' Start recording if connected'''
        if not self.isConnected:
            self.label.config(text='Not connected')
            return
        
        # use timestamped filenames
        filename = time.strftime("%Y%m%d_%H%M%S")
        filename_audio = filename+".wav"

        # start recording
        self.videoRecorderProxy.startRecording("/home/nao/recordings/cameras", filename)
        self.isRecordingVideo = True
        self.audioRecorderProxy.startMicrophonesRecording("/home/nao/recordings/microphones/"+filename_audio)
        self.isRecordingAudio = True
        self.label.config(text='Recording')


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

    def close(self):
        ''' Stop recording and close the program '''

        if self.isRecordingVideo:
            self.videoRecorderProxy.stopRecording()
        if self.isRecordingAudio:
            self.audioRecorderProxy.stopMicrophonesRecording()
        self.master.destroy()

def main():
    ''' Main function '''
    
    # create tkinter window
    root = tk.Tk()
    root.geometry("380x100+380+100")
    mainWindow = MainWindow(root)

    # enter tk loop
    root.mainloop()

if __name__ == "__main__":
    main()
