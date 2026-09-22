import React, { useState } from 'react';
import { Send, Paperclip, Plus, X } from 'lucide-react';

const ChatInput = ({ onSend, onUpload, disabled }) => {
  const [text, setText] = useState('');
  const [showUpload, setShowUpload] = useState(false);

  const handleSubmit = () => {
    if (text.trim() && !disabled) {
      onSend(text);
      setText('');
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const handleFileChange = (e) => {
    const files = Array.from(e.target.files);
    if (files.length) {
      onUpload(files);
      setShowUpload(false);
    }
  };

  return (
    <div className="bg-white border-t border-gray-200 p-4">
      <div className="flex items-end space-x-3 max-w-4xl mx-auto">
        
        {/* Attachment Button */}
        <div className="relative pb-1">
          <button
            onClick={() => setShowUpload(!showUpload)}
            className="text-gray-500 hover:text-emerald-600 p-2 rounded-full hover:bg-gray-100 transition"
          >
            <Paperclip size={22} />
          </button>
          
          {showUpload && (
            <div className="absolute bottom-full left-0 mb-2 bg-white rounded-lg shadow-xl border border-gray-100 p-2 min-w-[150px]">
              <label className="cursor-pointer px-3 py-2 hover:bg-emerald-50 rounded flex items-center space-x-2 text-gray-700 hover:text-emerald-700 transition">
                <Plus size={16} />
                <span className="text-sm font-medium">Upload File</span>
                <input type="file" multiple accept=".pdf,.txt" onChange={handleFileChange} className="hidden" />
              </label>
            </div>
          )}
        </div>

        {/* Text Area */}
        <div className="flex-1 bg-gray-50 border border-gray-200 rounded-2xl focus-within:ring-2 focus-within:ring-emerald-500 focus-within:border-transparent transition">
          <textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            onKeyDown={handleKeyPress}
            placeholder="Type a message..."
            rows={1}
            className="w-full bg-transparent px-4 py-3 focus:outline-none resize-none max-h-32 text-gray-700"
            style={{ minHeight: '48px' }}
          />
        </div>

        {/* Send Button */}
        <button
          onClick={handleSubmit}
          disabled={!text.trim() || disabled}
          className="bg-emerald-600 hover:bg-emerald-700 text-white p-3 rounded-full disabled:opacity-50 disabled:cursor-not-allowed transition shadow-sm mb-1"
        >
          <Send size={20} />
        </button>
      </div>
    </div>
  );
};

export default ChatInput;