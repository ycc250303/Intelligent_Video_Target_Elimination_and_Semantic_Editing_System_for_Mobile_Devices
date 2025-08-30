import AsyncStorage from '@react-native-async-storage/async-storage';

export interface Persona {
  id: string;
  name: string;
  description: string;
  imageUri: string;
  tag: string;
  progress: number;
  createdAt: string;
  instruction?: string;
  // 新增：指令历史记录
  instructionHistory?: Array<{
    id: string;
    instruction: string;
    action: string;
    timestamp: number;
    videoPath: string;
  }>;
  // 新增：会话ID
  sessionId?: string;
}

const PERSONA_STORAGE_KEY = 'user_personas';

export class PersonaManager {
  // 获取所有Persona
  static async getAllPersonas(): Promise<Persona[]> {
    try {
      const personasJson = await AsyncStorage.getItem(PERSONA_STORAGE_KEY);
      if (personasJson) {
        return JSON.parse(personasJson);
      }
      return [];
    } catch (error) {
      console.error('Error getting personas:', error);
      return [];
    }
  }

  // 添加新Persona
  static async addPersona(persona: Persona): Promise<boolean> {
    try {
      const existingPersonas = await this.getAllPersonas();
      const updatedPersonas = [...existingPersonas, persona];
      await AsyncStorage.setItem(PERSONA_STORAGE_KEY, JSON.stringify(updatedPersonas));
      return true;
    } catch (error) {
      console.error('Error adding persona:', error);
      return false;
    }
  }

  // 删除Persona
  static async deletePersona(personaId: string): Promise<boolean> {
    try {
      const existingPersonas = await this.getAllPersonas();
      const updatedPersonas = existingPersonas.filter(p => p.id !== personaId);
      await AsyncStorage.setItem(PERSONA_STORAGE_KEY, JSON.stringify(updatedPersonas));
      return true;
    } catch (error) {
      console.error('Error deleting persona:', error);
      return false;
    }
  }

  // 更新Persona
  static async updatePersona(updatedPersona: Persona): Promise<boolean> {
    try {
      const existingPersonas = await this.getAllPersonas();
      const updatedPersonas = existingPersonas.map(p =>
        p.id === updatedPersona.id ? updatedPersona : p
      );
      await AsyncStorage.setItem(PERSONA_STORAGE_KEY, JSON.stringify(updatedPersonas));
      return true;
    } catch (error) {
      console.error('Error updating persona:', error);
      return false;
    }
  }

  // 清空所有Persona
  static async clearAllPersonas(): Promise<boolean> {
    try {
      await AsyncStorage.removeItem(PERSONA_STORAGE_KEY);
      return true;
    } catch (error) {
      console.error('Error clearing personas:', error);
      return false;
    }
  }
} 