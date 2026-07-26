import { useEffect, useState } from 'react';
import axios from 'axios';

interface JobStatus {
  id: string;
  status: string;
  created_at: string;
}

const StatusList: React.FC = () => {
  const [jobs, setJobs] = useState<JobStatus[]>([]);
  const [loading, setLoading] = useState(false);

  const fetchStatus = async () => {
    setLoading(true);
    try {
      const res = await axios.get('/api/status');
      setJobs(res.data);
    } catch (err) {
      console.error('Failed to fetch status', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStatus();
    const interval = setInterval(fetchStatus, 5000); // poll every 5 seconds
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="w-full max-w-2xl space-y-4">
      <h2 className="text-2xl font-semibold text-secondary mb-2">Job Statuses</h2>
      {loading && <p className="text-white">Loading...</p>}
      <div className="grid gap-4 md:grid-cols-2">
        {jobs.map(job => (
          <div
            key={job.id}
            className="p-4 bg-glass backdrop-blur-xs rounded-xl border border-white/20 shadow"
          >
            <p className="font-medium text-primary">ID: {job.id}</p>
            <p className="text-sm">Status: {job.status}</p>
            <p className="text-xs text-white/70">Created: {new Date(job.created_at).toLocaleString()}</p>
          </div>
        ))}
      </div>
    </div>
  );
};

export default StatusList;
