import { useState, useCallback } from 'react';
import { uploadDocument, listDocuments, deleteDocument } from '../services/document_api';

export function useDocuments() {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const uploadDocument_ = useCallback(async (file) => {
    setLoading(true);
    setError(null);
    try {
      const result = await uploadDocument(file);
      await fetchDocuments();
      return result;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchDocuments = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const docs = await listDocuments();
      setDocuments(docs.documents || []);
    } catch (err) {
      setError(err.message);
      setDocuments([]);
    } finally {
      setLoading(false);
    }
  }, []);

  const deleteDocument_ = useCallback(async (docId) => {
    setError(null);
    try {
      await deleteDocument(docId);
      setDocuments((prev) => prev.filter((d) => d.id !== docId));
    } catch (err) {
      setError(err.message);
      throw err;
    }
  }, []);

  return {
    documents,
    loading,
    error,
    uploadDocument: uploadDocument_,
    deleteDocument: deleteDocument_,
    fetchDocuments,
  };
}
