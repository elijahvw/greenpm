import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { MessageService } from '../services/api';
import { 
  PlusIcon, 
  MagnifyingGlassIcon, 
  ChatBubbleLeftRightIcon,
  PaperAirplaneIcon,
  EllipsisVerticalIcon
} from '@heroicons/react/24/outline';

const Messages: React.FC = () => {
  const { user } = useAuth();
  const [threads, setThreads] = useState<any[]>([]);
  const [selectedThread, setSelectedThread] = useState<any>(null);
  const [messages, setMessages] = useState<any[]>([]);
  const [newMessage, setNewMessage] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    fetchThreads();
  }, []);

  useEffect(() => {
    if (selectedThread) {
      fetchMessages(selectedThread.id);
    }
  }, [selectedThread]);

  const fetchThreads = async () => {
    try {
      setLoading(true);
      const data = await MessageService.getThreads();
      setThreads(data.threads);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch message threads');
    } finally {
      setLoading(false);
    }
  };

  const fetchMessages = async (threadId: string) => {
    try {
      const data = await MessageService.getMessages(threadId);
      setMessages(data.messages);
      
      // Mark thread as read
      await MessageService.markThreadRead(threadId);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch messages');
    }
  };

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newMessage.trim() || !selectedThread) return;

    try {
      await MessageService.sendMessage({
        thread_id: selectedThread.id,
        content: newMessage.trim()
      });
      
      setNewMessage('');
      fetchMessages(selectedThread.id);
      fetchThreads(); // Refresh thread list
    } catch (err: any) {
      setError(err.message || 'Failed to send message');
    }
  };

  const filteredThreads = threads.filter(thread =>
    thread.subject?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    thread.participants?.some((p: any) => 
      p.email?.toLowerCase().includes(searchTerm.toLowerCase())
    )
  );

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-green-500"></div>
      </div>
    );
  }

  return (
    <div className="flex h-screen bg-white">
      {/* Sidebar */}
      <div className="w-1/3 border-r border-gray-200 flex flex-col">
        {/* Header */}
        <div className="p-4 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <h1 className="text-xl font-semibold text-gray-900">Messages</h1>
            <button className="p-2 text-gray-400 hover:text-gray-600">
              <PlusIcon className="h-5 w-5" />
            </button>
          </div>
          
          {/* Search */}
          <div className="mt-4 relative">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <MagnifyingGlassIcon className="h-5 w-5 text-gray-400" />
            </div>
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md leading-5 bg-white placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:ring-1 focus:ring-green-500 focus:border-green-500 sm:text-sm"
              placeholder="Search messages..."
            />
          </div>
        </div>

        {/* Thread List */}
        <div className="flex-1 overflow-y-auto">
          {filteredThreads.length === 0 ? (
            <div className="p-4 text-center text-gray-500">
              {searchTerm ? 'No threads found' : 'No messages yet'}
            </div>
          ) : (
            filteredThreads.map((thread) => (
              <ThreadItem
                key={thread.id}
                thread={thread}
                isSelected={selectedThread?.id === thread.id}
                onClick={() => setSelectedThread(thread)}
                currentUserId={user?.id?.toString()}
              />
            ))
          )}
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        {selectedThread ? (
          <>
            {/* Chat Header */}
            <div className="p-4 border-b border-gray-200">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-lg font-medium text-gray-900">
                    {selectedThread.subject || 'Conversation'}
                  </h2>
                  <p className="text-sm text-gray-500">
                    {selectedThread.participants?.length} participants
                  </p>
                </div>
                <button className="p-2 text-gray-400 hover:text-gray-600">
                  <EllipsisVerticalIcon className="h-5 w-5" />
                </button>
              </div>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              {messages.map((message) => (
                <MessageItem
                  key={message.id}
                  message={message}
                  isOwn={message.sender_id === user?.id}
                />
              ))}
            </div>

            {/* Message Input */}
            <div className="p-4 border-t border-gray-200">
              <form onSubmit={handleSendMessage} className="flex space-x-2">
                <input
                  type="text"
                  value={newMessage}
                  onChange={(e) => setNewMessage(e.target.value)}
                  placeholder="Type a message..."
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-green-500 focus:border-green-500"
                />
                <button
                  type="submit"
                  disabled={!newMessage.trim()}
                  className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <PaperAirplaneIcon className="h-5 w-5" />
                </button>
              </form>
            </div>
          </>
        ) : (
          /* Empty State */
          <div className="flex-1 flex items-center justify-center">
            <div className="text-center">
              <ChatBubbleLeftRightIcon className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-2 text-sm font-medium text-gray-900">No conversation selected</h3>
              <p className="mt-1 text-sm text-gray-500">
                Choose a conversation from the sidebar to start messaging
              </p>
            </div>
          </div>
        )}
      </div>

      {/* Error Toast */}
      {error && (
        <div className="fixed bottom-4 right-4 bg-red-500 text-white px-4 py-2 rounded-md shadow-lg">
          {error}
          <button
            onClick={() => setError(null)}
            className="ml-2 text-red-200 hover:text-white"
          >
            ×
          </button>
        </div>
      )}
    </div>
  );
};

const ThreadItem: React.FC<{
  thread: any;
  isSelected: boolean;
  onClick: () => void;
  currentUserId?: string;
}> = ({ thread, isSelected, onClick, currentUserId }) => {
  const otherParticipants = thread.participants?.filter(
    (p: any) => p.id !== currentUserId
  ) || [];

  return (
    <div
      onClick={onClick}
      className={`p-4 border-b border-gray-100 hover:bg-gray-50 cursor-pointer ${
        isSelected ? 'bg-green-50 border-green-200' : ''
      }`}
    >
      <div className="flex items-center justify-between">
        <div className="flex-1 min-w-0">
          <p className="text-sm font-medium text-gray-900 truncate">
            {thread.subject || 'No subject'}
          </p>
          <p className="text-sm text-gray-500 truncate">
            {otherParticipants.map((p: any) => p.email).join(', ')}
          </p>
        </div>
        <div className="flex-shrink-0 ml-2">
          <p className="text-xs text-gray-500">
            {new Date(thread.last_message_at).toLocaleDateString()}
          </p>
        </div>
      </div>
      
      {thread.last_message && (
        <p className="mt-1 text-sm text-gray-600 truncate">
          {thread.last_message}
        </p>
      )}
    </div>
  );
};

const MessageItem: React.FC<{
  message: any;
  isOwn: boolean;
}> = ({ message, isOwn }) => {
  return (
    <div className={`flex ${isOwn ? 'justify-end' : 'justify-start'}`}>
      <div
        className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
          isOwn
            ? 'bg-green-600 text-white'
            : 'bg-gray-100 text-gray-900'
        }`}
      >
        <p className="text-sm">{message.content}</p>
        <p className={`text-xs mt-1 ${isOwn ? 'text-green-100' : 'text-gray-500'}`}>
          {new Date(message.created_at).toLocaleTimeString()}
        </p>
      </div>
    </div>
  );
};

export default Messages;