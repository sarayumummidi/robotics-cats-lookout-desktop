import yt_dlp
import cv2
import time
import numpy as np
from datetime import datetime
import os
import requests
from requests.auth import HTTPDigestAuth

ydl_opts = {
            'format': 'bestvideo[ext=mp4]/bestvideo/best',
            'quiet': True,
}

if not os.path.exists("./frames"):
    os.makedirs("./frames")

class Instance:
    def __init__(self, id, name, frequency, lookout_endpoint, latitude, longitude):
        self.id = id
        self.name = name
        self.frequency = frequency
        self.lookout_endpoint = lookout_endpoint
        self.latitude = latitude
        self.longitude = longitude
        self.run = True
        self.instance_type = ""
        self.latest_frame = None
        self.latest_detections = None

    
    def start(self):
        raise NotImplementedError("Subclasses must implement start()")
    
    def stop(self):
        self.run = False
        print(f"[INSTANCE {self.id}] Stopping instance...")

class YoutubeInstance(Instance):
    def __init__(self, id:int, name:str, youtube_url:str, lookout_endpoint:str, frequency:int=60, latitude:float=0.0, longitude:float=0.0):
        super().__init__(id, name, frequency, lookout_endpoint, latitude, longitude)
        self.youtube_url = youtube_url
        self.ydl = yt_dlp.YoutubeDL(ydl_opts)
        self.instance_type = "youtube"
        self.image_file = f"./frames/youtube_{self.name.lower().replace(' ', '')}.jpg"
        print(f"[INSTANCE {self.id}] Initialized with YouTube URL: {self.youtube_url}, Lookout Endpoint URL: {self.lookout_endpoint}, Frequency: {self.frequency} seconds")

    def start(self):
        t = 0
        info = self.ydl.extract_info(self.youtube_url, download=False)
        if info is None:
            print(f"[INSTANCE {self.id}] Error: Could not extract video info")
            return
        stream_url = info['url']
        
        cap = cv2.VideoCapture(stream_url)
        
        if not cap.isOpened():
            print(f"[INSTANCE {self.id}] Error: Could not open video stream.")
            return
        
        try:
            while self.run:
                try:
                    time.sleep(self.frequency - (time.time() - t))
                except ValueError:
                    pass
                t = time.time()
                ret, frame = cap.read()
                
                if not ret:
                    print(f"[INSTANCE {self.id}] Error: Could not read frame.")
                    time.sleep(5)
                    continue

                self.latest_frame = frame.copy()
                
                # Save frame to single image file
                cv2.imwrite(self.image_file, frame)
                print(f"[INSTANCE {self.id}] Image captured and saved to {self.image_file} at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                
                # Add some debugging to check if frames are actually different
                if hasattr(self, 'last_frame_hash'):
                    import hashlib
                    current_hash = hashlib.md5(frame.tobytes()).hexdigest()
                    if current_hash == self.last_frame_hash:
                        print(f"[INSTANCE {self.id}] WARNING: Same frame detected, stream might be static")
                    else:
                        print(f"[INSTANCE {self.id}] New frame detected")
                    self.last_frame_hash = current_hash
                else:
                    import hashlib
                    self.last_frame_hash = hashlib.md5(frame.tobytes()).hexdigest()
                
                _, buffer = cv2.imencode('.jpg', frame)
                headers = {'Content-Type': 'image/jpeg'}
                try:
                    response = requests.post(self.lookout_endpoint, data=buffer.tobytes(), headers=headers)
                    if response.status_code != 200:
                        print(f"[INSTANCE {self.id}] Warning: Failed to post frame, status code {response.status_code}")
                    else:
                        print(f"[INSTANCE {self.id}] Frame posted successfully at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                        # Parse detection results
                        try:
                            detection_data = response.json()
                            self.latest_detections = detection_data
                            print(f"[INSTANCE {self.id}] Detection results: {detection_data}")
                        except Exception as parse_error:
                            print(f"[INSTANCE {self.id}] Error parsing detection results: {parse_error}")
                except Exception as e:
                    print(f"[INSTANCE {self.id}] Error posting frame: {e}")
                

        except KeyboardInterrupt:
            print(f"[INSTANCE {self.id}] Stopping frame capture...")
        finally:
            cap.release()
    
    def stop(self):
        self.run = False
        print(f"[INSTANCE {self.id}] Stopping instance...")

class CameraInstance(Instance):
    def __init__(self, id:int, name:str, camera_url:str, lookout_endpoint:str, camera_username:str, camera_password:str, folder_path:str, frequency:int=60, latitude:float=0.0, longitude:float=0.0):
        super().__init__(id, name, frequency, lookout_endpoint, latitude, longitude)
        self.camera_url = camera_url
        self.camera_username = camera_username
        self.camera_password = camera_password
        self.folder_path = folder_path
        self.instance_type = "camera"
        self.image_file = f"./frames/camera_{self.name.lower().replace(' ', '')}.jpg"
        print(f"[INSTANCE {self.id}] Initialized with Camera URL: {self.camera_url}, Folder Path: {self.folder_path}, Frequency: {self.frequency} seconds")

    def start(self):
        t = 0
        
        try:
            while self.run:
                start_time = time.time()
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                image_path = os.path.join(self.folder_path, "capture.jpg")
                
                # step 1: capture image
                try: 
                    response = requests.get(self.camera_url, auth=HTTPDigestAuth(self.camera_username, self.camera_password), stream=True)
                    if response.status_code != 200:
                        print(f"[INSTANCE {self.id}] Error: Could not capture image, status code {response.status_code}")
                        time.sleep(5)
                        continue
                    else:
                        arr = np.frombuffer(response.content, dtype=np.uint8)
                        frame = cv2.imdecode(arr, cv2.IMREAD_COLOR)
                        if frame is None:
                            print(f"[INSTANCE {self.id}] Error: Could not decode image.")
                            time.sleep(5)
                            continue
                        cv2.imwrite(image_path, frame)
                        print(f"[INSTANCE {self.id}] Image captured and saved to {image_path}")

                        # Save to image file for full view dashboard
                        cv2.imwrite(self.image_file, frame)
                        print(f"[INSTANCE {self.id}] Image captured and saved to {self.image_file}")
                except Exception as e:
                    print(f"[INSTANCE {self.id}] Error capturing image: {e}")
                    time.sleep(5)
                    continue
                    
                # step 2: post image to API
                try:
                    with open(image_path, 'rb') as f:
                        response = requests.post(self.lookout_endpoint, data=f.read(), headers={'Content-Type': 'image/jpeg'})
                        if response.status_code != 200:
                            print(f"[INSTANCE {self.id}] Error: Failed to post image, status code {response.status_code}")
                        else:
                            print(f"[INSTANCE {self.id}] Image posted successfully at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                            # Parse detection results
                            try:
                                detection_data = response.json()
                                self.latest_detections = detection_data
                                print(f"[INSTANCE {self.id}] Detection results: {detection_data}")
                            except Exception as parse_error:
                                print(f"[INSTANCE {self.id}] Error parsing detection results: {parse_error}")
                except Exception as e:
                    print(f"[INSTANCE {self.id}] Error posting image: {e}")
                    time.sleep(5)
                    continue
                
                # step 3: sleep for the rest of the frequency
                elapsed_time = time.time() - start_time
                time.sleep(max(0, self.frequency - elapsed_time))

        except KeyboardInterrupt:
            print(f"[INSTANCE {self.id}] Stopping folder monitoring...")
                
    
    def stop(self):
        self.run = False
        print(f"[INSTANCE {self.id}] Stopping instance...")

if __name__ == "__main__":
    camera_url = "http://demo.customer.roboticscats.com:55758/axis-cgi/jpg/image.cgi?resolution=1920x1080"
    camera_username = "root"
    camera_password = "Cashflow108!"
    folder_path = "./images"
    instance = CameraInstance(2, "Camera-1", camera_url, "https://lax.pop.roboticscats.com/api/detects?apiKey=69ee9fa22340e2d84da76c282f9d2033", camera_username, camera_password, folder_path, 60)
    instance.start()

