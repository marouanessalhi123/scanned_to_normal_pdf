// developer: Marouan Essalhi
import React, { useCallback, useState } from "react";
import { useDropzone } from "react-dropzone";
import { UploadCloud } from "lucide-react";

const PDFUploader = () => {
  const [file, setFile] = useState(null);
  const [uploadedFile, setUploadedFile] = useState(null);
  const [text, setText] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleFileUpload = useCallback((acceptedFile) => {
    if (acceptedFile) {
      setFile(acceptedFile);
      setError(null);
    }
  }, []);

  const onDrop = useCallback((acceptedFiles) => {
    if (acceptedFiles?.length > 0) {
      handleFileUpload(acceptedFiles[0]);
    }
  }, [handleFileUpload]);

  const handleUpload = async (e) => {
    e.preventDefault();
    
    if (!file) {
      setError("Please select a file first!");
      return;
    }

    setIsLoading(true);
    setError(null);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch("https://pdf-process-backend-6.onrender.com/upload", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`Upload failed: ${response.statusText}`);
      }

      const data = await response.json();
      setUploadedFile(data.file_url);
      setText(data.text);
    } catch (error) {
      setError(`Error uploading file: ${error.message}`);
      console.error("Error uploading file:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { "application/pdf": [".pdf"] },
    multiple: false,
  });

  return (
    <div className="container mt-5">
      <form onSubmit={handleUpload}>
        <div
          {...getRootProps()}
          className="border border-dashed border-secondary rounded p-5 text-center bg-light shadow-sm"
          style={{ cursor: "pointer" }}
        >
          <input {...getInputProps()} />
          <div className="d-flex flex-column align-items-center">
            <UploadCloud size={50} className="text-secondary mb-3" />
            {isDragActive ? (
              <p className="text-primary fw-semibold">Déposez votre fichier ici...</p>
            ) : (
              <p className="text-muted">
                <strong className="text-dark">Choisissez un fichier</strong> ou glissez-le ici.
              </p>
            )}
            {file && <p className="text-success fw-medium">{file.name}</p>}
          </div>
        </div>

        {error && (
          <div className="alert alert-danger mt-3">
            {error}
          </div>
        )}

        <div className="d-flex justify-content-center gap-3 mt-3">
          <button
            type="submit"
            disabled={!file || isLoading}
            className="btn btn-primary"
          >
            <UploadCloud className="me-2" />
            {isLoading ? "Processing..." : "Upload & Process PDF"}
          </button>

          {uploadedFile && (
            <a
              href={`https://pdf-process-backend-6.onrender.com${uploadedFile}`}
              className="btn btn-success"
              download
            >
              Download Processed PDF
            </a>
          )}
        </div>
      </form>

      {uploadedFile && text && (
        <div className="mt-4">
          <h4>Extracted Text:</h4>
          <pre className="bg-dark text-light p-3 rounded">{text}</pre>
        </div>
      )}
    </div>
  );
};

export default PDFUploader;