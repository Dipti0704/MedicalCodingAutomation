import { useState } from "react";
import Header from "../components/Header";
import TextInput from "../components/TextInput";
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

  return (
    <div className="container">
      <Header />

      <div className="card">
        <TextInput text={text} setText={setText} />

        <button onClick={analyze}>
          {loading ? "Analyzing..." : "Analyze Clinical Notes"}
        </button>
      </div>

      {result && (
        <>
          <ResultCard
            title="ICD-10 Diagnosis Codes"
            codes={result.analysis.icd_codes}
          />
          <ResultCard
            title="Procedure Codes"
            codes={result.analysis.cpt_codes}
          />
        </>
      )}
    </div>
  );
}
