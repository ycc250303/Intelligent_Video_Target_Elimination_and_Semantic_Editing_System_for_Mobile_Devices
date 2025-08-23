/**
 * Persona服务 - 处理所有Persona相关的API调用
 */
import { API_CONFIG, REQUEST_CONFIG, ApiResponse, PersonaResponse, PersonaListResponse } from '../utils/apiConfig';

class PersonaService {
  
  /**
   * 通用请求方法
   */
  private async request<T>(
    endpoint: string, 
    options: RequestInit = {}
  ): Promise<ApiResponse<T>> {
    try {
      const url = `${API_CONFIG.BASE_URL}${endpoint}`;
      
      const response = await fetch(url, {
        ...options,
        headers: {
          ...REQUEST_CONFIG.headers,
          ...options.headers,
        },
        timeout: REQUEST_CONFIG.timeout,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('API请求失败:', error);
      throw error;
    }
  }

  /**
   * 获取所有Persona（内置+用户创建）
   */
  async getAllPersonas(userId: string = 'default'): Promise<PersonaListResponse> {
    const response = await this.request<PersonaListResponse>(
      `${API_CONFIG.ENDPOINTS.PERSONAS}?user_id=${userId}`
    );
    
    if (response.status === 'success' && response.data) {
      return response.data;
    }
    
    throw new Error(response.error || '获取Persona列表失败');
  }

  /**
   * 获取单个Persona详情
   */
  async getPersonaDetail(personaId: string): Promise<PersonaResponse> {
    const response = await this.request<PersonaResponse>(
      API_CONFIG.ENDPOINTS.PERSONAS_DETAIL(personaId)
    );
    
    if (response.status === 'success' && response.data) {
      return response.data;
    }
    
    throw new Error(response.error || 'Persona不存在');
  }

  /**
   * 创建新的Persona
   */
  async createPersona(data: {
    name: string;
    description: string;
    tag: string;
    userId?: string;
  }): Promise<PersonaResponse> {
    const response = await this.request<PersonaResponse>(
      API_CONFIG.ENDPOINTS.PERSONAS_CREATE,
      {
        method: 'POST',
        body: JSON.stringify({
          name: data.name,
          description: data.description,
          tag: data.tag,
          user_id: data.userId || 'default',
        }),
      }
    );
    
    if (response.status === 'success' && response.data) {
      return response.data;
    }
    
    throw new Error(response.error || '创建Persona失败');
  }

  /**
   * 删除Persona
   */
  async deletePersona(personaId: string): Promise<boolean> {
    const response = await this.request(
      API_CONFIG.ENDPOINTS.PERSONAS_DELETE(personaId),
      {
        method: 'DELETE',
      }
    );
    
    if (response.status === 'success') {
      return true;
    }
    
    throw new Error(response.error || '删除Persona失败');
  }

  /**
   * 搜索Persona
   */
  async searchPersonas(query: string, userId: string = 'default'): Promise<PersonaResponse[]> {
    const response = await this.request<PersonaResponse[]>(
      `${API_CONFIG.ENDPOINTS.PERSONAS_SEARCH}?query=${encodeURIComponent(query)}&user_id=${userId}`
    );
    
    if (response.status === 'success' && response.data) {
      return response.data;
    }
    
    throw new Error(response.error || '搜索失败');
  }

  /**
   * 获取人格卡数据
   */
  async getPersonalityCard(cardName: string): Promise<any> {
    const response = await this.request(
      API_CONFIG.ENDPOINTS.PERSONALITY_CARD(cardName)
    );
    
    if (response.status === 'success' && response.data) {
      return response.data;
    }
    
    throw new Error(response.error || '获取人格卡失败');
  }

  /**
   * 基于人格卡生成Persona
   */
  async generatePersonaFromCard(cardName: string, personaName?: string): Promise<PersonaResponse> {
    const response = await this.request<PersonaResponse>(
      API_CONFIG.ENDPOINTS.GENERATE_FROM_CARD(cardName),
      {
        method: 'POST',
        body: JSON.stringify({
          persona_name: personaName || `AI生成-${cardName}`,
        }),
      }
    );
    
    if (response.status === 'success' && response.data) {
      return response.data;
    }
    
    throw new Error(response.error || '生成Persona失败');
  }

  /**
   * 检查后端连接状态
   */
  async checkConnection(): Promise<boolean> {
    try {
      const response = await this.request(API_CONFIG.ENDPOINTS.HEALTH_CHECK);
      return response.status === 'success';
    } catch (error) {
      console.warn('后端连接检查失败:', error);
      return false;
    }
  }

  /**
   * 获取内置预设（兼容性方法）
   */
  async getBuiltinPresets(): Promise<PersonaResponse[]> {
    const allPersonas = await this.getAllPersonas();
    return allPersonas.builtin;
  }

  /**
   * 获取用户创建的Persona（兼容性方法）
   */
  async getUserPersonas(userId: string = 'default'): Promise<PersonaResponse[]> {
    const allPersonas = await this.getAllPersonas(userId);
    return allPersonas.user;
  }
}

// 导出单例实例
export const personaService = new PersonaService();
export default personaService;
