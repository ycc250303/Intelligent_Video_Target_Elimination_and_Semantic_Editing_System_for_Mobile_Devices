import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ImageBackground,
  ScrollView,
  Dimensions,
  TouchableOpacity,
  Image,
  TextInput,
  Alert,
} from 'react-native';
import { useLanguage } from './context/LanguageContext';
import { useNavigation, useRoute } from '@react-navigation/native';
import { launchImageLibrary, ImagePickerResponse, MediaType } from 'react-native-image-picker';
import { PersonaManager, Persona } from './utils/personaManager';

const { width } = Dimensions.get('window');

// 计算相对尺寸
const getRelativeSize = (percentage: number) => {
  return (width * percentage) / 100;
};

const getRelativeFontSize = (percentage: number) => {
  return Math.round((width * percentage) / 100);
};

// 新增：指令历史记录类型
interface InstructionRecord {
  id: string;
  instruction: string;
  action: string;
  timestamp: number;
  videoPath: string;
}

// 新增：路由参数类型
interface RouteParams {
  instructionHistory?: InstructionRecord[];
  currentSessionId?: string;
  defaultName?: string;
  defaultDescription?: string;
}

const CreatePersonaScreen: React.FC = () => {
  const { currentLanguage } = useLanguage();
  const navigation = useNavigation();
  const route = useRoute();
  const params = (route.params || {}) as RouteParams;

  const [personaName, setPersonaName] = useState(params.defaultName || '');
  const [personaDescription, setPersonaDescription] = useState(params.defaultDescription || '');
  const [selectedImage, setSelectedImage] = useState<string | null>(null);

  // 新增：指令历史
  const instructionHistory = params.instructionHistory || [];
  const currentSessionId = params.currentSessionId;

  const getLocalizedText = (zhText: string, enText: string) => {
    return currentLanguage === 'zh' ? zhText : enText;
  };

  const handleImagePicker = () => {
    const options = {
      mediaType: 'photo' as MediaType,
      includeBase64: false,
      maxHeight: 2000,
      maxWidth: 2000,
      quality: 0.8 as const,
    };

    launchImageLibrary(options, (response: ImagePickerResponse) => {
      if (response.didCancel) {
        console.log('User cancelled image picker');
      } else if (response.errorCode) {
        Alert.alert(
          getLocalizedText('错误', 'Error'),
          getLocalizedText('选择图片时出现错误', 'Error selecting image')
        );
      } else if (response.assets && response.assets[0]) {
        const imageUri = response.assets[0].uri;
        if (imageUri) {
          setSelectedImage(imageUri);
        }
      }
    });
  };

  const handleCreatePersona = async () => {
    if (!personaName.trim()) {
      Alert.alert(
        getLocalizedText('错误', 'Error'),
        getLocalizedText('请输入Persona名称', 'Please enter a Persona name')
      );
      return;
    }

    if (!personaDescription.trim()) {
      Alert.alert(
        getLocalizedText('错误', 'Error'),
        getLocalizedText('请输入Persona描述', 'Please enter a Persona description')
      );
      return;
    }

    // 图片不再是必填项，如果没有选择则使用默认图片
    const imageUri = selectedImage || 'default_persona_image';

    try {
      // 创建Persona对象，包含指令历史
      const newPersona: Persona = {
        id: Date.now().toString(),
        name: personaName.trim(),
        description: personaDescription.trim(),
        imageUri: imageUri,
        tag: getLocalizedText('自定义', 'Custom'),
        progress: 0.8, // 默认进度
        createdAt: new Date().toISOString(),
        // 新增：保存指令历史
        instructionHistory: instructionHistory,
        sessionId: currentSessionId,
      };

      // 保存Persona到本地存储
      const success = await PersonaManager.addPersona(newPersona);

      if (success) {
        // 显示成功消息
        Alert.alert(
          getLocalizedText('成功', 'Success'),
          getLocalizedText('Persona创建成功！', 'Persona created successfully!'),
          [
            {
              text: getLocalizedText('确定', 'OK'),
              onPress: () => {
                // 清空表单
                setPersonaName('');
                setPersonaDescription('');
                setSelectedImage(null);
                // 返回上一页
                navigation.goBack();
              },
            },
          ]
        );
      } else {
        Alert.alert(
          getLocalizedText('错误', 'Error'),
          getLocalizedText('保存Persona时出现错误', 'Error saving Persona')
        );
      }
    } catch (error) {
      console.error('Error creating persona:', error);
      Alert.alert(
        getLocalizedText('错误', 'Error'),
        getLocalizedText('创建Persona时出现错误', 'Error creating Persona')
      );
    }
  };

  return (
    <ImageBackground
      source={require('../Images/background.png')}
      style={styles.background}
      resizeMode="cover"
    >
      <ScrollView contentContainerStyle={styles.scrollContent}>
        {/* Header */}
        <View style={styles.headerTitleWrapper}>
          <TouchableOpacity
            style={styles.backButton}
            onPress={() => navigation.goBack()}
          >
            <Text style={styles.backButtonText}>{'<'}</Text>
          </TouchableOpacity>
          <Text style={styles.headerTitle}>{getLocalizedText('创建Persona', 'Create Persona')}</Text>
        </View>

        {/* Image Upload Section */}
        <View style={styles.sectionWrapper}>
          <Text style={styles.sectionTitle}>{getLocalizedText('上传图片', 'Upload Image')}</Text>
          <TouchableOpacity style={styles.imageUploadContainer} onPress={handleImagePicker}>
            {selectedImage ? (
              <View style={styles.selectedImageContainer}>
                <Image source={{ uri: selectedImage }} style={styles.selectedImage} />
                <TouchableOpacity
                  style={styles.removeImageButton}
                  onPress={() => setSelectedImage(null)}
                >
                  <Text style={styles.removeImageButtonText}>×</Text>
                </TouchableOpacity>
              </View>
            ) : (
              <View style={styles.uploadPlaceholder}>
                <Image source={require('../Images/HomePage/add.png')} style={styles.uploadIcon} />
                <Text style={styles.uploadText}>{getLocalizedText('点击上传图片', 'Tap to upload image')}</Text>
              </View>
            )}
          </TouchableOpacity>
        </View>

        {/* Persona Name Section */}
        <View style={styles.sectionWrapper}>
          <Text style={styles.sectionTitle}>{getLocalizedText('Persona名称', 'Persona Name')}</Text>
          <TextInput
            style={styles.textInput}
            value={personaName}
            onChangeText={setPersonaName}
            placeholder={getLocalizedText('请输入Persona名称', 'Enter Persona name')}
            placeholderTextColor="#999"
            maxLength={20}
          />
        </View>

        {/* Persona Description Section */}
        <View style={styles.sectionWrapper}>
          <Text style={styles.sectionTitle}>{getLocalizedText('Persona描述', 'Persona Description')}</Text>
          <TextInput
            style={[styles.textInput, styles.descriptionInput]}
            value={personaDescription}
            onChangeText={setPersonaDescription}
            placeholder={getLocalizedText('请描述这个Persona的特点、性格、说话方式等', 'Describe the characteristics, personality, speaking style of this Persona')}
            placeholderTextColor="#999"
            multiline
            numberOfLines={6}
            textAlignVertical="top"
          />
        </View>

        {/* 新增：指令历史显示 */}
        {instructionHistory.length > 0 && (
          <View style={styles.sectionWrapper}>
            <Text style={styles.sectionTitle}>{getLocalizedText('指令历史', 'Instruction History')}</Text>
            <View style={styles.instructionHistoryContainer}>
              {instructionHistory.map((record, index) => (
                <View key={record.id} style={styles.instructionItem}>
                  <Text style={styles.instructionIndex}>{index + 1}</Text>
                  <View style={styles.instructionContent}>
                    <Text style={styles.instructionText}>{record.instruction}</Text>
                    <Text style={styles.instructionAction}>{record.action}</Text>
                  </View>
                </View>
              ))}
            </View>
          </View>
        )}

        {/* Create Button */}
        <TouchableOpacity style={styles.createButton} onPress={handleCreatePersona}>
          <Text style={styles.createButtonText}>{getLocalizedText('创建Persona', 'Create Persona')}</Text>
        </TouchableOpacity>
      </ScrollView>
    </ImageBackground>
  );
};

