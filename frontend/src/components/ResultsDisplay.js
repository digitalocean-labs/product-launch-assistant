import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import { 
  Target, 
  FileText, 
  DollarSign, 
  Calendar, 
  Megaphone, 
  Copy, 
  Download, 
  ArrowLeft,
  CheckCircle
} from 'lucide-react';

function ResultsDisplay({ results, onReset }) {
  const [copiedSection, setCopiedSection] = useState(null);
  const [activeTab, setActiveTab] = useState('market_research');

  const sections = [
    {
      id: 'market_research',
      title: 'Market Research',
      icon: Target,
      color: 'blue',
      content: results.market_research
    },
    {
      id: 'product_description',
      title: 'Product Description',
      icon: FileText,
      color: 'green',
      content: results.product_description
    },
    {
      id: 'pricing_strategy',
      title: 'Pricing Strategy',
      icon: DollarSign,
      color: 'purple',
      content: results.pricing_strategy
    },
    {
      id: 'launch_plan',
      title: 'Launch Plan',
      icon: Calendar,
      color: 'orange',
      content: results.launch_plan
    },
    {
      id: 'marketing_content',
      title: 'Marketing Content',
      icon: Megaphone,
      color: 'pink',
      content: results.marketing_content
    }
  ];

  const colorClasses = {
    blue: 'bg-blue-100 text-blue-600',
    green: 'bg-green-100 text-green-600',
    purple: 'bg-purple-100 text-purple-600',
    orange: 'bg-orange-100 text-orange-600',
    pink: 'bg-pink-100 text-pink-600'
  };

  const copyToClipboard = async (text, sectionId) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedSection(sectionId);
      setTimeout(() => setCopiedSection(null), 2000);
    } catch (err) {
      console.error('Failed to copy text: ', err);
    }
  };

  const downloadResults = () => {
    const content = sections.map(section => 
      `# ${section.title}\n\n${section.content}\n\n---\n\n`
    ).join('');
    
    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${results.product_name.replace(/\s+/g, '_')}_launch_plan.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const activeSection = sections.find(section => section.id === activeTab);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Launch Plan for {results.product_name}
        </h1>
        <p className="text-gray-600 mb-6">
          Your comprehensive AI-generated product launch strategy
        </p>
        
        <div className="flex flex-wrap justify-center gap-4 mb-8">
          <button
            onClick={onReset}
            className="btn-secondary flex items-center space-x-2"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>Create New Plan</span>
          </button>
          
          <button
            onClick={downloadResults}
            className="btn-primary flex items-center space-x-2"
          >
            <Download className="w-4 h-4" />
            <span>Download Report</span>
          </button>
        </div>
      </div>

      {/* Product Summary */}
      <div className="card">
        <h2 className="text-xl font-semibold mb-4">Product Summary</h2>
        <div className="grid md:grid-cols-3 gap-4">
          <div>
            <label className="text-sm font-medium text-gray-500">Product Name</label>
            <p className="text-gray-900">{results.product_name}</p>
          </div>
          <div>
            <label className="text-sm font-medium text-gray-500">Target Market</label>
            <p className="text-gray-900">{results.target_market}</p>
          </div>
          <div>
            <label className="text-sm font-medium text-gray-500">Product Details</label>
            <p className="text-gray-900 line-clamp-2">{results.product_details}</p>
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="flex flex-wrap gap-2">
        {sections.map((section) => {
          const IconComponent = section.icon;
          return (
            <button
              key={section.id}
              onClick={() => setActiveTab(section.id)}
              className={`flex items-center space-x-2 px-4 py-2 rounded-lg font-medium transition-colors ${
                activeTab === section.id
                  ? 'bg-primary-100 text-primary-700 border border-primary-200'
                  : 'bg-white text-gray-600 hover:bg-gray-50 border border-gray-200'
              }`}
            >
              <IconComponent className="w-4 h-4" />
              <span>{section.title}</span>
            </button>
          );
        })}
      </div>

      {/* Content Display */}
      <div className="card">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center space-x-3">
            <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${colorClasses[activeSection.color]}`}>
              <activeSection.icon className="w-5 h-5" />
            </div>
            <h3 className="text-xl font-semibold">{activeSection.title}</h3>
          </div>
          
          <button
            onClick={() => copyToClipboard(activeSection.content, activeSection.id)}
            className="flex items-center space-x-2 text-sm text-gray-600 hover:text-gray-900 transition-colors"
          >
            {copiedSection === activeSection.id ? (
              <>
                <CheckCircle className="w-4 h-4 text-green-500" />
                <span>Copied!</span>
              </>
            ) : (
              <>
                <Copy className="w-4 h-4" />
                <span>Copy</span>
              </>
            )}
          </button>
        </div>

        <div className="prose max-w-none">
          <div className="bg-gray-50 rounded-lg p-6 text-gray-800 leading-relaxed prose prose-gray max-w-none">
            <ReactMarkdown 
              components={{
                h1: ({children}) => <h1 className="text-2xl font-bold text-gray-900 mb-4">{children}</h1>,
                h2: ({children}) => <h2 className="text-xl font-semibold text-gray-900 mb-3 mt-6">{children}</h2>,
                h3: ({children}) => <h3 className="text-lg font-semibold text-gray-900 mb-2 mt-4">{children}</h3>,
                p: ({children}) => <p className="mb-2">{children}</p>,
                ul: ({children}) => <ul className="list-disc ml-6 mb-4">{children}</ul>,
                li: ({children}) => <li className="mb-1">{children}</li>,
                strong: ({children}) => <strong className="font-semibold">{children}</strong>,
              }}
            >
              {activeSection.content}
            </ReactMarkdown>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="card">
        <h3 className="text-lg font-semibold mb-4">Quick Actions</h3>
        <div className="grid md:grid-cols-2 gap-4">
          <button
            onClick={downloadResults}
            className="flex items-center justify-center space-x-2 p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
          >
            <Download className="w-5 h-5 text-gray-600" />
            <span>Download Full Report</span>
          </button>
          
          <button
            onClick={() => copyToClipboard(activeSection.content, 'all')}
            className="flex items-center justify-center space-x-2 p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
          >
            <Copy className="w-5 h-5 text-gray-600" />
            <span>Copy Current Section</span>
          </button>
        </div>
      </div>
    </div>
  );
}

export default ResultsDisplay; 