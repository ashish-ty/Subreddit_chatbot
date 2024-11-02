'use client'

import { useState } from 'react'
import { Button } from "../components/ui/button"
import { Input } from "../components/ui/input"
import { Label } from "../components/ui/label"
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card"
import { AlertCircle, CheckCircle2, Send, MessageCircle, RefreshCw } from 'lucide-react'

interface ChatMessage {
  type: 'user' | 'bot'
  content: string
}

export default function Component() {
  const [subreddit, setSubreddit] = useState('')
  const [apiKey, setApiKey] = useState('')
  const [connectionStatus, setConnectionStatus] = useState<'idle' | 'connecting' | 'success' | 'error'>('idle')
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([])
  const [error, setError] = useState('')

  const handleConnect = async (e: React.FormEvent) => {
    e.preventDefault()
    setConnectionStatus('connecting')
    setError('')
    
    try {
      const response = await fetch('http://localhost:5000/connect', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          subreddit,
          api_key: apiKey
        }),
      })

      const data = await response.json()

      if (data.status === 'success') {
        setConnectionStatus('success')
        setChatMessages([{
          type: 'bot',
          content: `Welcome to r/${subreddit}! How can I assist you today?`
        }])
      } else {
        setConnectionStatus('error')
        setError(data.message || 'Failed to connect to subreddit')
      }
    } catch (err) {
      setConnectionStatus('error')
      setError('Failed to connect to server')
    }
  }

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault()
    const form = e.target as HTMLFormElement
    const messageInput = form.message as HTMLInputElement
    const message = messageInput.value.trim()
    
    if (message) {
      // Add user message immediately
      const userMessage: ChatMessage = {
        type: 'user',
        content: message
      }
      setChatMessages(prev => [...prev, userMessage])
      messageInput.value = ''

      try {
        const response = await fetch('http://localhost:5000/chat', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            message
          }),
        })

        const data = await response.json()

        if (data.status === 'success') {
          const botMessage: ChatMessage = {
            type: 'bot',
            content: data.message
          }
          setChatMessages(prev => [...prev, botMessage])
        } else {
          // Add error message as bot message
          const errorMessage: ChatMessage = {
            type: 'bot',
            content: 'Sorry, I encountered an error processing your request.'
          }
          setChatMessages(prev => [...prev, errorMessage])
        }
      } catch (err) {
        const errorMessage: ChatMessage = {
          type: 'bot',
          content: 'Sorry, I encountered an error connecting to the server.'
        }
        setChatMessages(prev => [...prev, errorMessage])
      }
    }
  }

  const handleTryAnother = () => {
    setConnectionStatus('idle')
    setSubreddit('')
    setApiKey('')
    setChatMessages([])
    setError('')
  }

  return (
    <div className="min-h-screen bg-black text-gray-200 flex flex-col">
      <header className="bg-gray-900 p-4 shadow-lg">
        <div className="container mx-auto flex items-center">
          <MessageCircle className="w-6 h-6 mr-2 text-purple-400" />
          <h1 className="text-xl font-bold text-purple-400">Subreddit Chatbot</h1>
        </div>
      </header>

      <main className="flex-grow container mx-auto p-4 flex flex-col md:flex-row gap-4">
        {connectionStatus !== 'success' && (
          <Card className="md:w-1/3 bg-gray-800 border-gray-700">
            <CardHeader>
              <CardTitle className="text-purple-400">Connect to Subreddit</CardTitle>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleConnect} className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="subreddit" className="text-gray-300">Subreddit Name</Label>
                  <Input
                    id="subreddit"
                    placeholder="Enter subreddit name"
                    value={subreddit}
                    onChange={(e) => setSubreddit(e.target.value)}
                    required
                    className="bg-gray-700 text-gray-200 placeholder-gray-400 border-gray-600"
                  />
                </div>
                <Button type="submit" className="w-full bg-purple-600 text-white hover:bg-purple-700 transition-colors" disabled={connectionStatus === 'connecting'}>
                  {connectionStatus === 'connecting' ? 'Connecting...' : 'Connect'}
                </Button>
              </form>
            </CardContent>
          </Card>
        )}

        <div className={connectionStatus === 'success' ? 'w-full' : 'md:w-2/3'}>
          {connectionStatus === 'success' && (
            <Card className="h-full flex flex-col bg-gray-800 border-gray-700">
              <CardHeader className="flex flex-row items-center justify-between">
                <CardTitle className="flex items-center gap-2 text-purple-400">
                  <CheckCircle2 className="text-green-500" />
                  Connected to r/{subreddit}
                </CardTitle>
                <Button onClick={handleTryAnother} variant="outline" size="sm" className="text-purple-400 border-purple-400 hover:bg-purple-400 hover:text-gray-900">
                  <RefreshCw className="w-4 h-4 mr-2" />
                  Try Another Subreddit
                </Button>
              </CardHeader>
              <CardContent className="flex-grow flex flex-col">
                <div className="flex-grow overflow-y-auto border border-gray-700 rounded p-2 mb-4 bg-gray-900">
                  {chatMessages.map((message, index) => (
                    <div key={index} className={`mb-2 flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}>
                      <div className={`p-2 rounded-lg max-w-[80%] ${message.type === 'user' ? 'bg-purple-900' : 'bg-gray-700'} text-gray-200`}>
                        {message.type === 'user' ? `You: ${message.content}` : `r/${subreddit}: ${message.content}`}
                      </div>
                    </div>
                  ))}
                </div>
                <form onSubmit={handleSendMessage} className="flex gap-2">
                  <Input 
                    name="message" 
                    placeholder="Type your message..." 
                    required 
                    className="flex-grow bg-gray-700 text-gray-200 placeholder-gray-400 border-gray-600" 
                  />
                  <Button type="submit" className="bg-purple-600 text-white hover:bg-purple-700 transition-colors">
                    <Send className="w-4 h-4" />
                  </Button>
                </form>
              </CardContent>
            </Card>
          )}

          {connectionStatus === 'error' && (
            <div className="flex items-center gap-2 text-white bg-red-600 p-4 rounded shadow-lg">
              <AlertCircle />
              <span>{error || 'Connection failed. Please check your inputs and try again.'}</span>
            </div>
          )}
        </div>
      </main>
    </div>
  )
}