import React, { useState, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import mermaid from 'mermaid';
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

  // Initialize Mermaid
  useEffect(() => {
    mermaid.initialize({
      startOnLoad: true,
      theme: 'default',
      securityLevel: 'loose',
    });
  }, []);



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
        {/* Build: 2024-09-02-v3 */}
        
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
      <div className="card bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-100">
        <div className="flex items-center mb-6">
          <div className="w-8 h-8 bg-blue-500 rounded-lg flex items-center justify-center mr-3">
            <FileText className="w-5 h-5 text-white" />
          </div>
          <h2 className="text-2xl font-bold text-blue-900">Product Summary</h2>
        </div>
        <div className="grid md:grid-cols-3 gap-6">
          <div className="bg-white p-4 rounded-lg border border-blue-200 shadow-sm">
            <label className="text-sm font-semibold text-blue-600 uppercase tracking-wide mb-2 block">
              Product Name
            </label>
            <p className="text-lg font-medium text-gray-900 leading-tight">
              {results.product_name}
            </p>
          </div>
          <div className="bg-white p-4 rounded-lg border border-blue-200 shadow-sm">
            <label className="text-sm font-semibold text-blue-600 uppercase tracking-wide mb-2 block">
              Target Market
            </label>
            <p className="text-lg font-medium text-gray-900 leading-tight">
              {results.target_market}
            </p>
          </div>
          <div className="bg-white p-4 rounded-lg border border-blue-200 shadow-sm">
            <label className="text-sm font-semibold text-blue-600 uppercase tracking-wide mb-2 block">
              Product Details
            </label>
            <p className="text-gray-700 leading-relaxed">
              {results.product_details}
            </p>
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="bg-white rounded-xl p-2 border border-gray-200 shadow-sm">
        <div className="flex flex-wrap gap-1">
          {sections.map((section) => {
            const IconComponent = section.icon;
            return (
              <button
                key={section.id}
                onClick={() => setActiveTab(section.id)}
                className={`flex items-center space-x-3 px-6 py-3 rounded-lg font-medium transition-all duration-200 ${
                  activeTab === section.id
                    ? 'bg-gradient-to-r from-primary-500 to-primary-600 text-white shadow-lg transform scale-105'
                    : 'bg-transparent text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                }`}
              >
                <IconComponent className={`w-5 h-5 ${activeTab === section.id ? 'text-white' : 'text-gray-500'}`} />
                <span className="font-semibold">{section.title}</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Content Display */}
      <div className="card">
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center space-x-4">
            <div className={`w-12 h-12 rounded-xl flex items-center justify-center shadow-lg ${colorClasses[activeSection.color]}`}>
              <activeSection.icon className="w-6 h-6" />
            </div>
            <div>
              <h3 className="text-2xl font-bold text-gray-900">{activeSection.title}</h3>
              <p className="text-gray-500 text-sm">AI-generated insights and recommendations</p>
            </div>
          </div>
          
          <button
            onClick={() => copyToClipboard(activeSection.content, activeSection.id)}
            className={`flex items-center space-x-2 px-4 py-2 rounded-lg font-medium transition-all duration-200 ${
              copiedSection === activeSection.id
                ? 'bg-green-100 text-green-700 border border-green-200'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200 border border-gray-200'
            }`}
          >
            {copiedSection === activeSection.id ? (
              <>
                <CheckCircle className="w-4 h-4 text-green-500" />
                <span>Copied!</span>
              </>
            ) : (
              <>
                <Copy className="w-4 h-4" />
                <span>Copy Section</span>
              </>
            )}
          </button>
        </div>

        <div className="prose max-w-none">
          <div className="bg-gradient-to-br from-gray-50 to-white rounded-xl p-8 text-gray-800 leading-relaxed border border-gray-100 shadow-sm">
            <ReactMarkdown 
              components={{
                h1: ({children}) => (
                  <h1 className="text-3xl font-bold text-gray-900 mb-6 pb-3 border-b-2 border-primary-200">
                    {children}
                  </h1>
                ),
                h2: ({children}) => (
                  <h2 className="text-2xl font-semibold text-gray-800 mb-4 mt-8 flex items-center">
                    <div className="w-2 h-2 bg-primary-500 rounded-full mr-3"></div>
                    {children}
                  </h2>
                ),
                h3: ({children}) => (
                  <h3 className="text-xl font-semibold text-gray-700 mb-3 mt-6 flex items-center">
                    <div className="w-1.5 h-1.5 bg-primary-400 rounded-full mr-2"></div>
                    {children}
                  </h3>
                ),
                p: ({children}) => (
                  <p className="mb-4 text-gray-700 leading-7 text-base">
                    {children}
                  </p>
                ),
                ul: ({children}) => (
                  <ul className="list-none ml-0 mb-6 space-y-2">
                    {children}
                  </ul>
                ),
                li: ({children}) => (
                  <li className="flex items-start mb-3 p-3 bg-white rounded-lg border-l-4 border-primary-100 shadow-sm">
                    <div className="w-2 h-2 bg-primary-300 rounded-full mt-2 mr-3 flex-shrink-0"></div>
                    <span className="text-gray-700">{children}</span>
                  </li>
                ),
                ol: ({children}) => (
                  <ol className="list-decimal ml-6 mb-6 space-y-2">
                    {children}
                  </ol>
                ),
                strong: ({children}) => (
                  <strong className="font-semibold text-gray-900 bg-yellow-50 px-1 py-0.5 rounded">
                    {children}
                  </strong>
                ),
                em: ({children}) => (
                  <em className="italic text-gray-600 bg-blue-50 px-1 py-0.5 rounded">
                    {children}
                  </em>
                ),
                code: ({children}) => (
                  <code className="bg-gray-100 text-gray-800 px-2 py-1 rounded text-sm font-mono">
                    {children}
                  </code>
                ),
                blockquote: ({children}) => (
                  <blockquote className="border-l-4 border-primary-300 bg-primary-50 pl-6 py-4 my-6 italic text-gray-700">
                    {children}
                  </blockquote>
                ),
                hr: () => (
                  <hr className="my-8 border-gray-200 border-t-2" />
                ),
                // Custom component for Mermaid diagrams
                pre: ({children}) => {
                  const content = children?.props?.children;
                  if (typeof content === 'string' && content.includes('```mermaid')) {
                    const mermaidCode = content.replace('```mermaid\n', '').replace('\n```', '');
                    const id = `mermaid-${Math.random().toString(36).substr(2, 9)}`;
                    
                    // Render Mermaid diagram after component mounts
                    setTimeout(() => {
                      mermaid.render(id, mermaidCode).then(({ svg }) => {
                        const element = document.getElementById(id);
                        if (element) {
                          element.innerHTML = svg;
                        }
                      }).catch(console.error);
                    }, 100);
                    
                    return (
                      <div className="my-6 p-4 bg-gray-50 rounded-lg border">
                        <div className="text-sm text-gray-500 mb-2">Visual Timeline</div>
                        <div id={id} className="mermaid-diagram"></div>
                      </div>
                    );
                  }
                  return <pre className="bg-gray-100 p-4 rounded-lg overflow-x-auto">{children}</pre>;
                }
              }}
            >
              {activeSection.content}
            </ReactMarkdown>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="card bg-gradient-to-r from-gray-50 to-gray-100 border border-gray-200">
        <div className="flex items-center mb-6">
          <div className="w-8 h-8 bg-gray-600 rounded-lg flex items-center justify-center mr-3">
            <Download className="w-5 h-5 text-white" />
          </div>
          <h3 className="text-xl font-bold text-gray-800">Quick Actions</h3>
        </div>
        <div className="grid md:grid-cols-2 gap-6">
          <button
            onClick={downloadResults}
            className="group flex items-center justify-center space-x-3 p-6 bg-white border-2 border-gray-200 rounded-xl hover:border-primary-300 hover:shadow-lg transition-all duration-200 hover:scale-105"
          >
            <div className="w-10 h-10 bg-primary-100 rounded-lg flex items-center justify-center group-hover:bg-primary-200 transition-colors">
              <Download className="w-5 h-5 text-primary-600" />
            </div>
            <div className="text-left">
              <span className="block font-semibold text-gray-900">Download Full Report</span>
              <span className="text-sm text-gray-500">Get complete launch plan as text file</span>
            </div>
          </button>
          
          <button
            onClick={() => copyToClipboard(activeSection.content, 'all')}
            className="group flex items-center justify-center space-x-3 p-6 bg-white border-2 border-gray-200 rounded-xl hover:border-primary-300 hover:shadow-lg transition-all duration-200 hover:scale-105"
          >
            <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center group-hover:bg-green-200 transition-colors">
              <Copy className="w-5 h-5 text-green-600" />
            </div>
            <div className="text-left">
              <span className="block font-semibold text-gray-900">Copy Current Section</span>
              <span className="text-sm text-gray-500">Copy {activeSection.title} to clipboard</span>
            </div>
          </button>
        </div>
      </div>
    </div>
  );
}

export default ResultsDisplay; 