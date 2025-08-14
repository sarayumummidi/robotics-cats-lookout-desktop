import React, { useEffect, useRef } from 'react'
import L from 'leaflet'

function InstanceMap({ instances }) {
  const mapRef = useRef(null)
  const mapInstanceRef = useRef(null)
  const markersRef = useRef({})

  useEffect(() => {
    if (!mapRef.current) return

    // Initialize map
    if (!mapInstanceRef.current) {
      mapInstanceRef.current = L.map(mapRef.current, {
        attributionControl: false,
      }).setView([39.8283, -98.5795], 4)

      L.tileLayer(
        'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png',
        {
          maxZoom: 20,
          attribution:
            '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
        }
      ).addTo(mapInstanceRef.current)
    }

    // Clear existing markers
    Object.values(markersRef.current).forEach((marker) => {
      mapInstanceRef.current.removeLayer(marker)
    })
    markersRef.current = {}

    // Add markers for each instance
    instances.forEach((instance) => {
      if (!instance.latitude || !instance.longitude) return

      const iconColor = instance.status === 'running' ? '#16825d' : '#a31515'
      const iconHtml = `<div style="width: 16px; height: 16px; background: ${iconColor}; border: 2px solid #ffffff; border-radius: 50%; box-shadow: 0 2px 4px rgba(0,0,0,0.3);"></div>`

      const customIcon = L.divIcon({
        html: iconHtml,
        className: 'custom-marker',
        iconSize: [20, 20],
        iconAnchor: [10, 10],
      })

      const marker = L.marker([instance.latitude, instance.longitude], {
        icon: customIcon,
        title: `Instance ${instance.name}`,
      }).addTo(mapInstanceRef.current)

      const extractYouTubeId = (url) => {
        if (!url) return 'Unknown'
        const match = url.match(
          /(?:youtube\.com\/watch\?v=|youtu\.be\/)([^&\n?#]+)/
        )
        return match ? match[1].substring(0, 11) : 'Unknown'
      }

      const getInstanceType = (instance) => {
        if (instance.youtube_url) return 'YouTube'
        if (instance.camera_url) return 'Camera'
        return 'Unknown'
      }

      const videoId = extractYouTubeId(
        instance.youtube_url || instance.camera_url
      )
      const popupContent = `
        <div class="map-popup">
          <div class="popup-header">
            <strong>${instance.name}</strong>
            <span class="status-badge status-${
              instance.status || 'stopped'
            }">${(instance.status || 'stopped').toUpperCase()}</span>
          </div>
          <div class="popup-content">
            <div class="popup-row">
              <span class="popup-label">Frequency:</span>
              <span class="popup-value">${instance.frequency}s</span>
            </div>
            <div class="popup-row">
              <span class="popup-label">Type:</span>
              <span class="popup-value">${getInstanceType(instance)}</span>
            </div>
            <div class="popup-row">
              <span class="popup-label">Location:</span>
              <span class="popup-value">${instance.latitude.toFixed(
                4
              )}, ${instance.longitude.toFixed(4)}</span>
            </div>
          </div>
        </div>
      `

      marker.bindPopup(popupContent, { className: 'custom-popup' })
      markersRef.current[instance.name] = marker
    })

    return () => {
      if (mapInstanceRef.current) {
        mapInstanceRef.current.remove()
        mapInstanceRef.current = null
      }
    }
  }, [instances])

  return (
    <div className="map-section">
      <h2>Instance Locations</h2>
      <div className="map-container" ref={mapRef}></div>
    </div>
  )
}

export default InstanceMap
