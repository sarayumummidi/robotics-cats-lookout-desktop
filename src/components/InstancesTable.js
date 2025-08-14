import React from 'react'

function InstancesTable({ instances, onStart, onStop, onEdit, onDelete }) {
  const getInstanceType = (instance) => {
    if (instance.youtube_url) return 'YouTube'
    if (instance.camera_url) return 'Camera'
    return 'Unknown'
  }

  const getInstanceLink = (instance) => {
    if (instance.youtube_url) return instance.youtube_url
    if (instance.camera_url) return instance.camera_url
    return '#'
  }

  const truncateUrl = (url, maxLength = 25) => {
    if (!url) return 'Unknown'
    if (url.length <= maxLength) return url
    return url.substring(0, maxLength) + '...'
  }

  const getDisplayText = (instance) => {
    if (instance.youtube_url) {
      return truncateUrl(instance.youtube_url)
    }
    if (instance.camera_url) {
      return truncateUrl(instance.camera_url)
    }
    return 'Unknown'
  }

  return (
    <div className="instances-section">
      <h2>Instances</h2>
      <div className="table-container">
        <table className="instances-table">
          <thead>
            <tr>
              <th>Status</th>
              <th>Name</th>
              <th>Frequency (s)</th>
              <th>Type</th>
              <th>Link</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {instances.map((instance) => (
              <tr key={instance.name}>
                <td>
                  <span
                    className={`status-badge status-${
                      instance.status || 'stopped'
                    }`}
                  >
                    {(instance.status || 'stopped').charAt(0).toUpperCase() +
                      (instance.status || 'stopped').slice(1)}
                  </span>
                </td>
                <td>{instance.name}</td>
                <td>{instance.frequency}</td>
                <td>{getInstanceType(instance)}</td>
                <td>
                  <a
                    href={getInstanceLink(instance)}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="instance-link"
                    style={{ color: 'inherit' }}
                    title={getInstanceLink(instance)}
                  >
                    <i
                      className={`${
                        getInstanceType(instance).toLowerCase() === 'youtube'
                          ? 'fab fa-youtube'
                          : 'fas fa-video'
                      }`}
                    ></i>
                    {getDisplayText(instance)}
                  </a>
                </td>
                <td>
                  <div className="action-buttons">
                    <button
                      className="btn btn-success btn-sm"
                      onClick={() => onStart(instance.name)}
                      title="Start"
                    >
                      <svg
                        width="12"
                        height="12"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        strokeWidth="2"
                      >
                        <polygon points="5,3 19,12 5,21"></polygon>
                      </svg>
                    </button>
                    <button
                      className="btn btn-warning btn-sm"
                      onClick={() => onStop(instance.name)}
                      title="Stop"
                    >
                      <svg
                        width="12"
                        height="12"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        strokeWidth="2"
                      >
                        <rect x="6" y="6" width="12" height="12"></rect>
                      </svg>
                    </button>
                    <button
                      className="btn btn-info btn-sm"
                      onClick={() => onEdit(instance)}
                      title="Edit"
                    >
                      <svg
                        width="12"
                        height="12"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        strokeWidth="2"
                      >
                        <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                        <path d="m18.5 2.5-3.5 3.5 3.5 3.5 3.5-3.5z"></path>
                      </svg>
                    </button>
                    <button
                      className="btn btn-danger btn-sm"
                      onClick={() => onDelete(instance.name)}
                      title="Delete"
                    >
                      <svg
                        width="12"
                        height="12"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        strokeWidth="2"
                      >
                        <polyline points="3,6 5,6 21,6"></polyline>
                        <path d="m19,6v14a2,2 0 0,1 -2,2H7a2,2 0 0,1 -2,-2V6m3,0V4a2,2 0 0,1 2,-2h4a2,2 0 0,1 2,2v2"></path>
                      </svg>
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

export default InstancesTable
