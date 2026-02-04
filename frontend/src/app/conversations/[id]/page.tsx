"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";

interface Message {
  id: string;
  sender_type: string;
  content: string;
  timestamp: string;
}

interface ConversationDetail {
  id: string;
  scammer_identifier: string;
  status: string;
  scam_type: string;
  detection_confidence: number;
  started_at: string;
  last_activity: string;
  message_count: number;
  duration_seconds: number;
  persona: any;
  messages: Message[];
  intelligence_extracted: {
    upi_id: number;
    bank_account: number;
    phone: number;
    url: number;
    email: number;
  };
  manipulation_tactics: string[];
}

export default function ConversationDetailPage() {
  const params = useParams();
  const conversationId = params.id as string;
  const [conversation, setConversation] = useState<ConversationDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchConversation();
  }, [conversationId]);

  const fetchConversation = async () => {
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const response = await fetch(`${apiUrl}/api/v1/conversations/${conversationId}`);
      
      if (!response.ok) {
        throw new Error("Failed to fetch conversation");
      }
      
      const data = await response.json();
      setConversation(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load conversation");
    } finally {
      setLoading(false);
    }
  };

  const formatDuration = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}m ${secs}s`;
  };

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleString();
  };

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/4 mb-4"></div>
          <div className="h-4 bg-gray-200 rounded w-1/2 mb-8"></div>
          <div className="space-y-4">
            {[1, 2, 3].map((i) => (
              <div key={i} className="h-24 bg-gray-200 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (error || !conversation) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="bg-red-50 border border-red-200 rounded-lg p-6">
          <h2 className="text-xl font-semibold text-red-800 mb-2">Error</h2>
          <p className="text-red-600">{error || "Conversation not found"}</p>
          <Link href="/conversations" className="text-blue-600 hover:text-blue-800 mt-4 inline-block">
            ← Back to Conversations
          </Link>
        </div>
      </div>
    );
  }

  const totalIntelligence = Object.values(conversation.intelligence_extracted).reduce((a, b) => a + b, 0);

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Header */}
      <div className="mb-6">
        <Link href="/conversations" className="text-blue-600 hover:text-blue-800 mb-4 inline-block">
          ← Back to Conversations
        </Link>
        <h1 className="text-3xl font-bold mb-2">Conversation Details</h1>
        <p className="text-gray-600">Scammer: {conversation.scammer_identifier}</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="text-sm text-gray-500 mb-1">Status</div>
          <div className="text-2xl font-bold">
            <span className={`px-3 py-1 rounded-full text-sm ${
              conversation.status === "active" ? "bg-green-100 text-green-800" :
              conversation.status === "completed" ? "bg-blue-100 text-blue-800" :
              "bg-gray-100 text-gray-800"
            }`}>
              {conversation.status}
            </span>
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow p-6">
          <div className="text-sm text-gray-500 mb-1">Scam Type</div>
          <div className="text-xl font-bold capitalize">{conversation.scam_type.replace(/_/g, " ")}</div>
        </div>
        
        <div className="bg-white rounded-lg shadow p-6">
          <div className="text-sm text-gray-500 mb-1">Confidence</div>
          <div className="text-2xl font-bold">{(conversation.detection_confidence * 100).toFixed(0)}%</div>
        </div>
        
        <div className="bg-white rounded-lg shadow p-6">
          <div className="text-sm text-gray-500 mb-1">Duration</div>
          <div className="text-2xl font-bold">{formatDuration(conversation.duration_seconds)}</div>
        </div>
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Messages */}
        <div className="lg:col-span-2">
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-4">Conversation Thread</h2>
            <div className="space-y-4 max-h-[600px] overflow-y-auto">
              {conversation.messages.map((message) => (
                <div
                  key={message.id}
                  className={`p-4 rounded-lg ${
                    message.sender_type === "scammer"
                      ? "bg-red-50 border-l-4 border-red-500"
                      : "bg-blue-50 border-l-4 border-blue-500"
                  }`}
                >
                  <div className="flex justify-between items-start mb-2">
                    <span className={`font-semibold ${
                      message.sender_type === "scammer" ? "text-red-700" : "text-blue-700"
                    }`}>
                      {message.sender_type === "scammer" ? "🚨 Scammer" : "🍯 Honeypot"}
                    </span>
                    <span className="text-xs text-gray-500">
                      {formatTimestamp(message.timestamp)}
                    </span>
                  </div>
                  <p className="text-gray-800 whitespace-pre-wrap">{message.content}</p>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Intelligence Extracted */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-4">Intelligence Extracted</h2>
            <div className="text-3xl font-bold text-green-600 mb-4">{totalIntelligence}</div>
            <div className="space-y-2">
              {Object.entries(conversation.intelligence_extracted).map(([type, count]) => (
                count > 0 && (
                  <div key={type} className="flex justify-between items-center">
                    <span className="text-sm text-gray-600 capitalize">{type.replace(/_/g, " ")}</span>
                    <span className="font-semibold">{count}</span>
                  </div>
                )
              ))}
            </div>
          </div>

          {/* Persona Info */}
          {conversation.persona && (
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-xl font-semibold mb-4">Persona Used</h2>
              <div className="space-y-2">
                <div>
                  <span className="text-sm text-gray-500">Name:</span>
                  <p className="font-medium">{conversation.persona.name}</p>
                </div>
                <div>
                  <span className="text-sm text-gray-500">Age:</span>
                  <p className="font-medium">{conversation.persona.age}</p>
                </div>
                <div>
                  <span className="text-sm text-gray-500">Occupation:</span>
                  <p className="font-medium">{conversation.persona.occupation}</p>
                </div>
              </div>
            </div>
          )}

          {/* Timeline */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-4">Timeline</h2>
            <div className="space-y-3">
              <div>
                <span className="text-sm text-gray-500">Started:</span>
                <p className="font-medium text-sm">{formatTimestamp(conversation.started_at)}</p>
              </div>
              <div>
                <span className="text-sm text-gray-500">Last Activity:</span>
                <p className="font-medium text-sm">{formatTimestamp(conversation.last_activity)}</p>
              </div>
              <div>
                <span className="text-sm text-gray-500">Messages:</span>
                <p className="font-medium">{conversation.message_count}</p>
              </div>
            </div>
          </div>

          {/* Manipulation Tactics */}
          {conversation.manipulation_tactics && conversation.manipulation_tactics.length > 0 && (
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-xl font-semibold mb-4">Manipulation Tactics</h2>
              <div className="space-y-2">
                {conversation.manipulation_tactics.map((tactic, index) => (
                  <div key={index} className="bg-yellow-50 border border-yellow-200 rounded p-2 text-sm">
                    {tactic}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
