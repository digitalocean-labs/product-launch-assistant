import React, { useState } from 'react';
import { Send, Sparkles, Target, DollarSign, Megaphone } from 'lucide-react';

function ProductForm({ onSubmit }) {
  const [formData, setFormData] = useState({
    product_name: '',
    product_details: '',
    target_market: ''
  });

  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    
    try {
      await onSubmit(formData);
    } catch (error) {
      console.error('Form submission error:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const isFormValid = formData.product_name.trim() && 
                     formData.product_details.trim() && 
                     formData.target_market.trim();

  return (
    <div className="max-w-4xl mx-auto">
      {/* Hero Section */}
      <div className="text-center mb-12">
        <div className="w-20 h-20 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center mx-auto mb-6">
          <Sparkles className="w-10 h-10 text-white" />
        </div>
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          Launch Your Product with AI
        </h1>
        <p className="text-xl text-gray-600 max-w-2xl mx-auto mb-8">
          Get a comprehensive product launch plan including market research, 
          pricing strategy, and marketing content - all powered by artificial intelligence.
        </p>
        
        {/* Feature Highlights */}
        <div className="grid md:grid-cols-3 gap-6 mb-12">
          <div className="bg-white rounded-lg p-6 shadow-sm">
            <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mx-auto mb-4">
              <Target className="w-6 h-6 text-blue-600" />
            </div>
            <h3 className="text-lg font-semibold mb-2">Market Research</h3>
            <p className="text-gray-600 text-sm">AI-powered analysis of competitors and market opportunities</p>
          </div>
          
          <div className="bg-white rounded-lg p-6 shadow-sm">
            <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mx-auto mb-4">
              <DollarSign className="w-6 h-6 text-green-600" />
            </div>
            <h3 className="text-lg font-semibold mb-2">Pricing Strategy</h3>
            <p className="text-gray-600 text-sm">Data-driven pricing recommendations for maximum profitability</p>
          </div>
          
          <div className="bg-white rounded-lg p-6 shadow-sm">
            <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mx-auto mb-4">
              <Megaphone className="w-6 h-6 text-purple-600" />
            </div>
            <h3 className="text-lg font-semibold mb-2">Marketing Content</h3>
            <p className="text-gray-600 text-sm">Ready-to-use social media posts and email campaigns</p>
          </div>
        </div>
      </div>

      {/* Form Section */}
      <div className="max-w-2xl mx-auto">
        <div className="card">
          <div className="text-center mb-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-2">
              Tell Us About Your Product
            </h2>
            <p className="text-gray-600">
              Fill in the details below and our AI will create a comprehensive launch strategy for you.
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label htmlFor="product_name" className="block text-sm font-medium text-gray-700 mb-2">
                Product Name *
              </label>
              <input
                type="text"
                id="product_name"
                name="product_name"
                value={formData.product_name}
                onChange={handleChange}
                placeholder="e.g., EcoSmart Water Bottle"
                className="input-field"
                required
              />
            </div>

            <div>
              <label htmlFor="product_details" className="block text-sm font-medium text-gray-700 mb-2">
                Product Description *
              </label>
              <textarea
                id="product_details"
                name="product_details"
                value={formData.product_details}
                onChange={handleChange}
                placeholder="Describe your product, its features, benefits, and what makes it unique..."
                rows="4"
                className="input-field resize-none"
                required
              />
            </div>

            <div>
              <label htmlFor="target_market" className="block text-sm font-medium text-gray-700 mb-2">
                Target Market *
              </label>
              <input
                type="text"
                id="target_market"
                name="target_market"
                value={formData.target_market}
                onChange={handleChange}
                placeholder="e.g., Health-conscious urban professionals aged 25-40"
                className="input-field"
                required
              />
            </div>

            <div className="pt-4">
              <button
                type="submit"
                disabled={!isFormValid || isSubmitting}
                className={`w-full btn-primary flex items-center justify-center space-x-2 ${
                  !isFormValid || isSubmitting ? 'opacity-50 cursor-not-allowed' : ''
                }`}
              >
                {isSubmitting ? (
                  <>
                    <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                    <span>Submitting...</span>
                  </>
                ) : (
                  <>
                    <Send className="w-5 h-5" />
                    <span>Generate Launch Plan</span>
                  </>
                )}
              </button>
            </div>
          </form>

          <div className="mt-8 p-4 bg-blue-50 rounded-lg">
            <h4 className="font-medium text-blue-900 mb-2">What you'll get:</h4>
            <ul className="text-sm text-blue-800 space-y-1">
              <li>• Comprehensive market research and competitor analysis</li>
              <li>• Optimized product description for e-commerce</li>
              <li>• Data-driven pricing strategy recommendations</li>
              <li>• Step-by-step launch plan with timelines</li>
              <li>• Ready-to-use marketing content and social media posts</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}

export default ProductForm; 