import { useState } from "react";
import Header from "../components/Header";
import TextInput from "../components/TextInput";
import FileUpload from "../components/FileUpload";
import ResultCard from "../components/ResultCard";

export default function Home() {
  const [text, setText] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const analyze = async () => {
    if (!text.trim()) return;

    setLoading(true);

    const res = await fetch("http://127.0.0.1:8000/analyze-text", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text }),
    });

    const data = await res.json();
    setResult(data);
    setLoading(false);
  };

  const decideReview = async (reviewId, status) => {
    const res = await fetch(`http://127.0.0.1:8000/reviews/${reviewId}/decision`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ status }),
    });

    if (!res.ok) return;

    setResult((prev) => {
      const updateCodes = (codes) =>
        codes.map((item) =>
          item.review_id === reviewId ? { ...item, status } : item
        );

      return {
        ...prev,
        analysis: {
          icd_codes: updateCodes(prev.analysis.icd_codes),
          cpt_codes: updateCodes(prev.analysis.cpt_codes),
        },
      };
    });
  };

  return (
    <div className="container">
      <Header />

      <div className="card">
        <TextInput text={text} setText={setText} />
        <FileUpload onExtracted={setText} />

        <button onClick={analyze}>
          {loading ? "Analyzing..." : "Analyze Clinical Notes"}
        </button>
      </div>

      {result && (
        <>
          {result.warnings.length > 0 && (
            <div className="card warnings-card">
              <div className="section-title">Warnings</div>
              {result.warnings.map((warning, index) => (
                <div className="warning" key={index}>
                  {warning}
                </div>
              ))}
            </div>
          )}

          <ResultCard
            title="ICD-10 Diagnosis Codes"
            codes={result.analysis.icd_codes}
            onDecide={decideReview}
          />
          <ResultCard
            title="Procedure Codes"
            codes={result.analysis.cpt_codes}
            onDecide={decideReview}
          />
        </>
      )}
    </div>
  );
}
