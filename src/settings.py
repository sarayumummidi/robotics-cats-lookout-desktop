import json
from src.instance import YoutubeInstance, CameraInstance

def load_settings(file_path='settings.json'):
    try:
        with open(file_path, 'r') as file:
            settings = json.load(file)
        print("Settings loaded successfully.")
        return settings
    except FileNotFoundError:
        print(f"Settings file '{file_path}' not found.")
        return {"instances": []}
    except json.JSONDecodeError:
        print(f"Error decoding JSON from the settings file '{file_path}'.")
        return {"instances": []}
    
def create_instances(settings):
    instances = []
    
    # Create instances based on type
    for item in settings.get("instances", []):
        instance_type = item.get("type")
        
        if instance_type == "youtube":
            instance = YoutubeInstance(
                id=item.get("id"),
                name=item.get("name"),
                youtube_url=item.get("youtube_url"),
                lookout_endpoint=item.get("output_url"),
                frequency=item.get("frequency", 60),
                latitude=item.get("latitude", 0.0),
                longitude=item.get("longitude", 0.0)
            )
            instances.append(instance)
        elif instance_type == "camera":
            instance = CameraInstance(
                id=item.get("id"),
                name=item.get("name"),
                camera_url=item.get("camera_url"),
                lookout_endpoint=item.get("output_url"),
                camera_username=item.get("camera_username"),
                camera_password=item.get("camera_password"),
                folder_path=item.get("folder_path", "./camera_images"),
                frequency=item.get("frequency", 60),
                latitude=item.get("latitude", 0.0),
                longitude=item.get("longitude", 0.0)
            )
            instances.append(instance)
        else:
            print(f"Unknown instance type: {instance_type}")
    
    return instances
    
    return instances

def save_settings(settings, file_path='settings.json'):
    try:
        with open(file_path, 'w') as file:
            json.dump(settings, file, indent=4)
        print("Settings saved successfully.")
    except Exception as e:
        print(f"Error saving settings: {e}")

