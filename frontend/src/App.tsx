import React from 'react';
import UploadForm from './components/UploadForm';
import StatusList from './components/StatusList';
import SearchBar from './components/SearchBar';

const App: React.FC = () => {
  return (
    <div className="min-h-screen flex flex-col items-center p-6 space-y-8">
      <h1 className="text-4xl font-bold text-primary mb-4">Clinical Intelligence Platform</h1>
      <SearchBar />
      <UploadForm />
      <StatusList />
    </div>
  );
};

export default App;
