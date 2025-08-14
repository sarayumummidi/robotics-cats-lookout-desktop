import React from 'react'

function NotificationSystem({ notifications }) {
  return (
    <div id="notifications">
      {notifications.map((notification) => (
        <div
          key={notification.id}
          className={`notification notification-${notification.type}`}
        >
          {notification.message}
        </div>
      ))}
    </div>
  )
}

export default NotificationSystem
