import { useState } from "react";

export default function FileUpload({ onExtracted }) {
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState("");

  const handleFileChange = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setUploading(true);
    setError("");

    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await fetch("http://127.0.0.1:8000/extract-text", {
        method: "POST",
        body: formData,
      });

      const data = await res.json();

      if (!res.ok) {
        throw new Error(data.detail || "Failed to extract text from file");
      }

      onExtracted(data.text);
    } catch (err) {
      setError(err.message);
    } finally {
      setUploading(false);
      e.target.value = "";
    }
  };

  return (
    <div className="file-upload">
      <label className="file-upload-label">
        {uploading ? "Extracting text..." : "Upload PDF or image instead"}
        <input
          type="file"
          accept=".pdf,.png,.jpg,.jpeg,.tiff,.bmp,.webp,.txt"
          onChange={handleFileChange}
          disabled={uploading}
        />
      </label>

      {error && <div className="file-upload-error">{error}</div>}
    </div>
  );
}
