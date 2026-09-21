const STORAGE_KEY = 'study_mentor_chats';

export const localStorageAPI = {
  // Get all chats
  getChats: () => {
    try {
      const data = localStorage.getItem(STORAGE_KEY);
      return data ? JSON.parse(data) : [];
    } catch (error) {
      console.error('Error reading from localStorage:', error);
      return [];
    }
  },

  // Save all chats
  saveChats: (chats) => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(chats));
      return true;
    } catch (error) {
      console.error('Error saving to localStorage:', error);
      return false;
    }
  },

  // Clear all chats
  clearChats: () => {
    try {
      localStorage.removeItem(STORAGE_KEY);
      return true;
    } catch (error) {
      console.error('Error clearing localStorage:', error);
      return false;
    }
  },

  // Get single chat by ID
  getChat: (chatId) => {
    const chats = localStorageAPI.getChats();
    return chats.find(chat => chat.id === chatId);
  },

  // Update single chat
  updateChat: (chatId, updatedData) => {
    const chats = localStorageAPI.getChats();
    const updatedChats = chats.map(chat =>
      chat.id === chatId ? { ...chat, ...updatedData } : chat
    );
    return localStorageAPI.saveChats(updatedChats);
  },

  // Delete chat
  deleteChat: (chatId) => {
    const chats = localStorageAPI.getChats();
    const filteredChats = chats.filter(chat => chat.id !== chatId);
    return localStorageAPI.saveChats(filteredChats);
  }
};