# Robotics Cats Lookout Desktop

A real-time wildfire detection system that monitors camera feeds and YouTube streams for potential fire outbreaks, with automated WhatsApp alerts.

## Tools & Technologies

### Backend

- **Python 3.8+** - Core programming language
- **Flask** - Web framework for API endpoints and server management
- **Flask-SocketIO** - Real-time WebSocket communication
- **OpenCV (cv2)** - Computer vision for image processing
- **yt-dlp** - YouTube video downloading and streaming
- **requests** - HTTP client for API calls and camera communication
- **psutil** - System monitoring (CPU, network usage)
- **Twilio** - WhatsApp messaging API

### Frontend

- **React.js** - User interface framework
- **JavaScript (ES6+)** - Frontend programming
- **CSS3** - Styling and responsive design
- **Leaflet.js** - Interactive mapping
- **Socket.IO Client** - Real-time updates

### AI & Detection

- **Robotics Cats Lookout API** - Wildfire detection service
- **JSON** - Data interchange format
- **HTTP Digest Authentication** - Secure camera access

### Development & Deployment

- **Node.js** - Package management and build tools
- **npm** - JavaScript package manager
- **Git** - Version control
- **Environment Variables** - Secure configuration management

## Features

- **Multi-Source Monitoring**: Monitor both IP cameras and YouTube live streams
- **Real-Time Detection**: AI-powered wildfire detection with confidence scoring
- **Automated Alerts**: WhatsApp notifications when high-confidence detections are found
- **Web Dashboard**: React-based interface for monitoring and managing instances
- **System Monitoring**: Real-time CPU and network usage tracking
- **Geographic Mapping**: Visual representation of camera locations on a map

## Architecture

The system consists of:

- **Flask Backend** (`app.py`): Main server handling API endpoints, instance management, and alert system
- **Instance Classes** (`src/instance.py`): Separate classes for YouTube and IP camera monitoring
- **React Frontend** (`src/`): Dashboard for viewing detections, managing instances, and system monitoring
- **Twilio Integration**: WhatsApp alert system for wildfire notifications

## Prerequisites

- Python 3.8+
- Node.js 14+
- Twilio account with WhatsApp API access
- IP camera access (for camera instances)
- YouTube API access (for YouTube instances)

## Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/sarayumummidi/robotics-cats-lookout-desktop.git
   cd project-4
   ```

2. **Install Python dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Install Node.js dependencies**

   ```bash
   npm install
   ```

4. **Set up environment variables**
   Create a `.env` file in the root directory:
   ```env
   TWILIO_SID=your_twilio_account_sid
   AUTH_TOKEN=your_twilio_auth_token
   ```

## Configuration

### Instance Types

#### YouTube Instance

Monitor YouTube live streams for wildfire detection:

```json
{
  "name": "Spray Valley",
  "instance_type": "youtube",
  "youtube_url": "https://www.youtube.com/watch?v=HghxOQ12dy4",
  "frequency": 60,
  "lookout_endpoint": "https://lax.pop.roboticscats.com/api/detects?apiKey=your_api_key",
  "latitude": 50.8641,
  "longitude": -115.356,
  "status": "stopped"
}
```

#### Camera Instance

Monitor IP cameras for wildfire detection:

```json
{
  "name": "Big Tree",
  "instance_type": "camera",
  "camera_url": "http://camera.ip.address/axis-cgi/jpg/image.cgi?resolution=1920x1080",
  "camera_username": "username",
  "camera_password": "password",
  "folder_path": "./images",
  "frequency": 60,
  "lookout_endpoint": "https://lax.pop.roboticscats.com/api/detects?apiKey=your_api_key",
  "latitude": 37.4848,
  "longitude": 122.2281,
  "status": "stopped"
}
```

## Usage

### Starting the Application

1. **Start the Flask backend**

   ```bash
   python app.py
   ```

   The server will start on `http://localhost:5000`

2. **Start the React frontend** (in a new terminal)
   ```bash
   npm start
   ```
   The dashboard will be available at `http://localhost:3000`

### Managing Instances

1. **Add New Instance**

   - Navigate to the dashboard
   - Click "Add Instance"
   - Fill in the required fields (name, type, URL, credentials)
   - Set the monitoring frequency and detection endpoint
   - Add geographic coordinates for mapping

2. **Start/Stop Monitoring**

   - Use the toggle buttons in the instances table
   - Instances will automatically capture frames at the specified frequency
   - Detection results are displayed in real-time

3. **View Detections**
   - Navigate to "Camera View" to see live images with detection overlays
   - Detection bounding boxes are displayed on images
   - Confidence scores are shown for each detection

### Alert System

The system automatically sends WhatsApp alerts when:

- High-confidence detections (>50% confidence) are found
- Detection results contain valid bounding box coordinates
- Instance configuration includes valid geographic coordinates

Alert message format:

```
Wildfire detected at location {latitude}, {longitude} from Camera {instance_name}. Please evacuate immediately.
```

## API Endpoints

### Instance Management

- `GET /api/instances` - Get all instances
- `POST /api/instances` - Add new instance
- `PUT /api/instances/<name>` - Update instance
- `DELETE /api/instances/<name>` - Delete instance
- `POST /api/instances/<name>/start` - Start instance
- `POST /api/instances/<name>/stop` - Stop instance

### Detection Data

- `GET /api/detections` - Get detection results for all instances
- `GET /api/images` - Get list of captured images

### System Monitoring

- `GET /` - Main dashboard
- WebSocket events for real-time system stats

## File Structure

```
project-4/
├── app.py                 # Main Flask application
├── src/
│   ├── instance.py        # Instance classes (YouTube/Camera)
│   ├── App.js            # Main React component
│   ├── components/       # React components
│   │   ├── Dashboard.js
│   │   ├── FullView.js
│   │   ├── InstanceMap.js
│   │   └── ...
│   └── ...
├── frames/               # Captured images from instances
├── images/               # Camera capture storage
├── settings.json         # Instance configurations
└── requirements.txt      # Python dependencies
```

## Monitoring and Logs

The system provides comprehensive logging:

- **Instance Logs**: Frame capture, detection results, and errors
- **System Logs**: CPU usage, network statistics, and alert notifications
- **Error Handling**: Graceful handling of network issues and API failures

## Security Considerations

- Store sensitive credentials in environment variables
- Use HTTPS in production
- Implement proper authentication for the web interface
- Secure camera credentials and API keys
- Regular security updates for dependencies

## Troubleshooting

### Common Issues

1. **Camera Connection Failed**

   - Verify camera URL and credentials
   - Check network connectivity
   - Ensure camera supports HTTP Digest Authentication

2. **YouTube Stream Issues**

   - Verify YouTube URL is accessible
   - Check if stream is live
   - Ensure yt-dlp is up to date

3. **Detection API Errors**

   - Verify API key is valid
   - Check endpoint URL
   - Ensure proper image format (JPEG)

4. **WhatsApp Alert Failures**
   - Verify Twilio credentials
   - Check phone number format
   - Ensure WhatsApp Business API is enabled

### Debug Mode

Enable debug logging by setting:

```python
app.debug = True
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:

- Create an issue in the repository
- Contact the development team
- Check the troubleshooting section above
