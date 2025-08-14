import { useState, useEffect, useRef } from 'react'
import io from 'socket.io-client'

export function useSocket() {
  const [systemStats, setSystemStats] = useState({
    cpu: 0,
    network_sent: 0,
    network_recv: 0,
  })
  const socketRef = useRef(null)

  useEffect(() => {
    // Only create socket if it doesn't exist
    if (!socketRef.current) {
      console.log('Creating new socket connection...')
      socketRef.current = io({
        transports: ['websocket', 'polling'],
        upgrade: true,
        rememberUpgrade: true
      })

      socketRef.current.on('connect', () => {
        console.log('Socket connected:', socketRef.current.id)
      })

      socketRef.current.on('disconnect', () => {
        console.log('Socket disconnected')
      })

      socketRef.current.on('system_stats', (stats) => {
        setSystemStats(stats)
      })
    }

    return () => {
      if (socketRef.current) {
        console.log('Cleaning up socket connection...')
        socketRef.current.close()
        socketRef.current = null
      }
    }
  }, [])

  return { socket: socketRef.current, systemStats }
}
