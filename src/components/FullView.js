import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'

function FullView() {
  const navigate = useNavigate()
  const [images, setImages] = useState([])
  const [loading, setLoading] = useState(true)

  const handleBack = () => {
    navigate('/')
  }

  const fetchImages = async () => {
    try {
      const response = await fetch('/api/images')
      if (response.ok) {
        const data = await response.json()
        setImages(data.images || [])
      } else {
        console.error('Failed to fetch images:', response.status)
      }
    } catch (error) {
      console.error('Error fetching images:', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchImages()
    // Refresh images every 30 seconds
    const interval = setInterval(fetchImages, 30000)
    return () => clearInterval(interval)
  }, [])

  return (
    <div className="full-view">
      <div className="header-container">
        <button className="logo" onClick={handleBack}>
          <h2>
            {' '}
            <i className="fas fa-tachometer-alt"></i> Lookout Desktop{' '}
          </h2>
        </button>
        <h1>Camera View</h1>
        <button className="back-button" onClick={handleBack}>
          <i className="fas fa-arrow-left"></i> Back
        </button>
      </div>
      <div className="camera-container">
        {loading ? (
          <div className="loading">Loading images...</div>
        ) : images.length > 0 ? (
          <div className="image-grid">
            {images.map((image, index) => (
              <div key={index} className="image-card">
                <div className="image-container">
                  <img
                    src={image.url}
                    alt={`Camera ${image.source}`}
                    className="camera-image"
                    onError={(e) => {
                      e.target.style.display = 'none'
                      console.error(`Failed to load image: ${image.url}`)
                    }}
                  />
                  {image.detections && image.detections.results && (
                    <div className="detection-overlay">
                      {image.detections.results.map((detection, detIndex) => (
                        <div
                          key={detIndex}
                          className="bounding-box"
                          style={{
                            left: `${detection.left}px`,
                            top: `${detection.top}px`,
                            width: `${detection.right - detection.left}px`,
                            height: `${detection.bottom - detection.top}px`,
                          }}
                          title={`Detection (${Math.round(
                            detection.score * 100
                          )}%)`}
                        />
                      ))}
                    </div>
                  )}
                </div>
                <div className="image-info">
                  <div className="image-source">{image.source}</div>
                  <div className="image-time">{image.timestamp}</div>
                  {image.detections && image.detections.results && (
                    <div className="detection-count">
                      {image.detections.results.length} detection(s)
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="no-images">No images available</div>
        )}
      </div>
    </div>
  )
}

export default FullView
