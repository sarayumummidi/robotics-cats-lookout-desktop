# Robotics Cats - YT Adapter

A lightweight web-based adapter that transforms YouTube livestreams into periodic frame submissions for wildfire detection processing through the RoboticsCats SaaS platform.

## Usage
To use the YT Adapter, follow these steps:
1. **Install Dependencies**: Ensure you have Python 3.x installed along with the required libraries:
   ```bash
   pip install -r requirements.txt
   ```
2. **Configure the Adapter**: Edit the `config.json` file to set your YouTube livestream URL, frame capture interval, and other parameters.  
Below is an example configuration:

```json
{
       "instances": [
              {
                     "name": "Spray Valley",
                     "youtube_url": "https://www.youtube.com/watch?v=YOUR_STREAM_ID",
                     "frequency": 600,
                     "output_url": "https://your-roboticscats-server/api/detects?apiKey=YOUR_API_KEY",
                     "latitude": 50.8641,
                     "longitude": -115.356,
                     "status": "running"
              },
              {
                     "name": "Banff",
                     "youtube_url": "https://www.youtube.com/watch?v=YOUR_STREAM_ID",
                     "frequency": 600,
                     "output_url": "https://your-roboticscats-server/api/detects?apiKey=YOUR_API_KEY",
                     "latitude": 51.1784,
                     "longitude": -115.5708,
                     "status": "running"
              }
       ]
}
```

- Replace the `youtube_url` and `output_url` values with your actual stream and API endpoint.
- Set `frequency` to the desired frame capture interval in seconds.
- Add or remove instances as needed for your deployment.

3. **Run the Adapter**: Start the adapter using:
   ```bash
   python app.py (or python3 app.py)
   ```

## Overview

RoboticsCats is a comprehensive wildfire detection SaaS solution that leverages computer vision and machine learning to identify early signs of wildfires. The YT Adapter extends this capability by allowing existing YouTube livestream infrastructure (such as wildlife cameras, traffic cameras, and other public streams) to be seamlessly integrated into a fleet of early detection systems.

This adapter captures frames from YouTube livestreams at configurable intervals and posts them to RoboticsCats servers for real-time wildfire detection analysis, enabling rapid response to potential fire threats.

## How It Works

1. **Stream Connection**: The adapter connects to YouTube livestreams using yt-dlp
2. **Frame Capture**: OpenCV captures frames at the specified frequency
3. **Processing**: Frames are encoded as JPEG and sent to RoboticsCats servers
4. **Analysis**: RoboticsCats AI analyzes frames for wildfire detection
5. **Alerts**: Early detection results trigger appropriate response protocols

## System Architecture

```
YouTube Livestream → YT Adapter → RoboticsCats API → Wildfire Detection
                        ↓
                 Web Dashboard (Monitoring & Control)
```

## Technical Specifications

- **Supported Video Formats**: All formats supported by yt-dlp and OpenCV
- **Frame Processing**: JPEG encoding with configurable quality
- **Concurrent Instances**: Unlimited (limited by system resources)
- **Geographic Mapping**: Leaflet.js with dark tile layers
- **Real-time Updates**: WebSocket-based status synchronization

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

**Jerry Wu** ([@jerryjiawu](https://github.com/jerryjiawu))

**🔥 Early Detection Saves Lives and Property 🔥**

*This adapter is part of a larger ecosystem dedicated to wildfire prevention and early response. Every instance deployed contributes to a safer, more resilient community.*
