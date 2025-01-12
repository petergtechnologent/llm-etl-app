import React, { useEffect, useState } from 'react';
import { getNotes, uploadFile } from './api';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';

function App() {
  const [notes, setNotes] = useState([]);
  const [selectedFile, setSelectedFile] = useState(null);
  const [chartData, setChartData] = useState([]);

  useEffect(() => {
    fetchNotes();
  }, []);

  const fetchNotes = async () => {
    try {
      const data = await getNotes();
      setNotes(data);

      // Prepare chart data (count by client)
      const clientCountMap = {};
      data.forEach((note) => {
        const client = note.client || 'NOT FOUND';
        clientCountMap[client] = (clientCountMap[client] || 0) + 1;
      });

      // Convert map to array for Recharts
      const processed = Object.keys(clientCountMap).map((client) => ({
        name: client,
        count: clientCountMap[client],
      }));
      setChartData(processed);
    } catch (error) {
      console.error('Error fetching notes', error);
    }
  };

  const handleFileChange = (e) => {
    setSelectedFile(e.target.files[0]);
  };

  const handleUpload = async () => {
    if (!selectedFile) return;
    try {
      await uploadFile(selectedFile);
      setSelectedFile(null);
      fetchNotes();
    } catch (error) {
      console.error('Error uploading file', error);
    }
  };

  return (
    <div className="container my-4">
      <h1 className="text-center mb-4">LLM-Enhanced ETL</h1>

      {/* Upload */}
      <div className="mb-4 p-3 border rounded">
        <h2>Upload a New Notes File</h2>
        <div className="input-group mb-3">
          <input
            className="form-control"
            type="file"
            onChange={handleFileChange}
          />
          <button className="btn btn-primary" onClick={handleUpload}>
            Upload
          </button>
        </div>
      </div>

      {/* Chart */}
      <div className="mb-4 p-3 border rounded">
        <h4>Number of Notes by Client</h4>
        <BarChart width={500} height={300} data={chartData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="name" />
          <YAxis allowDecimals={false} />
          <Tooltip />
          <Legend />
          <Bar dataKey="count" fill="#8884d8" />
        </BarChart>
      </div>

      {/* Notes list */}
      <div className="p-3 border rounded">
        <h2>Parsed Notes from DB</h2>
        <div className="row">
          {notes.map((note) => (
            <div className="col-sm-6 col-md-4 col-lg-3" key={note.id}>
              <div className="card mb-3">
                <div className="card-body">
                  <h5 className="card-title">{note.client}</h5>
                  <p className="card-text">
                    <strong>Target:</strong> {note.target_demographic}<br/>
                    <strong>Platforms:</strong> {note.platforms.join(', ')}<br/>
                    <strong>Notes:</strong> {note.notes}
                  </p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default App;