const styles = StyleSheet.create({
  background: {
    flex: 1,
    width: '100%',
    height: '100%',
  },
  scrollContent: {
    flexGrow: 1,
    padding: getRelativeSize(5),
    paddingTop: getRelativeSize(10),
    paddingBottom: getRelativeSize(5),
  },
  headerTitleWrapper: {
    width: '100%',
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    height: getRelativeSize(44),
    paddingHorizontal: 0,
    marginTop: 0,
    marginBottom: 0,
    backgroundColor: 'transparent',
  },
  backButton: {
    paddingHorizontal: getRelativeSize(3.75),
    paddingVertical: getRelativeSize(1.25),
    height: getRelativeSize(14),
    justifyContent: 'center',
    alignItems: 'center',
  },
  backButtonText: {
    fontSize: getRelativeFontSize(7),
    color: 'white',
    fontWeight: 'bold',
    marginRight: getRelativeSize(2.5),
  },
  headerTitle: {
    fontSize: getRelativeFontSize(7),
    fontWeight: 'bold',
    color: 'white',
    flex: 1,
    textAlign: 'center',
    lineHeight: getRelativeSize(14),
    left: getRelativeSize(-5),
  },
  sectionWrapper: {
    marginBottom: getRelativeSize(5),
  },
  sectionTitle: {
    fontSize: getRelativeFontSize(4.5),
    fontWeight: 'bold',
    color: 'white',
    marginBottom: getRelativeSize(2.5),
  },
  imageUploadContainer: {
    width: '100%',
    height: getRelativeSize(30),
    backgroundColor: 'rgba(255, 255, 255, 0.1)',
    borderRadius: getRelativeSize(2.5),
    borderWidth: 2,
    borderColor: 'rgba(255, 255, 255, 0.3)',
    borderStyle: 'dashed',
    justifyContent: 'center',
    alignItems: 'center',
  },
  uploadPlaceholder: {
    alignItems: 'center',
    justifyContent: 'center',
  },
  uploadIcon: {
    width: getRelativeSize(8),
    height: getRelativeSize(8),
    marginBottom: getRelativeSize(2),
    tintColor: 'rgba(255, 255, 255, 0.7)',
  },
  uploadText: {
    fontSize: getRelativeFontSize(3.5),
    color: 'rgba(255, 255, 255, 0.7)',
    textAlign: 'center',
  },
  selectedImageContainer: {
    position: 'relative',
    width: '100%',
    height: '100%',
  },
  selectedImage: {
    width: '100%',
    height: '100%',
    borderRadius: getRelativeSize(2.5),
  },
  removeImageButton: {
    position: 'absolute',
    top: getRelativeSize(1),
    right: getRelativeSize(1),
    width: getRelativeSize(6),
    height: getRelativeSize(6),
    backgroundColor: 'rgba(255, 0, 0, 0.8)',
    borderRadius: getRelativeSize(3),
    justifyContent: 'center',
    alignItems: 'center',
  },
  removeImageButtonText: {
    color: 'white',
    fontSize: getRelativeFontSize(4),
    fontWeight: 'bold',
  },
  textInput: {
    backgroundColor: 'rgba(255, 255, 255, 0.1)',
    borderRadius: getRelativeSize(2.5),
    paddingHorizontal: getRelativeSize(3),
    paddingVertical: getRelativeSize(2.5),
    fontSize: getRelativeFontSize(4),
    color: 'white',
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.3)',
  },
  descriptionInput: {
    height: getRelativeSize(20),
    textAlignVertical: 'top',
  },
  createButton: {
    backgroundColor: '#6A5ACD',
    borderRadius: getRelativeSize(7.5),
    paddingVertical: getRelativeSize(3),
    paddingHorizontal: getRelativeSize(20),
    alignSelf: 'center',
    marginTop: getRelativeSize(5),
    marginBottom: getRelativeSize(5),
    minWidth: getRelativeSize(60),
  },
  createButtonText: {
    color: 'white',
    fontSize: getRelativeFontSize(4),
    fontWeight: 'bold',
    textAlign: 'center',
  },
  instructionHistoryContainer: {
    backgroundColor: 'rgba(255, 255, 255, 0.1)',
    borderRadius: getRelativeSize(2.5),
    padding: getRelativeSize(3),
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.3)',
  },
  instructionItem: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: getRelativeSize(1),
    paddingVertical: getRelativeSize(1),
    paddingHorizontal: getRelativeSize(2),
    backgroundColor: 'rgba(255, 255, 255, 0.05)',
    borderRadius: getRelativeSize(1),
  },
  instructionIndex: {
    fontSize: getRelativeFontSize(3.5),
    fontWeight: 'bold',
    color: 'white',
    marginRight: getRelativeSize(2),
  },
  instructionContent: {
    flex: 1,
  },
  instructionText: {
    fontSize: getRelativeFontSize(3.5),
    color: 'white',
    marginBottom: getRelativeSize(0.5),
  },
  instructionAction: {
    fontSize: getRelativeFontSize(3),
    color: 'rgba(255, 255, 255, 0.7)',
  },
});

export default CreatePersonaScreen; 