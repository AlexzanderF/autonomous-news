export enum Sentiment {
  POSITIVE = 'POSITIVE',
  NEGATIVE = 'NEGATIVE',
  NEUTRAL = 'NEUTRAL',
  CONTROVERSIAL = 'CONTROVERSIAL'
}

export enum NewsCategory {
  TECH = 'TECHNOLOGY',
  GEOPOLITICS = 'GEOPOLITICS',
  FINANCE = 'FINANCE',
  ENVIRONMENT = 'ENVIRONMENT',
  SPACE = 'SPACE'
}

export interface NewsItem {
  id: string;
  slug: string; // URL-friendly identifier (unique in DB)
  headline: string;
  summary: string;
  category: NewsCategory;
  sentiment: Sentiment;
  sourceCount: number;
  timestamp: string; // ISO string
  imageUrl?: string;
  biasScore: number; // 0 to 100 (0 = left, 100 = right, 50 = center - simplified for UI)
  sentimentScore: number; // 0 to 100
}

export interface ChatMessage {
  role: 'user' | 'model';
  text: string;
  timestamp: number;
}
