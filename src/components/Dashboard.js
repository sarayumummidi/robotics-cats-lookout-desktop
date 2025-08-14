import React, { useState, useEffect } from 'react'
import InstancesTable from './InstancesTable'
import InstanceMap from './InstanceMap'
import InstanceModal from './InstanceModal'
import NotificationSystem from './NotificationSystem'
import { useSocket } from '../hooks/useSocket'
import { useInstances } from '../hooks/useInstances'

function Dashboard() {
  const [showModal, setShowModal] = useState(false)
  const [editingInstance, setEditingInstance] = useState(null)
  const [notifications, setNotifications] = useState([])

  const { instances, loading, error, refreshInstances } = useInstances()
  const { systemStats } = useSocket()

  const showNotification = (message, type = 'info') => {
    const id = Date.now()
    const notification = { id, message, type }
    setNotifications((prev) => [...prev, notification])

    setTimeout(() => {
      setNotifications((prev) => prev.filter((n) => n.id !== id))
    }, 3000)
  }

  const handleAddInstance = () => {
    setEditingInstance(null)
    setShowModal(true)
  }

  const handleEditInstance = (instance) => {
    setEditingInstance(instance)
    setShowModal(true)
  }

  const handleModalClose = () => {
    setShowModal(false)
    setEditingInstance(null)
  }

  const handleInstanceSaved = () => {
    handleModalClose()
    refreshInstances()
    showNotification('Instance saved successfully', 'success')
  }

  const handleInstanceAction = async (instanceName, action) => {
    try {
      const response = await fetch(`/api/instances/${instanceName}/${action}`, {
        method: 'POST',
      })

      if (!response.ok) {
        const error = await response.json()
        showNotification(error.error || `Failed to ${action} instance`, 'error')
      } else {
        showNotification(`Instance ${action}ed successfully`, 'success')
        refreshInstances()
      }
    } catch (error) {
      console.error(`Error ${action}ing instance:`, error)
      showNotification(`Error ${action}ing instance`, 'error')
    }
  }

  const handleDeleteInstance = async (instanceName) => {
    if (window.confirm('Are you sure you want to delete this instance?')) {
      try {
        const response = await fetch(`/api/instances/${instanceName}`, {
          method: 'DELETE',
        })

        if (!response.ok) {
          showNotification('Error deleting instance', 'error')
        } else {
          showNotification('Instance deleted successfully', 'success')
          refreshInstances()
        }
      } catch (error) {
        console.error('Error deleting instance:', error)
        showNotification('Error deleting instance', 'error')
      }
    }
  }

  if (loading) {
    return <div>Loading...</div>
  }

  if (error) {
    return <div>Error: {error}</div>
  }

  return (
    <div className="container">
      <header>
        <h1>
          <i className="fas fa-tachometer-alt"></i> Lookout Desktop
        </h1>
        <div className="header-actions">
          <button className="btn btn-primary" onClick={handleAddInstance}>
            <i className="fas fa-plus"></i> Add Instance
          </button>
        </div>
      </header>

      <InstancesTable
        instances={instances}
        onStart={(name) => handleInstanceAction(name, 'start')}
        onStop={(name) => handleInstanceAction(name, 'stop')}
        onEdit={handleEditInstance}
        onDelete={handleDeleteInstance}
      />

      <InstanceMap instances={instances} />

      {showModal && (
        <InstanceModal
          instance={editingInstance}
          onClose={handleModalClose}
          onSave={handleInstanceSaved}
        />
      )}

      <NotificationSystem notifications={notifications} />
    </div>
  )
}

export default Dashboard
