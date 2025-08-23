import React, { createContext, useContext, useEffect, useMemo, useState } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { builtInPresets, buildInstructionFromPreset } from '../utils/personaPresets';
import { PersonaManager, Persona } from '../utils/personaManager';
import personaService, { PersonaResponse } from '../services/personaService';

type ActivePersonaSource = 'builtin' | 'user';

export interface ActivePersonaState {
  id: string;
  name: string;
  source: ActivePersonaSource;
  instruction: string;
}

interface PersonaContextValue {
  activePersona: ActivePersonaState | null;
  applyPreset: (presetId: string) => Promise<ActivePersonaState | null>;
  applyUserPersona: (personaId: string) => Promise<ActivePersonaState | null>;
  clearActivePersona: () => Promise<void>;
  // 新增后端集成方法
  refreshPersonas: () => Promise<void>;
  isBackendConnected: boolean;
  backendPersonas: {
    builtin: PersonaResponse[];
    user: PersonaResponse[];
  };
}

const ACTIVE_PERSONA_KEY = '@active_persona';

const PersonaContext = createContext<PersonaContextValue | undefined>(undefined);

export const PersonaProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [activePersona, setActivePersona] = useState<ActivePersonaState | null>(null);
  const [isBackendConnected, setIsBackendConnected] = useState(false);
  const [backendPersonas, setBackendPersonas] = useState<{
    builtin: PersonaResponse[];
    user: PersonaResponse[];
  }>({
    builtin: [],
    user: []
  });

  useEffect(() => {
    (async () => {
      try {
        // 加载本地存储的活动Persona
        const raw = await AsyncStorage.getItem(ACTIVE_PERSONA_KEY);
        if (raw) {
          const parsed = JSON.parse(raw) as ActivePersonaState;
          setActivePersona(parsed);
        }
        
        // 尝试连接后端并加载Persona数据
        await checkBackendConnection();
      } catch (e) {
        console.warn('初始化Persona上下文失败:', e);
      }
    })();
  }, []);

  const checkBackendConnection = async () => {
    try {
      const connected = await personaService.checkConnection();
      setIsBackendConnected(connected);
      
      if (connected) {
        await refreshPersonas();
      }
    } catch (error) {
      console.warn('后端连接检查失败:', error);
      setIsBackendConnected(false);
    }
  };

  const refreshPersonas = async () => {
    try {
      const allPersonas = await personaService.getAllPersonas();
      setBackendPersonas(allPersonas);
    } catch (error) {
      console.error('刷新Persona数据失败:', error);
      // 如果后端失败，使用本地数据作为备份
      setBackendPersonas({
        builtin: [],
        user: []
      });
    }
  };

  const persist = async (state: ActivePersonaState | null) => {
    if (!state) {
      await AsyncStorage.removeItem(ACTIVE_PERSONA_KEY);
      return;
    }
    await AsyncStorage.setItem(ACTIVE_PERSONA_KEY, JSON.stringify(state));
  };

  const applyPreset = async (presetId: string): Promise<ActivePersonaState | null> => {
    try {
      // 优先从后端获取
      if (isBackendConnected) {
        const persona = await personaService.getPersonaDetail(presetId);
        const instruction = buildInstructionFromPersona(persona);
        const next: ActivePersonaState = {
          id: persona.id,
          name: persona.name,
          source: 'builtin',
          instruction,
        };
        setActivePersona(next);
        await persist(next);
        return next;
      }
    } catch (error) {
      console.warn('从后端获取预设失败，使用本地数据:', error);
    }
    
    // 后备方案：使用本地预设
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
    try {
      // 优先从后端获取
      if (isBackendConnected) {
        const persona = await personaService.getPersonaDetail(personaId);
        const instruction = buildInstructionFromPersona(persona);
        const next: ActivePersonaState = {
          id: persona.id,
          name: persona.name,
          source: 'user',
          instruction,
        };
        setActivePersona(next);
        await persist(next);
        return next;
      }
    } catch (error) {
      console.warn('从后端获取用户Persona失败，使用本地数据:', error);
    }
    
    // 后备方案：使用本地数据
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

  // 辅助函数：从PersonaResponse生成指令
  const buildInstructionFromPersona = (persona: PersonaResponse): string => {
    const parts = [
      `剪辑风格：${persona.name}`,
      `基调：${persona.stylePreset.tone}`,
      `字幕设置：${persona.stylePreset.subtitle.fontFamily} ${persona.stylePreset.subtitle.fontSize}px ${persona.stylePreset.subtitle.color}`,
      `剪辑节奏：${persona.stylePreset.cut.pace}`,
      `背景音乐：${persona.stylePreset.bgm.mood} 音量${persona.stylePreset.bgm.volume}`,
    ];
    return parts.join('；');
  };

  const value = useMemo<PersonaContextValue>(() => ({ 
    activePersona, 
    applyPreset, 
    applyUserPersona, 
    clearActivePersona,
    refreshPersonas,
    isBackendConnected,
    backendPersonas
  }), [activePersona, isBackendConnected, backendPersonas]);

  return <PersonaContext.Provider value={value}>{children}</PersonaContext.Provider>;
};

export const usePersona = (): PersonaContextValue => {
  const ctx = useContext(PersonaContext);
  if (!ctx) throw new Error('usePersona must be used within PersonaProvider');
  return ctx;
};


