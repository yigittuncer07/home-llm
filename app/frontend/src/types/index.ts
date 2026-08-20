// ----- Domain models (mirroring backend snake_case field names) -----

export interface Chat {
  chat_id: number;
  user_id: number;
  title: string | null;
}

export type MessageRole = 'user' | 'assistant' | 'system';

export interface Message {
  message_id: number;
  chat_id: number;
  model: string;
  tokens: number | null;
  role: MessageRole;
  content: string;
  timestamp: string;
}

export interface UserConfig {
  personalized_prompt: string;
}

// ----- API request / response shapes -----

export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
}

export interface RegisterResponse {
  message: string;
}

// NOTE: backend SendMessageRequest uses `prompt` (not `content`) and requires a `model` field.
export interface SendMessageRequest {
  prompt: string;
  model: string;
}

export interface ChatsResponse {
  chats: Chat[];
}

export interface ChatHistoryResponse {
  chat_id: number;
  messages: Message[];
}

export interface ChatDeleteResponse {
  message: string;
}

// ----- SSE stream payload -----
// Backend publishes: data: {"token": "...", "is_finished": false}
// Terminal event:    data: {"is_finished": true}
export interface StreamEvent {
  token?: string;
  is_finished?: boolean;
}
