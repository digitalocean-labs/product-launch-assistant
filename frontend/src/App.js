import React, { useState, useEffect } from 'react';
import axios from 'axios';
import Header from './components/Header';
import ProductForm from './components/ProductForm';
import ResultsDisplay from './components/ResultsDisplay';
import { Loader2 } from 'lucide-react';
import './index.css';

// Use environment variable for API URL, fallback to localhost for development
let API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Clean up API URL - remove trailing slash
API_URL = API_URL.replace(/\/$/, '');

function App() {
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Test API connection on component mount
  useEffect(() => {
    const testConnection = async () => {
      try {
        console.log('🔍 Testing API connection to:', `${API_URL}/health`);
        const response = await axios.get(`${API_URL}/health`, {
          timeout: 10000 // 10 second timeout
        });
        console.log('✅ API connection successful:', response.data);
      } catch (err) {
        console.error('❌ API connection failed:', err.message);
        console.error('API URL:', API_URL);
        console.error('Full error:', err);
      }
    };

    testConnection();
  }, []);

  const handleSubmit = async (formData) => {
    setLoading(true);
    setError(null);
    setResults(null);

    try {
      const response = await axios.post(`${API_URL}/launch_assistant`, formData, {
        headers: {
          'Content-Type': 'application/json',
        },
      });
      setResults(response.data);
    } catch (err) {
      console.error('Error:', err);
      setError(
        err.response?.data?.detail || 
        err.message || 
        'An error occurred while generating the launch plan'
      );
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setResults(null);
    setError(null);
    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <Header />
      
      <main className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto">
          
          {/* Show Form (initial state) */}
          {!results && !loading && !error && (
            <ProductForm onSubmit={handleSubmit} loading={loading} />
          )}
          
          {/* Show Loading State */}
          {loading && (
            <div className="text-center py-16">
              <div className="w-16 h-16 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center mx-auto mb-6">
                <Loader2 className="w-8 h-8 text-white animate-spin" />
              </div>
              <h2 className="text-2xl font-semibold text-gray-900 mb-2">
                Generating Your Launch Plan
              </h2>
              <p className="text-gray-600 max-w-md mx-auto">
                Our AI is analyzing your product and creating a comprehensive strategy. 
                This may take a few moments...
              </p>
              <div className="mt-8">
                <div className="bg-white rounded-lg p-6 max-w-md mx-auto shadow-sm">
                  <h4 className="font-medium text-gray-900 mb-3">Creating your:</h4>
                  <ul className="text-sm text-gray-600 space-y-2">
                    <li className="flex items-center">
                      <div className="w-4 h-4 bg-blue-100 rounded mr-3"></div>
                      Market research & competitor analysis
                    </li>
                    <li className="flex items-center">
                      <div className="w-4 h-4 bg-green-100 rounded mr-3"></div>
                      Optimized product description
                    </li>
                    <li className="flex items-center">
                      <div className="w-4 h-4 bg-purple-100 rounded mr-3"></div>
                      Pricing strategy recommendations
                    </li>
                    <li className="flex items-center">
                      <div className="w-4 h-4 bg-orange-100 rounded mr-3"></div>
                      Step-by-step launch plan
                    </li>
                    <li className="flex items-center">
                      <div className="w-4 h-4 bg-pink-100 rounded mr-3"></div>
                      Marketing content & campaigns
                    </li>
                  </ul>
                </div>
              </div>
            </div>
          )}
          
          {/* Show Error State */}
          {error && !loading && (
            <div className="text-center py-16">
              <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-6">
                <svg className="w-8 h-8 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.732-.833-2.464 0L3.34 16.5c-.77.833.192 2.5 1.732 2.5z" />
                </svg>
              </div>
              <h2 className="text-2xl font-semibold text-gray-900 mb-2">
                Oops! Something went wrong
              </h2>
              <p className="text-gray-600 mb-6 max-w-md mx-auto">
                {error}
              </p>
              <div className="space-y-4">
                <button
                  onClick={handleReset}
                  className="btn-primary"
                >
                  Try Again
                </button>
                <p className="text-sm text-gray-500">
                  If the problem persists, please check your internet connection or try again later.
                </p>
              </div>
            </div>
          )}
          
          {/* Show Results */}
          {results && !loading && (
            <ResultsDisplay results={results} onReset={handleReset} />
          )}
          
        </div>
      </main>
    </div>
  );
}

export default App; 