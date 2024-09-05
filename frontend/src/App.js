import React, { useState, useRef } from 'react';
import axios from 'axios';
import { FaFileExcel, FaTimes } from 'react-icons/fa';

function App() {
  const [selectedMethod, setSelectedMethod] = useState('bom_analysis');
  const [files, setFiles] = useState({});
  const [centralBomId, setCentralBomId] = useState('');
  const [maxDistance, setMaxDistance] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const fileInputRefs = useRef({});

  const methods = [
    {
      id: 'bom_analysis',
      name: 'BOM Adjacency',
      fileInputs: ['bom_file'],
      description: [
        "Input: bom_graph file in CSV format, Central BOM ID, and Max Distance",
        "Process: Identifies all precursor and successor BOMs within the specified distance to the central BOM ID",
        "Output: A CSV with all BOM IDs satisfying this relationship"
      ]
    },
    {
      id: 'bom_graph',
      name: 'BOM Graph Generator',
      fileInputs: ['bom_details_list', 'bom_parents_list'],
      description: [
        "Input: Two Excel files - Agility BOM Details List and Agility BOM Parents List",
        "Process: Combines and processes the information from both files to form a relationship based BOM graph",
        "Output: A CSV file with with BOM relationships that can be used to generate a graph in graphia"
      ]
    },
  ];


  const handleFileChange = (e, fileType) => {
    setFiles(prev => ({...prev, [fileType]: e.target.files[0]}));
  };

  const handleRemoveFile = (fileType) => {
    setFiles(prev => {
      const newFiles = {...prev};
      delete newFiles[fileType];
      return newFiles;
    });
    if (fileInputRefs.current[fileType]) {
      fileInputRefs.current[fileType].value = '';
    }
  };

  const handleUploadClick = (fileType) => {
    if (fileInputRefs.current[fileType]) {
      fileInputRefs.current[fileType].click();
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);

    const formData = new FormData();
    formData.append('method', selectedMethod);

    methods.find(m => m.id === selectedMethod).fileInputs.forEach(fileType => {
      if (files[fileType]) {
        formData.append(fileType, files[fileType]);
      }
    });

    if (selectedMethod === 'bom_analysis') {
      formData.append('central_bom_id', centralBomId);
      formData.append('max_distance', maxDistance);
    }

    try {
      const response = await axios.post('http://localhost:5000/process', formData, {
        responseType: 'blob',
      });

      // Get the filename from the Content-Disposition header if Flask sends it
      const contentDisposition = response.headers['content-disposition'];
      let filename = '';

      // Extract the filename from the Content-Disposition header
      if (contentDisposition && contentDisposition.includes('filename=')) {
        filename = contentDisposition
          .split('filename=')[1]
          .split(';')[0]
          .replace(/['"]/g, '');  // Remove any quotes around the filename
      }

      // Create a download link
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;

      // Use the filename from the response, or fall back to a default if missing
      link.setAttribute('download', filename || 'result_file.csv');

      document.body.appendChild(link);
      link.click();
      link.remove();  // Clean up after click
    } catch (error) {
      console.error('Download failed', error);
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
        <form onSubmit={handleSubmit} className="w-full max-w-2xl">
          <h2 className="text-2xl font-bold mb-4">{methods.find(m => m.id === selectedMethod).name}</h2>
          <div className="bg-gray-100 p-4 rounded-lg mb-6">
            <ul className="list-disc list-inside">
              {methods.find(m => m.id === selectedMethod).description.map((item, index) => (
                <li key={index} className="mb-2">{item}</li>
              ))}
            </ul>
          </div>
          {selectedMethod === 'bom_analysis' && (
            <>
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
            </>
          )}
          <div className="flex flex-wrap -mx-2">
            {methods.find(m => m.id === selectedMethod).fileInputs.map((fileType) => (
              <div key={fileType} className="mb-4 px-2" style={{width: `${100 / methods.find(m => m.id === selectedMethod).fileInputs.length}%`}}>
                <p className="mb-2 text-sm font-medium text-gray-700">{fileType.replace('_', ' ').split(' ').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ')}</p>
                <div
                  className="border-2 border-dashed border-gray-300 p-4 rounded relative flex flex-col items-center justify-center"
                  style={{height: '150px'}}
                >
                  {files[fileType] ? (
                    <>
                      <FaFileExcel className="text-4xl mx-auto text-green-500" />
                      <p className="text-sm text-center mt-2 truncate">{files[fileType].name}</p>
                      <button
                        type="button"
                        onClick={() => handleRemoveFile(fileType)}
                        className="absolute top-1 right-1 bg-red-500 text-white rounded-full p-1 hover:bg-red-600 focus:outline-none"
                      >
                        <FaTimes size={10} />
                      </button>
                    </>
                  ) : (
                    <FaFileExcel className="text-4xl text-gray-300" />
                  )}
                </div>
                <input
                  type="file"
                  onChange={(e) => handleFileChange(e, fileType)}
                  className="hidden"
                  id={`file-upload-${fileType}`}
                  accept=".csv,.xlsx,.xls"
                  ref={el => fileInputRefs.current[fileType] = el}
                />
                <button
                  type="button"
                  onClick={() => handleUploadClick(fileType)}
                  className="w-full bg-green-600 text-white px-4 py-2 rounded cursor-pointer mt-2 hover:bg-green-700 text-sm"
                >
                  {files[fileType] ? 'Change File' : 'Upload'}
                </button>
              </div>
            ))}
          </div>
          {error && <div className="text-red-500 mb-4">{error}</div>}
          <button
            type="submit"
            className="w-full bg-blue-500 text-white px-4 py-2 rounded mt-4 hover:bg-blue-600"
            disabled={isLoading || !Object.keys(files).length}
          >
            {isLoading ? 'Processing...' : 'Process'}
          </button>
        </form>
      </div>
    </div>
  );
}

export default App;
