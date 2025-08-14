import { useState, useEffect } from 'react';
import axios from 'axios';

export function useInstances() {
  const [instances, setInstances] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchInstances = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await axios.get('/api/instances');
      setInstances(response.data.instances || []);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchInstances();
  }, []);

  return {
    instances,
    loading,
    error,
    refreshInstances: fetchInstances
  };
} 