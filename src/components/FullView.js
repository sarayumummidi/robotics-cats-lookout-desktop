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
      const [imagesResponse, detectionsResponse] = await Promise.all([
        fetch('/api/images'),
        fetch('/api/detections'),
      ])

      if (imagesResponse.ok && detectionsResponse.ok) {
        const imagesData = await imagesResponse.json()
        const detectionsData = await detectionsResponse.json()
        console.log(detectionsData)

        const imagesWithDetections = imagesData.images.map((image) => {
          const detections = detectionsData.detections[image.source] || null
          console.log(`Image: ${image.source}, Detections:`, detections)
          return { ...image, detections }
        })

        setImages(imagesWithDetections || [])
      } else {
        console.error(
          'Failed to fetch data:',
          imagesResponse.status,
          detectionsResponse.status
        )
      }
    } catch (error) {
      console.error('Error fetching data:', error)
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
                            left: `${(detection.left / 1920) * 100}%`,
                            top: `${(detection.top / 1080) * 100}%`,
                            width: `${
                              ((detection.right - detection.left) / 1920) * 100
                            }%`,
                            height: `${
                              ((detection.bottom - detection.top) / 1080) * 100
                            }%`,
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
                      {image.detections.results.length} detection(s) -{' '}
                      {Math.round(image.detections.results[0].score * 100)}%
                      confidence
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
