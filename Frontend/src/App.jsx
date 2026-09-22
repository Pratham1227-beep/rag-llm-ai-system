// src/App.jsx
import React, { useState, useEffect } from 'react';
import { Menu, MoreVertical, Trash2, AlertCircle, X, Paperclip, LogOut } from 'lucide-react';
import Sidebar from './components/Layout/Sidebar';
import MessageList from './components/Chat/MessageList';
import ChatInput from './components/Chat/ChatInput';
import LoginPage from './components/Auth/LoginPage';
import { useChatLogic } from './hooks/useChatLogic';
import { authService } from './services/authService';

function App() {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [currentUser, setCurrentUser] = useState(null);
  const [authChecked, setAuthChecked] = useState(false);

  // On mount, check if user already has a valid token
  useEffect(() => {
    if (authService.isAuthenticated()) {
      setCurrentUser(authService.getUser());
    }
    setAuthChecked(true);
  }, []);

  const handleLogin = (user) => {
    setCurrentUser(user);
  };

  const handleLogout = () => {
    authService.logout();
    setCurrentUser(null);
  };

  // Don't render until we've checked localStorage
  if (!authChecked) return null;

  // Show login page if not authenticated
  if (!currentUser) {
    return <LoginPage onLogin={handleLogin} />;
  }

  return <ChatApp currentUser={currentUser} sidebarOpen={sidebarOpen} setSidebarOpen={setSidebarOpen} onLogout={handleLogout} />;
}

function ChatApp({ currentUser, sidebarOpen, setSidebarOpen, onLogout }) {
  const {
    chats,
    currentChatId,
    messages,
    uploadedFiles,
    backendStatus,
    isTyping,
    error,
    createNewChat,
    selectChat,
    deleteChat,
    sendMessage,
    handleFileUpload,
    removeFile,
    clearCurrentChat,
    checkBackendHealth,
    setError
  } = useChatLogic();

  return (
    <div className="flex h-screen bg-gray-100 overflow-hidden">

      {/* 1. Sidebar Component */}
      <Sidebar
        isOpen={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
        chats={chats}
        currentChatId={currentChatId}
        onSelect={selectChat}
        onDelete={deleteChat}
        onNew={createNewChat}
        backendStatus={backendStatus}
      />

      {/* 2. Main Chat Area */}
      <div className="flex-1 flex flex-col min-w-0">

        {/* Header */}
        <div className="bg-white border-b border-gray-200 px-4 py-3 flex items-center justify-between shadow-sm z-10">
          <div className="flex items-center space-x-3">
            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="text-gray-500 hover:bg-gray-100 p-2 rounded-lg transition"
            >
              <Menu size={20} />
            </button>
            <div>
              <h1 className="font-bold text-gray-800">Enterprise RAG AI System</h1>
              <span className="text-xs text-emerald-600 flex items-center gap-1">
                <span className="w-1.5 h-1.5 bg-emerald-500 rounded-full"></span> Online
              </span>
            </div>
          </div>
          <div className="flex items-center space-x-1">
            {/* User badge */}
            <span className="text-xs text-gray-500 bg-gray-100 px-3 py-1.5 rounded-full mr-1 hidden sm:inline-flex items-center gap-1.5">
              <span className="w-1.5 h-1.5 bg-emerald-400 rounded-full"></span>
              {currentUser?.username}
            </span>
            <button onClick={clearCurrentChat} className="text-gray-400 hover:text-red-500 hover:bg-red-50 p-2 rounded-lg transition" title="Clear Chat">
              <Trash2 size={18} />
            </button>
            <button onClick={checkBackendHealth} className="text-gray-400 hover:text-gray-600 hover:bg-gray-100 p-2 rounded-lg transition" title="Check Connection">
              <MoreVertical size={18} />
            </button>
            <button onClick={onLogout} className="text-gray-400 hover:text-red-500 hover:bg-red-50 p-2 rounded-lg transition" title="Logout" id="logout-btn">
              <LogOut size={18} />
            </button>
          </div>
        </div>

        {/* Error Banner */}
        {error && (
          <div className="bg-red-50 px-4 py-2 flex items-center justify-between border-b border-red-100">
            <div className="flex items-center space-x-2 text-red-700 text-sm">
              <AlertCircle size={16} />
              <span>{error}</span>
            </div>
            <button onClick={() => setError(null)} className="text-red-500 hover:text-red-700">
              <X size={16} />
            </button>
          </div>
        )}

        {/* Uploaded Files Preview Bar */}
        {uploadedFiles.length > 0 && (
          <div className="bg-emerald-50/50 px-4 py-2 border-b border-emerald-100 overflow-x-auto">
            <div className="flex space-x-2">
              {uploadedFiles.map(file => (
                <div key={file.id} className="flex items-center bg-white border border-emerald-200 rounded-md px-2 py-1 shadow-sm">
                  <Paperclip size={12} className="text-emerald-500 mr-2" />
                  <span className="text-xs text-gray-700 max-w-[100px] truncate">{file.name}</span>
                  <button onClick={() => removeFile(file.id)} className="ml-2 text-gray-400 hover:text-red-500">
                    <X size={12} />
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Message List */}
        <MessageList messages={messages} isTyping={isTyping} />

        {/* Input Area */}
        <ChatInput
          onSend={sendMessage}
          onUpload={handleFileUpload}
          disabled={backendStatus === 'offline'}
        />
      </div>
    </div>
  );
}

export default App;