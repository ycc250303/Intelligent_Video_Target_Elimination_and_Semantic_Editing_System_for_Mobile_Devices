import React, { createContext, useContext, useEffect, useMemo, useState } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { builtInPresets, buildInstructionFromPreset } from '../utils/personaPresets';
import { PersonaManager, Persona } from '../utils/personaManager';
import { personaAPIClient, PersonaData } from '../services/PersonaAPIClient';

type ActivePersonaSource = 'builtin' | 'user' | 'remote';

export interface ActivePersonaState {
  id: string;
  name: string;
  source: ActivePersonaSource;
  instruction: string;
}

interface PersonaContextValue {
  activePersona: ActivePersonaState | null;
  featuredPersonas: PersonaData[];
  userPersonas: PersonaData[];
  isLoading: boolean;
  error: string | null;
  
  // 原有方法
  applyPreset: (presetId: string) => Promise<ActivePersonaState | null>;
  applyUserPersona: (personaId: string) => Promise<ActivePersonaState | null>;
  clearActivePersona: () => Promise<void>;
  
  // 新增方法
  applyRemotePersona: (personaId: string) => Promise<ActivePersonaState | null>;
  refreshFeaturedPersonas: () => Promise<void>;
  refreshUserPersonas: (author: string) => Promise<void>;
  createPersona: (data: {
    name: string;
    description: string;
    category: string;
    author: string;
    tags?: string[];
    style_preferences?: Record<string, number>;
    is_public?: boolean;
  }) => Promise<PersonaData | null>;
  submitFeedback: (data: {
    persona_id: string;
    user_id: string;
    rating: number;
    style_preferences?: Record<string, any>;
    operation_feedback?: Record<string, number>;
    text_feedback?: string;
  }) => Promise<boolean>;
}

const ACTIVE_PERSONA_KEY = '@active_persona';

const PersonaContext = createContext<PersonaContextValue | undefined>(undefined);

export const PersonaProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [activePersona, setActivePersona] = useState<ActivePersonaState | null>(null);
  const [featuredPersonas, setFeaturedPersonas] = useState<PersonaData[]>([]);
  const [userPersonas, setUserPersonas] = useState<PersonaData[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const persist = async (state: ActivePersonaState | null) => {
    if (!state) {
      await AsyncStorage.removeItem(ACTIVE_PERSONA_KEY);
      return;
    }
    await AsyncStorage.setItem(ACTIVE_PERSONA_KEY, JSON.stringify(state));
  };

  const refreshFeaturedPersonas = async () => {
    try {
      setIsLoading(true);
      setError(null);
      
      const response = await personaAPIClient.getFeaturedPersonas(10);
      
      if (response.success && response.data) {
        setFeaturedPersonas(response.data);
      } else {
        setError(response.message);
      }
    } catch (e) {
      console.error('获取推荐Persona失败:', e);
      setError('获取推荐Persona失败');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    (async () => {
      try {
        const raw = await AsyncStorage.getItem(ACTIVE_PERSONA_KEY);
        if (raw) {
          const parsed = JSON.parse(raw) as ActivePersonaState;
          setActivePersona(parsed);
        }
        
        // 初始化时加载推荐Persona
        await refreshFeaturedPersonas();
      } catch (e) {
        console.error('初始化PersonaContext失败:', e);
        setError('初始化失败');
      }
    })();
  }, []);

  const applyPreset = async (presetId: string): Promise<ActivePersonaState | null> => {
    const preset = builtInPresets.find(p => p.id === presetId);
    if (!preset) return null;
    const instruction = buildInstructionFromPreset(preset.name, preset.stylePreset);
    const next: ActivePersonaState = {
      id: preset.id,
      name: preset.name,
      source: 'builtin',
      instruction,
    };
    setActivePersona(next);
    await persist(next);
    return next;
  };

  const applyUserPersona = async (personaId: string): Promise<ActivePersonaState | null> => {
    const all: Persona[] = await PersonaManager.getAllPersonas();
    const match = all.find(p => p.id === personaId);
    if (!match) return null;
    const instruction = match.instruction || match.description || '';
    const next: ActivePersonaState = {
      id: match.id,
      name: match.name,
      source: 'user',
      instruction,
    };
    setActivePersona(next);
    await persist(next);
    return next;
  };

  const clearActivePersona = async () => {
    setActivePersona(null);
    await persist(null);
  };

  const applyRemotePersona = async (personaId: string): Promise<ActivePersonaState | null> => {
    try {
      setIsLoading(true);
      setError(null);
      
      const response = await personaAPIClient.getPersona(personaId);
      
      if (response.success && response.data) {
        const persona = response.data;
        const instruction = `使用${persona.name}的剪辑风格，${persona.description}`;
        
        const next: ActivePersonaState = {
          id: persona.id,
          name: persona.name,
          source: 'remote',
          instruction,
        };
        
        setActivePersona(next);
        await persist(next);
        return next;
      } else {
        setError(response.message);
        return null;
      }
    } catch (e) {
      console.error('应用远程Persona失败:', e);
      setError('应用Persona失败');
      return null;
    } finally {
      setIsLoading(false);
    }
  };

  const refreshUserPersonas = async (author: string) => {
    try {
      setIsLoading(true);
      setError(null);
      
      const response = await personaAPIClient.getUserPersonas(author);
      
      if (response.success && response.data) {
        setUserPersonas(response.data);
      } else {
        setError(response.message);
      }
    } catch (e) {
      console.error('获取用户Persona失败:', e);
      setError('获取用户Persona失败');
    } finally {
      setIsLoading(false);
    }
  };

  const createPersona = async (data: {
    name: string;
    description: string;
    category: string;
    author: string;
    tags?: string[];
    style_preferences?: Record<string, number>;
    is_public?: boolean;
  }): Promise<PersonaData | null> => {
    try {
      setIsLoading(true);
      setError(null);
      
      const response = await personaAPIClient.createPersona(data);
      
      if (response.success && response.data) {
        // 刷新用户Persona列表
        await refreshUserPersonas(data.author);
        return response.data;
      } else {
        setError(response.message);
        return null;
      }
    } catch (e) {
      console.error('创建Persona失败:', e);
      setError('创建Persona失败');
      return null;
    } finally {
      setIsLoading(false);
    }
  };

  const submitFeedback = async (data: {
    persona_id: string;
    user_id: string;
    rating: number;
    style_preferences?: Record<string, any>;
    operation_feedback?: Record<string, number>;
    text_feedback?: string;
  }): Promise<boolean> => {
    try {
      setError(null);
      
      const response = await personaAPIClient.submitFeedback(data);
      
      if (response.success) {
        return true;
      } else {
        setError(response.message);
        return false;
      }
    } catch (e) {
      console.error('提交反馈失败:', e);
      setError('提交反馈失败');
      return false;
    }
  };

  const value = useMemo<PersonaContextValue>(
    () => ({
      activePersona,
      featuredPersonas,
      userPersonas,
      isLoading,
      error,
      applyPreset,
      applyUserPersona,
      clearActivePersona,
      applyRemotePersona,
      refreshFeaturedPersonas,
      refreshUserPersonas,
      createPersona,
      submitFeedback,
    }),
    [activePersona, featuredPersonas, userPersonas, isLoading, error]
  );

  return <PersonaContext.Provider value={value}>{children}</PersonaContext.Provider>;
};

export const usePersona = (): PersonaContextValue => {
  const ctx = useContext(PersonaContext);
  if (!ctx) throw new Error('usePersona must be used within PersonaProvider');
  return ctx;
};