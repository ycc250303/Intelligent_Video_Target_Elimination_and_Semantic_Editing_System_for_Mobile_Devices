/**
 * API配置文件 - 统一管理所有API端点
 */

// 获取本地IP地址的函数
export const getLocalIP = (): string => {
  // 在实际部署时，这里应该是你的后端服务器IP
  // 开发时可以是本地IP，生产时应该是服务器IP
  return '192.168.1.100'; // 替换为你的实际IP地址
};

// API基础配置
export const API_CONFIG = {
  BASE_URL: `http://${getLocalIP()}:8000`,
  ENDPOINTS: {
    // 视频相关
    UPLOAD_VIDEO: '/upload-video',
    PROCESS_VIDEO: '/process-video',
    CHECK_FILE: '/check-file',
    HEALTH_CHECK: '/health-check',
    
    // Persona相关
    PERSONAS: '/api/personas',
    PERSONAS_CREATE: '/api/personas/create',
    PERSONAS_DELETE: (id: string) => `/api/personas/${id}/delete`,
    PERSONAS_DETAIL: (id: string) => `/api/personas/${id}`,
    PERSONAS_SEARCH: '/api/personas/search',
    
    // 人格卡相关
    PERSONALITY_CARD: (name: string) => `/api/personality-cards/${name}`,
    GENERATE_FROM_CARD: (name: string) => `/api/personality-cards/${name}/generate-persona`,
  }
};

// 请求配置
export const REQUEST_CONFIG = {
  timeout: 30000, // 30秒超时
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  }
};

// API响应类型定义
export interface ApiResponse<T = any> {
  status: 'success' | 'error';
  data?: T;
  message?: string;
  error?: string;
}

export interface PersonaResponse {
  id: string;
  name: string;
  description: string;
  tag: string;
  type: 'builtin' | 'user';
  downloads?: number;
  likes?: number;
  created_at: string;
  updated_at?: string;
  coverImage: string;
  stylePreset: {
    tone: string;
    subtitle: {
      fontFamily: string;
      fontSize: number;
      color: string;
      position?: string;
      animation?: string;
    };
    cut: {
      pace: string;
      jumpCut: boolean;
      zoomPan?: boolean;
    };
    transitions?: string;
    overlay?: {
      captions: boolean;
      stickers: boolean;
      barrage: boolean;
    };
    bgm: {
      mood: string;
      volume: number;
    };
  };
}

export interface PersonaListResponse {
  builtin: PersonaResponse[];
  user: PersonaResponse[];
}
