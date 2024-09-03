import React, { useState } from 'react';
import axios from 'axios';
import { FaFileExcel, FaTimes } from 'react-icons/fa';

function App() {
  const [selectedMethod, setSelectedMethod] = useState('bom_analysis');
  const [file, setFile] = useState(null);
  const [centralBomId, setCentralBomId] = useState('');
  const [maxDistance, setMaxDistance] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [isHovering, setIsHovering] = useState(false);

  const methods = [
    { id: 'bom_analysis', name: 'BOM Adjacency' },
    // Add other methods here if needed
  ];

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleRemoveFile = () => {
    setFile(null);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);

    const formData = new FormData();
    formData.append('method', selectedMethod);
    formData.append('bom_file', file);
    formData.append('central_bom_id', centralBomId);
    formData.append('max_distance', maxDistance);

    try {
      const response = await axios.post('http://localhost:5000/process', formData, {
        responseType: 'blob',
      });

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `BOM_${centralBomId}_${maxDistance}_edges.xlsx`);
      document.body.appendChild(link);
      link.click();
    } catch (error) {
      console.error('Error:', error);
      setError(error.response?.data?.error || 'An error occurred while processing the file');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex h-screen">
      <div className="w-64 bg-gray-900 text-white p-4">
        <FaFileExcel className="text-4xl mb-4" />
        {methods.map((method) => (
          <button
            key={method.id}
            className={`block w-full text-left p-2 ${
              selectedMethod === method.id ? 'bg-blue-500' : ''
            }`}
            onClick={() => setSelectedMethod(method.id)}
          >
            {method.name}
          </button>
        ))}
      </div>
      <div className="flex-1 p-8 flex flex-col items-center justify-center">
        <div className="w-full max-w-md mb-8">
          <h1 className="text-2xl font-bold text-black mb-4">BOM Adjacency Finder</h1>
          <div className="bg-gray-100 p-4 rounded-lg">
            <ul className="list-disc list-inside">
              <li className="mb-2">Input: CSV file containing BOM relationships, Central BOM ID, and Max Distance</li>
              <li className="mb-2">Process: Identifies precursor and successor BOMs within the specified distance</li>
              <li>Output: Excel file with detailed BOM relationships</li>
            </ul>
          </div>
        </div>
        <form onSubmit={handleSubmit} className="w-full max-w-md">
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-1">Central BOM ID</label>
            <input
              type="text"
              value={centralBomId}
              onChange={(e) => setCentralBomId(e.target.value)}
              className="w-full p-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Enter Central BOM ID"
              required
            />
          </div>
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-1">Max Distance</label>
            <input
              type="number"
              value={maxDistance}
              onChange={(e) => setMaxDistance(e.target.value)}
              className="w-full p-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Enter Max Distance"
              required
            />
          </div>
          <div className="text-center mb-4 mt-8">
            <p className="mb-2">Please upload in CSV/XSLX Format</p>
            <div
              className="border-2 border-dashed border-gray-300 p-8 mt-2 rounded relative"
              onMouseEnter={() => setIsHovering(true)}
              onMouseLeave={() => setIsHovering(false)}
            >
              {file ? (
                <>
                  <FaFileExcel className="text-6xl mx-auto text-green-500" />
                  {isHovering && (
                    <button
                      type="button"
                      onClick={handleRemoveFile}
                      className="absolute top-2 right-2 bg-red-500 text-white rounded-full p-1 hover:bg-red-600 focus:outline-none"
                    >
                      <FaTimes size={12} />
                    </button>
                  )}
                </>
              ) : (
                <FaFileExcel className="text-6xl mx-auto text-gray-300" />
              )}
            </div>
            <input
              type="file"
              onChange={handleFileChange}
              className="hidden"
              id="file-upload"
              accept=".csv,.xlsx"
              required
            />
            <label
              htmlFor="file-upload"
              className="bg-blue-500 text-white px-4 py-2 rounded cursor-pointer inline-block mt-4 hover:bg-blue-600"
            >
              {file ? 'Change File' : 'Upload'}
            </label>
          </div>
          {error && <div className="text-red-500 mb-4">{error}</div>}
          <button
            type="submit"
            className="w-full bg-blue-500 text-white px-4 py-2 rounded mt-4 hover:bg-blue-600"
            disabled={isLoading || !file}
          >
            {isLoading ? 'Processing...' : 'Process'}
          </button>
        </form>
      </div>
    </div>
  );
}

export default App;
