import React, { useState } from 'react';
import App from './App';

function Main(props) {
  const [enabled, setEnabled] = useState(true);

  return (
    <div className="App">
      <App/>
    </div>
  );
}

export default Main;
