import React, { useEffect, useState } from 'react';
import { getNotes, uploadFile } from './api';

function App() {
  const [notes, setNotes] = useState([]);
  const [selectedFile, setSelectedFile] = useState(null);

  useEffect(() => {
    fetchNotes();
  }, []);

  const fetchNotes = async () => {
    try {
      const data = await getNotes();
      setNotes(data);
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
      fetchNotes(); // Refresh list
    } catch (error) {
      console.error('Error uploading file', error);
    }
  };

  return (
    <div style={{ margin: '20px' }}>
      <h1>LLM-Enhanced ETL</h1>
      <div style={{ marginBottom: '20px' }}>
        <h2>Upload a New Notes File</h2>
        <input type="file" onChange={handleFileChange} />
        <button onClick={handleUpload}>Upload</button>
      </div>

      <h2>Parsed Notes from DB</h2>
      <ul>
        {notes.map((note) => (
          <li key={note.id} style={{ marginBottom: '10px' }}>
            <strong>Client:</strong> {note.client} <br />
            <strong>Target:</strong> {note.target_demographic} <br />
            <strong>Platforms:</strong> {note.platforms.join(', ')} <br />
            <strong>Notes:</strong> {note.notes}
          </li>
        ))}
      </ul>
    </div>
  );
}

export default App;
