// src/hooks/useChatLogic.js
import { useState, useEffect, useCallback } from 'react';
import { chatAPI } from '../services/api';

export const useChatLogic = () => {
  const [chats, setChats] = useState([]);
  const [currentChatId, setCurrentChatId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [backendStatus, setBackendStatus] = useState('checking');
  const [isTyping, setIsTyping] = useState(false);
  const [error, setError] = useState(null);

  // Initialize
  useEffect(() => {
    checkBackendHealth();
    loadChats();
  }, []);

  // Sync with LocalStorage
  useEffect(() => {
    if (chats.length > 0) {
      localStorage.setItem('study_mentor_chats', JSON.stringify(chats));
    }
  }, [chats]);

  const checkBackendHealth = async () => {
    try {
      await chatAPI.healthCheck();
      setBackendStatus('online');
    } catch (err) {
      setBackendStatus('offline');
      setError('Backend is offline.');
    }
  };

  const loadChats = () => {
    const stored = localStorage.getItem('study_mentor_chats');
    if (stored) {
      const parsed = JSON.parse(stored);
      setChats(parsed);
      if (parsed.length > 0) {
        selectChat(parsed[0].id, parsed);
      }
    } else {
      createNewChat();
    }
  };

  const createNewChat = () => {
    const newChat = {
      id: Date.now().toString(),
      name: `Chat ${chats.length + 1}`,
      messages: [],
      uploadedFiles: [],
      timestamp: new Date().toISOString(),
    };
    setChats(prev => [newChat, ...prev]);
    setCurrentChatId(newChat.id);
    setMessages([]);
    setUploadedFiles([]);
  };

  const selectChat = (chatId, chatList = chats) => {
    const chat = chatList.find(c => c.id === chatId);
    if (chat) {
      setCurrentChatId(chatId);
      setMessages(chat.messages);
      setUploadedFiles(chat.uploadedFiles || []);
    }
  };

  const deleteChat = (chatId, e) => {
    e?.stopPropagation();
    const updatedChats = chats.filter(c => c.id !== chatId);
    setChats(updatedChats);
    
    if (currentChatId === chatId) {
      if (updatedChats.length > 0) {
        selectChat(updatedChats[0].id, updatedChats);
      } else {
        createNewChat();
      }
    }
  };

  const handleFileUpload = async (files) => {
    setError(null);
    try {
      const response = await chatAPI.uploadFiles(files);
      const newFiles = response.files.map((file, index) => ({
        id: Date.now() + index,
        name: file.name,
        content: file.content,
        type: file.type,
      }));
      
      const updatedFiles = [...uploadedFiles, ...newFiles];
      setUploadedFiles(updatedFiles);
      updateCurrentChat(messages, updatedFiles);
    } catch (err) {
      setError(`Upload failed: ${err.message}`);
    }
  };

  const removeFile = (fileId) => {
    const updated = uploadedFiles.filter(f => f.id !== fileId);
    setUploadedFiles(updated);
    updateCurrentChat(messages, updated);
  };

  // Helper to update state and chat history simultaneously
  const updateCurrentChat = (msgs, files) => {
    const updatedChats = chats.map(chat => 
      chat.id === currentChatId 
        ? { ...chat, messages: msgs, uploadedFiles: files, timestamp: new Date().toISOString() }
        : chat
    );
    setChats(updatedChats);
  };

  const sendMessage = async (text) => {
    if (!text.trim()) return;
    setError(null);

    const userMessage = {
      id: Date.now().toString(),
      text,
      sender: 'user',
      timestamp: new Date().toISOString(),
    };

    const newMessages = [...messages, userMessage];
    setMessages(newMessages);
    setIsTyping(true);
    updateCurrentChat(newMessages, uploadedFiles);

    try {
      const response = await chatAPI.sendMessage(
        newMessages, 
        uploadedFiles.map(f => ({ name: f.name, content: f.content }))
      );
      
      const aiMessage = {
        id: (Date.now() + 1).toString(),
        text: response.response,
        sender: 'ai',
        timestamp: new Date().toISOString(),
      };

      const finalMessages = [...newMessages, aiMessage];
      setMessages(finalMessages);
      setIsTyping(false);
      updateCurrentChat(finalMessages, uploadedFiles);

    } catch (err) {
      setIsTyping(false);
      setError(err.message);
      // Optional: Add error message to chat stream logic here
    }
  };

  const clearCurrentChat = () => {
    setMessages([]);
    setUploadedFiles([]);
    updateCurrentChat([], []);
  };

  return {
    // State
    chats, currentChatId, messages, uploadedFiles, backendStatus, isTyping, error,
    // Actions
    createNewChat, selectChat, deleteChat, sendMessage, 
    handleFileUpload, removeFile, clearCurrentChat, checkBackendHealth, setError
  };
};