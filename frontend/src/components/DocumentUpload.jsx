import React, { useState } from 'react';

function DocumentUpload() {
  const [file, setFile] = useState(null);

  const handleSubmit = (e) => {
    e.preventDefault();
  };

  return (
    <form className="document-upload" onSubmit={handleSubmit}>
      <input type="file" onChange={(e) => setFile(e.target.files[0])} />
      <button type="submit">Upload</button>
    </form>
  );
}

export default DocumentUpload;
