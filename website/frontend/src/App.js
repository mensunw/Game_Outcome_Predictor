import React, { useEffect, useState } from 'react';

function App() {
  const [backendMessage, setBackendMessage] = useState("");

  useEffect(() => {
    fetch("http://127.0.0.1:8000/test/")
      .then((response) => response.json())
      .then((data) => setBackendMessage(data.message))
      .catch((error) => console.error("Error fetching from backend:", error));
  }, []);

  return (
    <div className="App">
      <header className="App-header">
        <h1>React & Django Test</h1>
        <p>Backend Message: {backendMessage}</p>
      </header>
    </div>
  );
}

export default App;