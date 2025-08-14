from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash, send_file
from flask_socketio import SocketIO, emit
import json
import psutil
import threading
import time
import subprocess
import os
from datetime import datetime
import re
from src.instance import Instance, YoutubeInstance, CameraInstance
from twilio.rest import Client
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.urandom(24)
socketio = SocketIO(app, cors_allowed_origins="*", logger=False, engineio_logger=False)

# Serve static files from frames and images folders
@app.route('/frames/<path:filename>')
def serve_frame(filename):
    return send_file(f'./frames/{filename}', mimetype='image/jpeg')

@app.route('/images/<path:filename>')
def serve_image(filename):
    return send_file(f'./images/{filename}', mimetype='image/jpeg')

SETTINGS_FILE = 'settings.json'

instances_status = {}
instance_objects = {}
system_stats = {'cpu': 0, 'network_sent': 0, 'network_recv': 0}

def load_settings():
    try:
        with open(SETTINGS_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {"instances": []}

def save_settings(settings):
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(settings, f, indent=4)



def extract_youtube_id(url):
    patterns = [
        r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([^&\n?#]+)',
        r'youtube\.com\/watch\?.*v=([^&\n?#]+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

def monitor_system():
    global system_stats
    last_network = psutil.net_io_counters()
    
    while True:
        try:
            system_stats['cpu'] = int(psutil.cpu_percent(interval=1))
            
            current_network = psutil.net_io_counters()
            system_stats['network_sent'] = int((current_network.bytes_sent - last_network.bytes_sent) / 1024 / 1024)
            system_stats['network_recv'] = int((current_network.bytes_recv - last_network.bytes_recv) / 1024 / 1024)
            last_network = current_network
            
            # Emit system stats to connected clients
            socketio.emit('system_stats', system_stats)
            
        except Exception as e:
            print(f"Error monitoring system: {e}")
        
        time.sleep(5)  # Increased interval to reduce spam

def restore_running_instances():
    settings = load_settings()
    for instance_config in settings.get('instances', []):
        if instance_config.get('status') == 'running':
            instance_name = instance_config['name']
            try:
                # Determine instance type and create appropriate instance
                instance_type = instance_config.get('instance_type', 'youtube')
                
                if instance_type == 'youtube':
                    instance_obj = YoutubeInstance(
                        id=instance_config['name'],
                        name=instance_config['name'],
                        youtube_url=instance_config['youtube_url'],
                        lookout_endpoint=instance_config['lookout_endpoint'],
                        frequency=instance_config['frequency'],
                        latitude=instance_config.get('latitude', 0.0),
                        longitude=instance_config.get('longitude', 0.0)
                    )
                elif instance_type == 'camera':
                    instance_obj = CameraInstance(
                        id=instance_config['name'],
                        name=instance_config['name'],
                        camera_url=instance_config['camera_url'],
                        lookout_endpoint=instance_config['lookout_endpoint'],
                        camera_username=instance_config['camera_username'],
                        camera_password=instance_config['camera_password'],
                        folder_path=instance_config['folder_path'],
                        frequency=instance_config['frequency'],
                        latitude=instance_config.get('latitude', 0.0),
                        longitude=instance_config.get('longitude', 0.0)
                    )
                else:
                    print(f"[SYSTEM] Unknown instance type '{instance_type}' for instance '{instance_name}'")
                    continue
                
                instance_thread = threading.Thread(target=instance_obj.start, daemon=True)
                instance_thread.start()
                
                instance_objects[instance_name] = instance_obj
                instances_status[instance_name] = {
                    'status': 'running',
                    'start_time': datetime.now(),
                    'thread': instance_thread
                }
                
                print(f"[SYSTEM] Restored running instance '{instance_name}'")
                
            except Exception as e:
                print(f"[SYSTEM] Failed to restore instance '{instance_name}': {e}")
                instance_config['status'] = 'stopped'
                save_settings(settings)

monitor_thread = threading.Thread(target=monitor_system, daemon=True)
monitor_thread.start()

restore_running_instances()

@app.route('/')
def index():
    settings = load_settings()
    return render_template('index.html', settings=settings)



@app.route('/api/instances', methods=['GET'])
def get_instances():
    try:
        settings = load_settings()
        return jsonify(settings)
    except Exception as e:
        print(f"Error in get_instances: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/instances', methods=['POST'])
def add_instance():
    
    data = request.get_json()
    settings = load_settings()
    
    existing_names = [instance['name'] for instance in settings['instances']]
    new_name = data.get('name', f"Instance-{len(existing_names) + 1}")
    
    counter = 1
    original_name = new_name
    while new_name in existing_names:
        new_name = f"{original_name}-{counter}"
        counter += 1
    
    new_instance = {
        'name': new_name,
        'instance_type': data.get('instance_type', 'youtube'),
        'youtube_url': data.get('youtube_url', ''),
        'camera_url': data.get('camera_url', ''),
        'camera_username': data.get('camera_username', ''),
        'camera_password': data.get('camera_password', ''),
        'folder_path': data.get('folder_path', './images'),
        'frequency': data.get('frequency', 60),
        'lookout_endpoint': data.get('lookout_endpoint', ''),
        'latitude': data.get('latitude', 0.0),
        'longitude': data.get('longitude', 0.0),
        'status': 'stopped'
    }
    
    settings['instances'].append(new_instance)
    save_settings(settings)
    
    socketio.emit('instance_added', new_instance)
    return jsonify(new_instance)

@app.route('/api/instances/<instance_name>', methods=['PUT'])
def update_instance(instance_name):
    
    data = request.get_json()
    settings = load_settings()
    
    for instance in settings['instances']:
        if instance['name'] == instance_name:
            instance.update({
                'instance_type': data.get('instance_type', instance.get('instance_type', 'youtube')),
                'frequency': data.get('frequency', instance['frequency']),
                'lookout_endpoint': data.get('lookout_endpoint', instance['lookout_endpoint']),
                'latitude': data.get('latitude', instance.get('latitude', 0.0)),
                'longitude': data.get('longitude', instance.get('longitude', 0.0))
            })
            
            # Update type-specific fields
            if instance['instance_type'] == 'youtube':
                instance['youtube_url'] = data.get('youtube_url', instance.get('youtube_url', ''))
            elif instance['instance_type'] == 'camera':
                instance['camera_url'] = data.get('camera_url', instance.get('camera_url', ''))
                instance['camera_username'] = data.get('camera_username', instance.get('camera_username', ''))
                instance['camera_password'] = data.get('camera_password', instance.get('camera_password', ''))
                instance['folder_path'] = data.get('folder_path', instance.get('folder_path', './images'))
            break
    
    save_settings(settings)
    socketio.emit('instance_updated', {'name': instance_name, 'data': data})
    return jsonify({'success': True})

@app.route('/api/instances/<instance_name>', methods=['DELETE'])
def delete_instance(instance_name):
    
    if instance_name in instance_objects:
        instance_obj = instance_objects[instance_name]
        instance_obj.stop()
        del instance_objects[instance_name]
        print(f"[SYSTEM] Stopped instance '{instance_name}' before deletion")
    
    if instance_name in instances_status:
        del instances_status[instance_name]
    
    settings = load_settings()
    settings['instances'] = [inst for inst in settings['instances'] if inst['name'] != instance_name]
    save_settings(settings)
    
    socketio.emit('instance_deleted', {'name': instance_name})
    return jsonify({'success': True})

@app.route('/api/instances/<instance_name>/start', methods=['POST'])
def start_instance(instance_name):
    
    if instance_name in instances_status and instances_status[instance_name]['status'] == 'running':
        return jsonify({'error': 'Instance already running'}), 400
    
    settings = load_settings()
    instance_config = next((inst for inst in settings['instances'] if inst['name'] == instance_name), None)
    
    if not instance_config:
        return jsonify({'error': 'Instance not found'}), 404
    
    try:
        # Determine instance type and create appropriate instance
        instance_type = instance_config.get('instance_type', 'youtube')
        
        if instance_type == 'youtube':
            instance_obj = YoutubeInstance(
                id=instance_config['name'],
                name=instance_config['name'],
                youtube_url=instance_config['youtube_url'],
                lookout_endpoint=instance_config['lookout_endpoint'],
                frequency=instance_config['frequency'],
                latitude=instance_config.get('latitude', 0.0),
                longitude=instance_config.get('longitude', 0.0)
            )
        elif instance_type == 'camera':
            instance_obj = CameraInstance(
                id=instance_config['name'],
                name=instance_config['name'],
                camera_url=instance_config['camera_url'],
                lookout_endpoint=instance_config['lookout_endpoint'],
                camera_username=instance_config['camera_username'],
                camera_password=instance_config['camera_password'],
                folder_path=instance_config['folder_path'],
                frequency=instance_config['frequency'],
                latitude=instance_config.get('latitude', 0.0),
                longitude=instance_config.get('longitude', 0.0)
            )
        else:
            return jsonify({'error': f'Unknown instance type: {instance_type}'}), 400
        
        instance_thread = threading.Thread(target=instance_obj.start, daemon=True)
        instance_thread.start()
        
        instance_objects[instance_name] = instance_obj
        instances_status[instance_name] = {
            'status': 'running',
            'start_time': datetime.now(),
            'thread': instance_thread
        }
        
        instance_config['status'] = 'running'
        save_settings(settings)
        
        print(f"[SYSTEM] Started instance '{instance_name}' with frequency {instance_config['frequency']}s")
        socketio.emit('instance_status_changed', {'name': instance_name, 'status': 'running'})
        return jsonify({'success': True, 'status': 'running'})
        
    except Exception as e:
        print(f"[SYSTEM] Error starting instance '{instance_name}': {e}")
        return jsonify({'error': f'Failed to start instance: {str(e)}'}), 500

@app.route('/api/instances/<instance_name>/stop', methods=['POST'])
def stop_instance(instance_name):
    
    try:
        if instance_name in instance_objects:
            instance_obj = instance_objects[instance_name]
            instance_type = instance_obj.instance_type
            instance_obj.stop()
            del instance_objects[instance_name]
            print(f"[SYSTEM] Stopped instance '{instance_name}'")
        
        if instance_name in instances_status:
            del instances_status[instance_name]
        
        settings = load_settings()
        instance_config = next((inst for inst in settings['instances'] if inst['name'] == instance_name), None)
        if instance_config:
            instance_config['status'] = 'stopped'
            save_settings(settings)
        
        socketio.emit('instance_status_changed', {'name': instance_name, 'status': 'stopped'})
        if os.path.exists(f"./frames/{instance_type}_{instance_name.lower().replace(' ', '')}.jpg"):
            os.remove(f"./frames/{instance_type}_{instance_name.lower().replace(' ', '')}.jpg")
        return jsonify({'success': True, 'status': 'stopped'})
        
    except Exception as e:
        print(f"[SYSTEM] Error stopping instance '{instance_name}': {e}")
        return jsonify({'error': f'Failed to stop instance: {str(e)}'}), 500
    


@app.route('/api/images', methods=['GET'])
def get_images():
    """Get list of all images from frames folder"""
    images = []
    
    # Get all jpg files from frames folder
    if os.path.exists('./frames'):
        for filename in os.listdir('./frames'):
            if filename.endswith('.jpg'):
                # Extract instance name from filename (e.g., youtube_sprayvalley.jpg -> Spray Valley)
                if filename.startswith('youtube_'):
                    source_name = filename.replace('youtube_', '').replace('.jpg', '').replace('_', ' ').title()
                    instance_type = 'youtube'
                elif filename.startswith('camera_'):
                    source_name = filename.replace('camera_', '').replace('.jpg', '').replace('_', ' ').title()
                    instance_type = 'camera'
                else:
                    source_name = filename.replace('.jpg', '').replace('_', ' ').title()
                    instance_type = 'unknown'
                
                images.append({
                    'url': f'/frames/{filename}',
                    'source': source_name,
                    'type': instance_type,
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                })
    
    return jsonify({'images': images})

@app.route('/api/detections', methods=['GET'])
def get_all_detections():
    """Get detection results for all running instances"""
    detections = {}
    
    # Get real detection results from running instances
    for instance_name, instance_obj in instance_objects.items():
        if instance_obj.latest_detections:
            detections[instance_name] = instance_obj.latest_detections
    
    # Add fake detection results for testing (overrides real data)
    detections['Bigtree'] = {
        'results': [
            {
                'bottom': 413,
                'left': 726,
                'right': 862,
                'score': 0.8626816868782043,
                'top': 345
            }
        ]
    }
    
    # Check for detections and trigger WhatsApp alert
    if detections['Bigtree']['results'][0]['score'] > 0.5:
        settings = load_settings()
        instance_config = next((inst for inst in settings['instances'] if inst['name'] == 'big tree'), None)
        if not instance_config:
            print(f"[SYSTEM] No latitude, longitude, or instance name found for big tree")
            return jsonify({'detections': detections})
        latitude = instance_config.get('latitude', 0.0)
        longitude = instance_config.get('longitude', 0.0)
        instance_name = instance_config.get('name', 'big tree')
        
        try:
            send_whatsapp_alert(instance_name, latitude, longitude)
            print(f"[SYSTEM] WhatsApp alert sent for detection in {instance_name} at location {latitude}, {longitude}")
        except Exception as e:
            print(f"[SYSTEM] Error sending WhatsApp alert for {instance_name}: {e}")
    
    return jsonify({'detections': detections})


account_sid = os.getenv('TWILIO_SID')
auth_token = os.getenv('AUTH_TOKEN')
client = Client(account_sid, auth_token)
def send_whatsapp_alert(instance_name, latitude, longitude):
    alert = client.messages.create(
    from_='whatsapp:+14155238886',
    to='whatsapp:+19164958045',
    body=f'Wildfire detected at location {latitude}, {longitude} from {instance_name}. Please evacuate immediately.'
    )


@socketio.on('connect')
def handle_connect():
    emit('connected', {'data': 'Connected to dashboard'})

def cleanup_instances():
    """Stop all running instances on server shutdown"""
    print("[SYSTEM] Stopping all running instances...")
    for instance_name, instance_obj in instance_objects.items():
        try:
            instance_obj.stop()
            print(f"[SYSTEM] Stopped instance '{instance_name}'")
        except Exception as e:
            print(f"[SYSTEM] Error stopping instance '{instance_name}': {e}")
    
    settings = load_settings()
    for instance_config in settings.get('instances', []):
        if instance_config.get('status') == 'running':
            instance_config['status'] = 'stopped'
    save_settings(settings)

import atexit
atexit.register(cleanup_instances)

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
