import React, { useState, useEffect } from 'react'
import axios from 'axios'

function InstanceModal({ instance, onClose, onSave }) {
  const [formData, setFormData] = useState({
    name: '',
    instance_type: '',
    youtube_url: '',
    camera_url: '',
    camera_username: '',
    camera_password: '',
    folder_path: './camera_images',
    frequency: 60,
    lookout_endpoint: '',
    latitude: 0.0,
    longitude: 0.0,
  })

  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (instance) {
      // Editing existing instance
      setFormData({
        name: instance.name || '',
        instance_type: instance.youtube_url
          ? 'youtube'
          : instance.camera_url
          ? 'camera'
          : '',
        youtube_url: instance.youtube_url || '',
        camera_url: instance.camera_url || '',
        camera_username: instance.camera_username || '',
        camera_password: instance.camera_password || '',
        folder_path: instance.folder_path || './camera_images',
        frequency: instance.frequency || 60,
        lookout_endpoint: instance.lookout_endpoint || '',
        latitude: instance.latitude || 0.0,
        longitude: instance.longitude || 0.0,
      })
    } else {
      // Adding new instance
      setFormData({
        name: '',
        instance_type: '',
        youtube_url: '',
        camera_url: '',
        camera_username: '',
        camera_password: '',
        folder_path: './camera_images',
        frequency: 60,
        lookout_endpoint: '',
        latitude: 0.0,
        longitude: 0.0,
      })
    }
  }, [instance])

  const handleInputChange = (e) => {
    const { name, value } = e.target
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)

    try {
      const data = {
        name: formData.name,
        instance_type: formData.instance_type,
        frequency: parseInt(formData.frequency),
        lookout_endpoint: formData.lookout_endpoint,
        latitude: parseFloat(formData.latitude),
        longitude: parseFloat(formData.longitude),
      }

      // Add type-specific fields
      if (formData.instance_type === 'youtube') {
        data.youtube_url = formData.youtube_url
      } else if (formData.instance_type === 'camera') {
        data.camera_url = formData.camera_url
        data.camera_username = formData.camera_username
        data.camera_password = formData.camera_password
        data.folder_path = formData.folder_path
      }

      if (instance) {
        // Update existing instance
        await axios.put(`/api/instances/${instance.name}`, data)
      } else {
        // Create new instance
        await axios.post('/api/instances', data)
      }

      onSave()
    } catch (error) {
      console.error('Error saving instance:', error)
      alert(
        'Error saving instance: ' +
          (error.response?.data?.error || error.message)
      )
    } finally {
      setLoading(false)
    }
  }


  return (
    <div className="modal show">
      <div className="modal-content">
        <div className="modal-header">
          <h3>{instance ? 'Edit Instance' : 'Add Instance'}</h3>
          <span className="close" onClick={onClose}>
            &times;
          </span>
        </div>
        <div className="modal-body">
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label htmlFor="instance-name">Instance Name:</label>
              <input
                type="text"
                id="instance-name"
                name="name"
                value={formData.name}
                onChange={handleInputChange}
                required
              />
            </div>
            <div className="form-group">
              <label htmlFor="instance-type">Instance Type:</label>
              <select
                id="instance-type"
                name="instance_type"
                value={formData.instance_type}
                onChange={handleInputChange}
                required
              >
                <option value="">Select Type</option>
                <option value="youtube">YouTube</option>
                <option value="camera">Camera</option>
              </select>
            </div>

            {/* YouTube Fields */}
            {formData.instance_type === 'youtube' && (
              <div>
                <div className="form-group">
                  <label htmlFor="youtube-url">YouTube URL:</label>
                  <input
                    type="url"
                    id="youtube-url"
                    name="youtube_url"
                    value={formData.youtube_url}
                    onChange={handleInputChange}
                    required
                  />
                </div>
              </div>
            )}

            {/* Camera Fields */}
            {formData.instance_type === 'camera' && (
              <div>
                <div className="form-group">
                  <label htmlFor="camera-url">Camera URL:</label>
                  <input
                    type="url"
                    id="camera-url"
                    name="camera_url"
                    value={formData.camera_url}
                    onChange={handleInputChange}
                    required
                  />
                </div>
                <div className="form-group">
                  <label htmlFor="camera-username">Camera Username:</label>
                  <input
                    type="text"
                    id="camera-username"
                    name="camera_username"
                    value={formData.camera_username}
                    onChange={handleInputChange}
                    required
                  />
                </div>
                <div className="form-group">
                  <label htmlFor="camera-password">Camera Password:</label>
                  <input
                    type="password"
                    id="camera-password"
                    name="camera_password"
                    value={formData.camera_password}
                    onChange={handleInputChange}
                    required
                  />
                </div>
                <div className="form-group">
                  <label htmlFor="folder-path">Folder Path:</label>
                  <input
                    type="text"
                    id="folder-path"
                    name="folder_path"
                    value={formData.folder_path}
                    onChange={handleInputChange}
                    required
                  />
                </div>
              </div>
            )}

            <div className="form-group">
              <label htmlFor="frequency">Frequency (seconds):</label>
              <input
                type="number"
                id="frequency"
                name="frequency"
                min="1"
                value={formData.frequency}
                onChange={handleInputChange}
                required
              />
            </div>
            <div className="form-group">
              <label htmlFor="lookout-endpoint">Lookout Endpoint:</label>
              <input
                type="url"
                id="lookout-endpoint"
                name="lookout_endpoint"
                value={formData.lookout_endpoint}
                onChange={handleInputChange}
                required
              />
            </div>
            <div className="form-group">
              <label htmlFor="latitude">Latitude:</label>
              <input
                type="number"
                id="latitude"
                name="latitude"
                step="0.000001"
                min="-90"
                max="90"
                value={formData.latitude}
                onChange={handleInputChange}
                required
              />
            </div>
            <div className="form-group">
              <label htmlFor="longitude">Longitude:</label>
              <input
                type="number"
                id="longitude"
                name="longitude"
                step="0.000001"
                min="-180"
                max="180"
                value={formData.longitude}
                onChange={handleInputChange}
                required
              />
            </div>
            <div className="form-actions">
              <button
                type="submit"
                className="btn btn-primary"
                disabled={loading}
              >
                {loading ? 'Saving...' : 'Save'}
              </button>
              <button
                type="button"
                className="btn btn-secondary"
                onClick={onClose}
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  )
}

export default InstanceModal
