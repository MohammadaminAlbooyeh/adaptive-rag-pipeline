import { useState, useCallback } from 'react';
import { uploadDocument, listDocuments } from '../services/document_api';

export function useDocuments() {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(false);

  const upload = useCallback(async (file) => {
    setLoading(true);
    const result = await uploadDocument(file);
    setLoading(false);
    return result;
  }, []);

  const fetchDocs = useCallback(async () => {
    const docs = await listDocuments();
    setDocuments(docs);
  }, []);

  return { documents, loading, upload, fetchDocs };
}
