import React, { useEffect, useState } from 'react';
import { getNotes, uploadFile } from './api';

// Recharts imports:
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';

function App() {
  const [notes, setNotes] = useState([]);
  const [selectedFile, setSelectedFile] = useState(null);

  // Data for the stacked bar chart
  const [chartData, setChartData] = useState([]);
  // We'll store a list of unique platforms for dynamic <Bar> generation
  const [allPlatforms, setAllPlatforms] = useState([]);

  useEffect(() => {
    fetchNotes();
  }, []);

  const fetchNotes = async () => {
    try {
      const data = await getNotes();
      setNotes(data);

      // Build the stacked bar chart data from the notes
      const { finalData, uniquePlatforms } = buildStackedChartData(data);
      setChartData(finalData);
      setAllPlatforms(uniquePlatforms);
    } catch (error) {
      console.error('Error fetching notes:', error);
    }
  };

  // Build a data structure for a stacked bar chart of platform usage by client
  const buildStackedChartData = (notesArray) => {
    /*
      We want an array like:
      [
        { name: 'Client A', Facebook: 2, TikTok: 1, ... },
        { name: 'Client B', Facebook: 0, TikTok: 3, ... },
        ...
      ]
      Also, we want a set/list of unique platform names to generate <Bar> components.
    */

    // 1. Create a nested object: client -> platform -> count
    const clientPlatformMap = {};

    // 2. Collect all platforms in a set to track what's used across all clients
    const platformSet = new Set();

    notesArray.forEach((note) => {
      const clientName = note.client || 'NOT FOUND';
      const platforms = note.platforms || [];

      if (!clientPlatformMap[clientName]) {
        clientPlatformMap[clientName] = {};
      }

      platforms.forEach((p) => {
        // Trim or standardize platform name if needed
        const platformName = p.trim() || 'NOT FOUND';
        platformSet.add(platformName);
        // Increment the count
        if (!clientPlatformMap[clientName][platformName]) {
          clientPlatformMap[clientName][platformName] = 0;
        }
        clientPlatformMap[clientName][platformName] += 1;
      });
    });

    // 3. Build the final data array
    const finalData = Object.keys(clientPlatformMap).map((clientName) => {
      const row = { name: clientName };
      // For each known platform, fill in the count or zero
      platformSet.forEach((plat) => {
        row[plat] = clientPlatformMap[clientName][plat] || 0;
      });
      return row;
    });

    return {
      finalData,
      uniquePlatforms: Array.from(platformSet)
    };
  };

  const handleFileChange = (e) => {
    setSelectedFile(e.target.files[0]);
  };

  const handleUpload = async () => {
    if (!selectedFile) return;
    try {
      await uploadFile(selectedFile);
      setSelectedFile(null);
      fetchNotes(); // Refresh data after upload
    } catch (error) {
      console.error('Error uploading file:', error);
    }
  };

  return (
    <div className="container my-4">
      <h1 className="text-center mb-4">LLM-Enhanced ETL</h1>

      {/* Upload Section */}
      <div className="card mb-4">
        <div className="card-body">
          <h5>Upload a New Notes File</h5>
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
      </div>

      {/* Stacked Bar Chart for platform usage by client */}
      <div className="card mb-4">
        <div className="card-body">
          <h5>Platform Usage by Client (Stacked Bar Chart)</h5>
          <div style={{ width: '100%', height: 400 }}>
            <ResponsiveContainer>
              <BarChart data={chartData} margin={{ top: 10, right: 30, left: 0, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis allowDecimals={false} />
                <Tooltip />
                <Legend />
                {/* Dynamically create a <Bar> for each unique platform */}
                {allPlatforms.map((platform, idx) => (
                  <Bar
                    key={platform}
                    dataKey={platform}
                    stackId="platforms"
                    fill={colorPicker(idx)}
                  />
                ))}
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Existing Notes List (optional) */}
      <div className="card mb-4">
        <div className="card-body">
          <h5>All Parsed Notes from DB</h5>
          <div className="row">
            {notes.map((note) => (
              <div className="col-sm-6 col-md-4 col-lg-3" key={note.id}>
                <div className="card mb-3">
                  <div className="card-body">
                    <h6 className="card-title">
                      <strong>Client:</strong> {note.client}
                    </h6>
                    <p className="card-text" style={{ fontSize: '0.9rem' }}>
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
    </div>
  );
}

// Simple function to assign a color to each platform bar. 
// You can expand this with a color palette or random generator.
function colorPicker(index) {
  const colors = [
    '#8884d8', '#82ca9d', '#ffc658', '#d0ed57', '#a4de6c',
    '#f07fff', '#ff7f7f', '#3fbaff', '#c387ff', '#ffa600'
  ];
  return colors[index % colors.length];
}

export default App;
