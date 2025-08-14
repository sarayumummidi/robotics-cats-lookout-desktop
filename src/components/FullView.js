import React from 'react'
import { useNavigate } from 'react-router-dom'

function FullView() {
    const navigate = useNavigate()
    const handleBack = () => {
        navigate('/')
    }
  return (
    <div className="full-view">
      <div className="header-container">
        <button className="logo" onClick={handleBack}>
            <h2> <i className="fas fa-tachometer-alt"></i> Lookout Desktop </h2>
        </button>
        <h1>Camera View</h1>
        <button className="back-button" onClick={handleBack}>
            <i className="fas fa-arrow-left"></i> Back
        </button>
      </div>
      <div className="camera-container">
      </div>
    </div>
  )
}

export default FullView