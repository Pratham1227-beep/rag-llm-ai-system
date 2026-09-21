import React from 'react';
import {X, Plus, Trash2 } from 'lucide-react';
import dronalogo from "../../assets/image.png";


const Sidebar = ({ isOpen, onClose, chats, currentChatId, onSelect, onDelete, onNew, backendStatus }) => {
  const handleSelectChat = (id) => {
    onSelect(id);
    // Close sidebar on mobile after selecting a chat
    if (window.innerWidth < 768) {
      onClose();
    }
  };

  return (
    <>
      {/* Sidebar */}
      <div className={`${isOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'} w-80 bg-white border-r border-gray-200 transition-transform duration-300 flex flex-col fixed md:relative h-full z-20`}>
        {/* Header */}
        <div className="bg-emerald-600 p-4 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-white rounded-full flex items-center justify-center">
              <img src={dronalogo}/>
            </div>
            <span className="text-white font-semibold whitespace-nowrap">Enterprise RAG AI System</span>
          </div>
          <button onClick={onClose} className="text-white hover:bg-emerald-700 p-1 rounded md:hidden">
            <X size={20} />
          </button>
        </div>

        {/* Backend Status */}
        <div className={`px-4 py-2 text-xs flex items-center space-x-2 whitespace-nowrap ${
          backendStatus === 'online' ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'
        }`}>
          <div className={`w-2 h-2 rounded-full ${backendStatus === 'online' ? 'bg-green-500' : 'bg-red-500'}`}></div>
          <span>Backend: {backendStatus}</span>
        </div>

        {/* New Chat Button */}
        <div className="p-3 border-b border-gray-200">
          <button onClick={onNew} className="w-full bg-emerald-500 hover:bg-emerald-600 text-white py-2 px-4 rounded-lg flex items-center justify-center space-x-2 transition whitespace-nowrap">
            <Plus size={20} />
            <span>New Chat</span>
          </button>
        </div>

        {/* Chat List */}
        <div className="flex-1 overflow-y-auto">
          {chats.map(chat => (
            <div
              key={chat.id}
              onClick={() => handleSelectChat(chat.id)}
              className={`p-4 cursor-pointer hover:bg-gray-50 border-b border-gray-100 transition group ${
                currentChatId === chat.id ? 'bg-emerald-50' : ''
              }`}
            >
              <div className="flex items-center justify-between">
                <div className="flex-1 min-w-0 pr-2">
                  <div className="font-medium text-gray-800 truncate">{chat.name}</div>
                  <div className="text-xs text-gray-500 truncate">
                    {chat.messages.length > 0 ? chat.messages[chat.messages.length - 1].text : 'No messages'}
                  </div>
                </div>
                <button 
                  onClick={(e) => onDelete(chat.id, e)}
                  className="text-gray-400 hover:text-red-500 opacity-0 group-hover:opacity-100 transition-opacity"
                >
                  <Trash2 size={16} />
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Mobile Overlay */}
      {isOpen && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-50 z-10 md:hidden"
          onClick={onClose}
        />
      )}
    </>
  );
};

export default Sidebar;



