/**
 * 应用配置文件
 * 集中管理API端点和其他配置
 */

// API配置
export const API_CONFIG = {
  // 基础URL - 这里需要根据实际部署情况修改
  BASE_URL: 'http://192.168.1.100:5000', // 示例IP，实际使用时请修改
  
  // 端点配置
  ENDPOINTS: {
    // 视频相关
    UPLOAD_VIDEO: '/upload-video',
    PROCESS_VIDEO: '/process-video',
    CHECK_FILE: '/check-file',
    
    // Persona相关
    PERSONA: {
      CREATE: '/api/persona/create',
      GET: '/api/persona/get',
      UPDATE: '/api/persona/update',
      DELETE: '/api/persona/delete',
      LIST: '/api/persona/list',
      FEATURED: '/api/persona/featured',
      POPULAR: '/api/persona/popular',
      SEARCH: '/api/persona/search',
      ANALYZE_VIDEO: '/api/persona/analyze-video',
      FEEDBACK: '/api/persona/feedback',
      GENERATE_PLAN: '/api/persona/generate-plan',
      RECORD_OPERATION: '/api/persona/record-operation',
      RECOMMENDATIONS: '/api/persona/recommendations',
      USER_PERSONAS: '/api/persona/user',
      STATISTICS: '/api/persona/statistics',
      CATEGORIES: '/api/persona/categories'
    }
  },
  
  // 请求配置
  REQUEST: {
    TIMEOUT: 30000, // 30秒超时
    RETRY_COUNT: 3,  // 重试次数
    RETRY_DELAY: 1000, // 重试延迟(ms)
  }
};

// Persona分类配置
export const PERSONA_CATEGORIES = {
  CREATIVE: {
    value: 'creative',
    label: {
      zh: '创意类',
      en: 'Creative'
    }
  },
  PROFESSIONAL: {
    value: 'professional',
    label: {
      zh: '专业类',
      en: 'Professional'
    }
  },
  ENTERTAINMENT: {
    value: 'entertainment',
    label: {
      zh: '娱乐类',
      en: 'Entertainment'
    }
  },
  EDUCATIONAL: {
    value: 'educational',
    label: {
      zh: '教育类',
      en: 'Educational'
    }
  },
  COMMERCIAL: {
    value: 'commercial',
    label: {
      zh: '商业类',
      en: 'Commercial'
    }
  },
  LIFESTYLE: {
    value: 'lifestyle',
    label: {
      zh: '生活类',
      en: 'Lifestyle'
    }
  }
};

// 用户配置
export const USER_CONFIG = {
  DEFAULT_USERNAME: 'user',
  MAX_PERSONAS_PER_USER: 20,
  MAX_PERSONA_NAME_LENGTH: 50,
  MAX_PERSONA_DESCRIPTION_LENGTH: 200
};

// 应用配置
export const APP_CONFIG = {
  VERSION: '1.0.0',
  SUPPORTED_VIDEO_FORMATS: ['mp4', 'mov', 'avi'],
  MAX_VIDEO_SIZE: 100 * 1024 * 1024, // 100MB
  CACHE_DURATION: 24 * 60 * 60 * 1000, // 24小时
};

// 开发配置
export const DEV_CONFIG = {
  ENABLE_LOGS: __DEV__,
  ENABLE_DEBUG: __DEV__,
  MOCK_API: false, // 是否启用模拟API
};

// 导出默认配置
export default {
  API_CONFIG,
  PERSONA_CATEGORIES,
  USER_CONFIG,
  APP_CONFIG,
  DEV_CONFIG
};
