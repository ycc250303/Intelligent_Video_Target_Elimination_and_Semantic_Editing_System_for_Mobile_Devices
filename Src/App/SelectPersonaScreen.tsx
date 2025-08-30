import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ImageBackground,
  ScrollView,
  TouchableOpacity,
  Image,
  Alert,
} from 'react-native';
import { useNavigation, useRoute } from '@react-navigation/native';
import { useLanguage } from './context/LanguageContext';
// import { builtInPresets, buildInstructionFromPreset } from './utils/personaPresets';
import { PersonaManager, Persona } from './utils/personaManager';

type RouteParams = {
  onApply?: (instruction: string) => void;
  onApplyStepByStep?: (instructions: Array<{ instruction: string, action: string }>) => void;
};

const SelectPersonaScreen: React.FC = () => {
  const navigation = useNavigation();
  const route = useRoute();
  const { currentLanguage } = useLanguage();
  const params = (route.params || {}) as RouteParams;

  // 新增：用户创建的Persona状态
  const [userPersonas, setUserPersonas] = useState<Persona[]>([]);

  const getLocalizedText = (zhText: string, enText: string) =>
    currentLanguage === 'zh' ? zhText : enText;

  // 新增：加载用户创建的Persona
  useEffect(() => {
    const loadUserPersonas = async () => {
      try {
        const personas = await PersonaManager.getAllPersonas();
        setUserPersonas(personas);
      } catch (error) {
        console.error('Error loading user personas:', error);
      }
    };

    loadUserPersonas();
  }, []);

  // 内置Persona应用函数 - 暂时注释掉
  /*
  const handleApply = async (presetId: string) => {
    const preset = builtInPresets.find(p => p.id === presetId);
    if (!preset) return;
    const instruction = buildInstructionFromPreset(preset.name, preset.stylePreset);
    if (typeof params.onApply === 'function') {
      params.onApply(instruction);
    }
    navigation.goBack();
  };
  */

  // 新增：处理用户Persona应用 - 支持逐步执行
  const handleApplyUserPersona = async (persona: Persona) => {
    if (!persona.instructionHistory || persona.instructionHistory.length === 0) {
      // 如果没有指令历史，使用描述作为指令
      if (typeof params.onApply === 'function') {
        params.onApply(persona.description);
      }
      navigation.goBack();
      return;
    }

    // 如果有指令历史，询问用户是否要逐步执行
    Alert.alert(
      getLocalizedText('选择执行方式', 'Select Execution Method'),
      getLocalizedText(
        `发现 ${persona.instructionHistory.length} 条指令历史，请选择执行方式：`,
        `Found ${persona.instructionHistory.length} instruction history, please select execution method:`
      ),
      [
        {
          text: getLocalizedText('取消', 'Cancel'),
          style: 'cancel',
        },
        {
          text: getLocalizedText('合并执行', 'Execute Combined'),
          onPress: () => {
            // 合并所有指令
            const instructions = persona.instructionHistory!.map(record => record.instruction).join('; ');
            if (typeof params.onApply === 'function') {
              params.onApply(instructions);
            }
            navigation.goBack();
          },
        },
        {
          text: getLocalizedText('逐步执行', 'Execute Step by Step'),
          onPress: () => {
            // 直接调用onApplyStepByStep回调，传递指令历史
            if (typeof params.onApplyStepByStep === 'function') {
              params.onApplyStepByStep(persona.instructionHistory!);
            }
            navigation.goBack();
          },
        },
      ]
    );
  };

  return (
    <ImageBackground
      source={require('../Images/background.png')}
      style={styles.background}
      resizeMode="cover"
    >
      <View style={styles.headerTitleWrapper}>
        <TouchableOpacity style={styles.backButton} onPress={() => navigation.goBack()}>
          <Text style={styles.backButtonText}>{'<'}</Text>
        </TouchableOpacity>
        <Text style={styles.headerTitle}>{getLocalizedText('选择Persona', 'Select Persona')}</Text>
      </View>

      <ScrollView contentContainerStyle={styles.content}>
        {/* 内置Persona - 暂时注释掉 */}
        {/*
        <Text style={styles.sectionTitle}>{getLocalizedText('内置Persona', 'Built-in Personas')}</Text>
        {builtInPresets.map(preset => (
          <ImageBackground
            key={preset.id}
            source={require('../Images/Community/text_background.png')}
            style={styles.card}
            resizeMode="stretch"
          >
            <View style={styles.cardInner}>
              <View style={styles.left}>
                <Image source={preset.icon} style={styles.icon} />
              </View>
              <View style={styles.middle}>
                <Text style={styles.name}>{preset.name}</Text>
                <Text style={styles.tag}>{preset.tag}</Text>
                <Text style={styles.desc}>{preset.description}</Text>
              </View>
              <View style={styles.right}>
                <TouchableOpacity style={styles.applyBtn} onPress={() => handleApply(preset.id)}>
                  <Text style={styles.applyBtnText}>{getLocalizedText('应用', 'Apply')}</Text>
                </TouchableOpacity>
              </View>
            </View>
          </ImageBackground>
        ))}
        */}

        {/* 用户创建的Persona */}
        {userPersonas.length > 0 && (
          <>
            <Text style={styles.sectionTitle}>{getLocalizedText('我的Persona', 'My Personas')}</Text>
            {userPersonas.map(persona => (
              <ImageBackground
                key={persona.id}
                source={require('../Images/Community/text_background.png')}
                style={styles.card}
                resizeMode="stretch"
              >
                <View style={styles.cardInner}>
                  <View style={styles.left}>
                    <Image
                      source={persona.imageUri && persona.imageUri !== 'default_persona_image'
                        ? { uri: persona.imageUri }
                        : require('../Images/HomePage/user.png')}
                      style={styles.icon}
                    />
                  </View>
                  <View style={styles.middle}>
                    <Text style={styles.name}>{persona.name}</Text>
                    <Text style={styles.tag}>{persona.tag}</Text>
                    <Text style={styles.desc}>{persona.description}</Text>
                    {persona.instructionHistory && persona.instructionHistory.length > 0 && (
                      <Text style={styles.instructionCount}>
                        {getLocalizedText('指令数量:', 'Instructions:')} {persona.instructionHistory.length}
                      </Text>
                    )}
                  </View>
                  <View style={styles.right}>
                    <TouchableOpacity style={styles.applyBtn} onPress={() => handleApplyUserPersona(persona)}>
                      <Text style={styles.applyBtnText}>{getLocalizedText('应用', 'Apply')}</Text>
                    </TouchableOpacity>
                  </View>
                </View>
              </ImageBackground>
            ))}
          </>
        )}
      </ScrollView>
    </ImageBackground>
  );
};

