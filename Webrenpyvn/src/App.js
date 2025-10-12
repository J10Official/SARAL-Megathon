import React from 'react';
import VNEngine from './components/VNEngine';
import './App.css';

function App() {
  console.log('🎮 WebRenPy VN Engine - Initializing Application');
  
  return (
    <div className="App">
      <VNEngine />
    </div>
  );
}

export default App;