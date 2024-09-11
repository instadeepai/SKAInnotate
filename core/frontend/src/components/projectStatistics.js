import React, { useEffect, useState } from 'react';
import { fetchProjectStatistics } from '../services/api';

const ProjectStats = ({ projectId }) => {
  const [stats, setStats] = useState({
    totalTasks: 0,
    completedTasks: 0,
    pendingTasks: 0,
    totalAnnotations: 0,
    accuracyRate: 0.0,
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchStatistics = async () => {
      try {
        const response = await fetchProjectStatistics(projectId);
        setStats(response.data);
      } catch (err) {
        setError('Failed to fetch statistics');
      } finally {
        setLoading(false);
      }
    };

    fetchStatistics();
  }, [projectId]);

  if (loading) return <div>Loading statistics...</div>;
  if (error) return <div>{error}</div>;

  return (
    <div>
      <h3>Project Statistics</h3>
      <ul>
        <li>Total Tasks: {stats.totalTasks}</li>
        <li>Completed Tasks: {stats.completedTasks}</li>
        <li>Pending Tasks: {stats.pendingTasks}</li>
        <li>Total Annotations: {stats.totalAnnotations}</li>
        <li>Accuracy Rate: {stats.accuracyRate.toFixed(2)}%</li>
      </ul>
    </div>
  );
};

export default ProjectStats;