const styles = StyleSheet.create({
  background: { flex: 1, width: '100%', height: '100%' },
  content: { padding: 16, paddingBottom: 24 },
  headerTitleWrapper: {
    width: '100%',
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    height: 60,
    backgroundColor: 'transparent',
  },
  backButton: { paddingHorizontal: 12, paddingVertical: 6, height: 40, justifyContent: 'center', alignItems: 'center' },
  backButtonText: { fontSize: 24, color: 'white', fontWeight: 'bold', marginRight: 6 },
  headerTitle: { fontSize: 24, fontWeight: 'bold', color: 'white', flex: 1, textAlign: 'center', lineHeight: 60 },
  card: {
    width: '106%',
    marginLeft: '-3%',
    height: 120,
    borderRadius: 12,
    marginBottom: 12,
    overflow: 'hidden',
  },
  cardInner: { flex: 1, flexDirection: 'row', padding: 12 },
  left: { width: 64, alignItems: 'center' },
  icon: { width: 40, height: 40, borderRadius: 20, marginTop: 10 },
  middle: { flex: 1, paddingHorizontal: 12 },
  name: { color: 'black', fontSize: 16, fontWeight: 'bold' },
  tag: { color: 'black', fontSize: 12, backgroundColor: '#FFD700', alignSelf: 'flex-start', paddingHorizontal: 8, paddingVertical: 3, borderRadius: 12, marginTop: 6 },
  desc: { color: '#222', fontSize: 12, marginTop: 8 },
  right: { width: 90, justifyContent: 'center', alignItems: 'center' },
  applyBtn: { backgroundColor: '#6A5ACD', borderRadius: 18, paddingVertical: 8, paddingHorizontal: 16 },
  applyBtnText: { color: 'white', fontSize: 14, fontWeight: 'bold' },
  sectionTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: 'white',
    marginTop: 20,
    marginBottom: 10,
  },
  instructionCount: {
    color: 'white',
    fontSize: 12,
    marginTop: 8,
  },
});

export default SelectPersonaScreen;


