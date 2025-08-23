/**
 * Persona API客户端
 * 与后端Persona API进行通信的客户端
 */

import { API_CONFIG } from '../utils/config';

export interface PersonaCategory {
  value: string;
  label: {
    zh: string;
    en: string;
  };
}

export interface PersonaStats {
  usage_count: number;
  download_count: number;
  rating_average: number;
  rating_count: number;
  share_count: number;
  view_count: number;
}

export interface PersonaData {
  id: string;
  name: string;
  description: string;
  category: string;
  author: string;
  status: string;
  is_public: boolean;
  is_featured: boolean;
  tags: string[];
  created_at: string;
  updated_at: string;
  version: string;
  stats: PersonaStats;
  style_preferences?: {
    fast_paced: number;
    slow_paced: number;
    dynamic: number;
    consistent: number;
    close_up_frequency: number;
    wide_shot_frequency: number;
    transition_smoothness: number;
    cut_frequency: number;
    narrative_style: number;
    emotional_intensity: number;
    visual_complexity: number;
    audio_emphasis: number;
    brightness: number;
    contrast: number;
    saturation: number;
    sharpness: number;
  };
  dominant_style?: string;
}

export interface CreatePersonaRequest {
  name: string;
  description: string;
  category: string;
  author: string;
  tags?: string[];
  style_preferences?: Record<string, number>;
  is_public?: boolean;
}

export interface UpdatePersonaRequest {
  author: string;
  name?: string;
  description?: string;
  category?: string;
  tags?: string[];
  style_preferences?: Record<string, number>;
  is_public?: boolean;
}

export interface FeedbackRequest {
  persona_id: string;
  user_id: string;
  rating: number;
  style_preferences?: Record<string, any>;
  operation_feedback?: Record<string, number>;
  text_feedback?: string;
}

export interface GeneratePlanRequest {
  persona_id: string;
  instruction: string;
  video_path: string;
  user_id?: string;
}

export interface APIResponse<T = any> {
  success: boolean;
  message: string;
  data?: T;
}

class PersonaAPIClient {
  private baseURL: string;

  constructor() {
    this.baseURL = `${API_CONFIG.BASE_URL}/api/persona`;
  }

  private async makeRequest<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<APIResponse<T>> {
    try {
      const url = `${this.baseURL}${endpoint}`;
      const response = await fetch(url, {
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
        ...options,
      });

      const data = await response.json();
      
      if (!response.ok) {
        console.error(`API请求失败: ${response.status}`, data);
      }

      return data;
    } catch (error) {
      console.error('API请求错误:', error);
      return {
        success: false,
        message: `网络错误: ${error.message}`,
      };
    }
  }

  /**
   * 创建新的Persona
   */
  async createPersona(data: CreatePersonaRequest): Promise<APIResponse<PersonaData>> {
    return this.makeRequest('/create', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  /**
   * 获取Persona详情
   */
  async getPersona(personaId: string): Promise<APIResponse<PersonaData>> {
    return this.makeRequest(`/get/${personaId}`, {
      method: 'GET',
    });
  }

  /**
   * 更新Persona
   */
  async updatePersona(
    personaId: string,
    data: UpdatePersonaRequest
  ): Promise<APIResponse<PersonaData>> {
    return this.makeRequest(`/update/${personaId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  /**
   * 删除Persona
   */
  async deletePersona(personaId: string, author: string): Promise<APIResponse> {
    return this.makeRequest(`/delete/${personaId}`, {
      method: 'DELETE',
      body: JSON.stringify({ author }),
    });
  }

  /**
   * 列出Persona
   */
  async listPersonas(params: {
    author?: string;
    category?: string;
    status?: string;
    is_public?: boolean;
    is_featured?: boolean;
    limit?: number;
    offset?: number;
  } = {}): Promise<APIResponse<PersonaData[]>> {
    const searchParams = new URLSearchParams();
    
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        searchParams.append(key, value.toString());
      }
    });

    const queryString = searchParams.toString();
    const endpoint = queryString ? `/list?${queryString}` : '/list';

    return this.makeRequest(endpoint, {
      method: 'GET',
    });
  }

  /**
   * 获取推荐Persona
   */
  async getFeaturedPersonas(limit: number = 10): Promise<APIResponse<PersonaData[]>> {
    return this.makeRequest(`/featured?limit=${limit}`, {
      method: 'GET',
    });
  }

  /**
   * 获取热门Persona
   */
  async getPopularPersonas(limit: number = 10): Promise<APIResponse<PersonaData[]>> {
    return this.makeRequest(`/popular?limit=${limit}`, {
      method: 'GET',
    });
  }

  /**
   * 搜索Persona
   */
  async searchPersonas(query: string, limit: number = 20): Promise<APIResponse<PersonaData[]>> {
    const searchParams = new URLSearchParams({
      q: query,
      limit: limit.toString(),
    });

    return this.makeRequest(`/search?${searchParams.toString()}`, {
      method: 'GET',
    });
  }

  /**
   * 分析视频偏好
   */
  async analyzeVideoPreferences(
    personaId: string,
    videoPath: string
  ): Promise<APIResponse<any>> {
    return this.makeRequest('/analyze-video', {
      method: 'POST',
      body: JSON.stringify({
        persona_id: personaId,
        video_path: videoPath,
      }),
    });
  }

  /**
   * 提交用户反馈
   */
  async submitFeedback(data: FeedbackRequest): Promise<APIResponse> {
    return this.makeRequest('/feedback', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  /**
   * 生成剪辑方案
   */
  async generateEditingPlan(data: GeneratePlanRequest): Promise<APIResponse<any>> {
    return this.makeRequest('/generate-plan', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  /**
   * 记录剪辑操作
   */
  async recordEditingOperation(data: {
    persona_id: string;
    operation_type: string;
    parameters: Record<string, any>;
    success?: boolean;
    execution_time?: number;
    error_message?: string;
    user_rating?: number;
  }): Promise<APIResponse> {
    return this.makeRequest('/record-operation', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  /**
   * 获取个性化推荐
   */
  async getRecommendations(
    userId: string,
    userPreferences?: Record<string, any>,
    limit: number = 5
  ): Promise<APIResponse<PersonaData[]>> {
    return this.makeRequest('/recommendations', {
      method: 'POST',
      body: JSON.stringify({
        user_id: userId,
        user_preferences: userPreferences,
        limit,
      }),
    });
  }

  /**
   * 获取用户创建的Persona
   */
  async getUserPersonas(author: string, limit: number = 50): Promise<APIResponse<PersonaData[]>> {
    return this.makeRequest(`/user/${encodeURIComponent(author)}?limit=${limit}`, {
      method: 'GET',
    });
  }

  /**
   * 获取Persona统计信息
   */
  async getPersonaStatistics(personaId: string): Promise<APIResponse<any>> {
    return this.makeRequest(`/statistics/${personaId}`, {
      method: 'GET',
    });
  }

  /**
   * 获取Persona分类列表
   */
  async getPersonaCategories(): Promise<APIResponse<PersonaCategory[]>> {
    return this.makeRequest('/categories', {
      method: 'GET',
    });
  }
}

// 创建单例实例
export const personaAPIClient = new PersonaAPIClient();
export default PersonaAPIClient;
