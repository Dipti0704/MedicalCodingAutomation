export default function TextInput({ text, setText }) {
  return (
    <>
      <label>Clinical Notes</label>
      <textarea
        placeholder="Example: Patient with old myocardial infarction and chest pain..."
        value={text}
        onChange={(e) => setText(e.target.value)}
      />
    </>
  );
}
