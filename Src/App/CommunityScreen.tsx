import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ImageBackground,
  Image,
  TouchableOpacity,
  ScrollView,
  TextInput,
  Dimensions,
} from 'react-native';
import { useLanguage } from './context/LanguageContext'; // Assuming context is available
import { PersonaManager } from './utils/personaManager';
import { builtInPresets, buildInstructionFromPreset } from './utils/personaPresets';
import { getPersonaDisplayMeta } from './utils/personaDisplay';

const { width } = Dimensions.get('window');

// 计算相对尺寸
const getRelativeSize = (percentage: number) => {
  return (width * percentage) / 100;
};

const getRelativeFontSize = (percentage: number) => {
  return Math.round((width * percentage) / 100);
};

const CommunityScreen: React.FC = ({ navigation }: any) => {
  const { currentLanguage } = useLanguage();
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');

  const getLocalizedText = (zhText: string, enText: string) => {
    return currentLanguage === 'zh' ? zhText : enText;
  };

  // 全新的分类标签系统
  const newCategories = [
    {
      id: 'all',
      zh: '全部',
      en: 'All',
      icon: '📋',
      color: '#6366F1',
      description: '所有风格',
    },
    {
      id: 'trending',
      zh: '热门',
      en: 'Trending',
      icon: '🔥',
      color: '#EF4444',
      description: '最受欢迎',
    },
    {
      id: 'creative',
      zh: '创意',
      en: 'Creative',
      icon: '🎨',
      color: '#F59E0B',
      description: '富有创意',
    },
    {
      id: 'professional',
      zh: '专业',
      en: 'Professional',
      icon: '💼',
      color: '#10B981',
      description: '商务专业',
    },
    {
      id: 'lifestyle',
      zh: '生活',
      en: 'Lifestyle',
      icon: '🌟',
      color: '#8B5CF6',
      description: '日常生活',
    },
    {
      id: 'entertainment',
      zh: '娱乐',
      en: 'Entertainment',
      icon: '🎬',
      color: '#EC4899',
      description: '娱乐搞笑',
    },
  ];

  // 基于标签的智能分类映射
  const getSmartCategory = (tag: string): string => {
    const tagMap: { [key: string]: string } = {
      '搞笑': 'entertainment',
      '电竞': 'entertainment',
      '游戏': 'entertainment',
      '运动': 'lifestyle',
      '健身': 'lifestyle',
      '旅行': 'lifestyle',
      '风光': 'lifestyle',
      '生活': 'lifestyle',
      'Vlog': 'lifestyle',
      '理性': 'professional',
      '数码': 'professional',
      '科技': 'professional',
      '资讯': 'professional',
      '新闻': 'professional',
      '测评': 'professional',
      '温柔': 'creative',
      '浪漫': 'creative',
      '艺术': 'creative',
      '电影': 'creative',
      '大片': 'creative',
    };

    return tagMap[tag] || 'creative';
  };

  const cardsFromPresets = builtInPresets.map((p, index) => ({
    id: p.id,
    title: p.name,
    author: getPersonaDisplayMeta(p.id).author,
    downloads: getPersonaDisplayMeta(p.id).downloads,
    description: p.description,
    image: getPersonaDisplayMeta(p.id).coverImage,
    tag: p.tag,
    category: getSmartCategory(p.tag),
    isHot: index < 3, // 前三个作为热门内容
    popularity: Math.floor(Math.random() * 1000) + 100, // 模拟人气值
    createdAt: new Date(Date.now() - Math.random() * 30 * 24 * 60 * 60 * 1000).toISOString(), // 随机创建时间
  }));

  const handleDownloadPreset = async (presetId: string) => {
    const preset = builtInPresets.find(p => p.id === presetId) || builtInPresets[0];
    const instruction = buildInstructionFromPreset(preset.name, preset.stylePreset);
    await PersonaManager.addPersona({
      id: Date.now().toString(),
      name: preset.name,
      description: getLocalizedText('来自社区的风格预设', 'Style preset from community'),
      imageUri: '',
      tag: preset.tag,
      progress: 0.8,
      createdAt: new Date().toISOString(),
      instruction,
    });
  };

  const filteredCards = cardsFromPresets.filter(card => {
    // 分类筛选逻辑
    let matchesCategory = false;

    switch (selectedCategory) {
      case 'all':
        matchesCategory = true;
        break;
      case 'trending':
        // 热门逻辑：显示所有内容
        matchesCategory = true;
        break;
      default:
        matchesCategory = card.category === selectedCategory;
        break;
    }

    if (!matchesCategory) {
      return false;
    }

    // 搜索筛选
    if (!searchQuery.trim()) {
      return true;
    }

    const q = searchQuery.trim().toLowerCase();
    return (
      card.title.toLowerCase().includes(q) ||
      card.description.toLowerCase().includes(q) ||
      String(card.author).toLowerCase().includes(q) ||
      card.tag.toLowerCase().includes(q)
    );
  });

  return (
    <ImageBackground
      source={require('../Images/background.png')}
      style={styles.background}
      resizeMode="cover"
    >
      <View style={styles.headerContainer}>
        <Text style={styles.headerTitle}>{getLocalizedText('社区', 'Community')}</Text>
      </View>

      <View style={styles.searchContainer}>
        <View style={styles.searchBox}>
          <Text style={styles.searchIcon}>🔍</Text>
          <TextInput
            style={styles.searchInput}
            placeholder={getLocalizedText('搜索风格、作者或标签...', 'Search styles, authors or tags...')}
            placeholderTextColor="#999"
            value={searchQuery}
            onChangeText={setSearchQuery}
          />
        </View>
      </View>

      <ScrollView
        horizontal
        contentContainerStyle={styles.categoriesContainer}
        showsHorizontalScrollIndicator={false}
      >
        {newCategories.map((category) => {
          const isSelected = selectedCategory === category.id;
          const categoryColor = isSelected ? category.color : 'rgba(255, 255, 255, 0.1)';
          const borderColor = isSelected ? category.color : 'rgba(255, 255, 255, 0.2)';
          const textColor = isSelected ? 'white' : 'rgba(255, 255, 255, 0.8)';

          return (
            <TouchableOpacity
              key={category.id}
              style={[
                styles.newCategoryButton,
                {
                  backgroundColor: categoryColor,
                  borderColor: borderColor,
                },
              ]}
              onPress={() => setSelectedCategory(category.id)}
              activeOpacity={0.8}
            >
              <Text style={styles.categoryIcon}>{category.icon}</Text>
              <Text 
                style={[
                  styles.newCategoryButtonText,
                  { color: textColor },
                ]}
                numberOfLines={1}
                adjustsFontSizeToFit={true}
                minimumFontScale={0.8}
              >
                {getLocalizedText(category.zh, category.en)}
              </Text>
              {isSelected && (
                <View style={[styles.categoryIndicator, styles.whiteIndicator]} />
              )}
            </TouchableOpacity>
          );
        })}
      </ScrollView>

      <ScrollView contentContainerStyle={styles.scrollContent} showsVerticalScrollIndicator={false}>
        <View style={styles.statsContainer}>
          <Text style={styles.statsText}>
            {getLocalizedText(`共 ${filteredCards.length} 个风格`, `${filteredCards.length} Styles Total`)}
          </Text>
        </View>

        <View style={styles.cardsGrid}>
          {filteredCards.map((card) => (
            <TouchableOpacity
              key={card.id}
              style={styles.card}
              onPress={() => navigation.navigate('StyleCardDetail', { card: card })}
              activeOpacity={0.8}
            >
              <Image source={card.image} style={styles.cardImage} resizeMode="cover" />
              <ImageBackground
                source={require('../Images/Community/text_background.png')}
                style={styles.cardContentBackground}
                resizeMode="stretch"
              >
                <View style={styles.cardTextContent}>
                  <Text style={styles.cardTitle}>{card.title}</Text>
                  <Text style={styles.cardMeta}>
                    {getLocalizedText('作者：', 'Author: ')}{card.author}  {getLocalizedText('下载：', 'Downloads: ')}{card.downloads}
                  </Text>
                  <Text style={styles.cardDescription}>{card.description}</Text>
                  <TouchableOpacity style={styles.downloadButton} onPress={() => handleDownloadPreset(card.id)}>
                    <Text style={styles.downloadButtonText}>{getLocalizedText('下载', 'Download')}</Text>
                    <Image source={require('../Images/Community/download.png')} style={styles.downloadIcon} />
                  </TouchableOpacity>
                </View>
              </ImageBackground>
            </TouchableOpacity>
          ))}
        </View>
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
  headerContainer: {
    paddingHorizontal: getRelativeSize(6),
    paddingTop: getRelativeSize(15),
    paddingBottom: getRelativeSize(8),
    alignItems: 'center',
  },
  headerTitle: {
    fontSize: getRelativeFontSize(8),
    fontWeight: '800',
    color: 'white',
    textAlign: 'center',
    marginBottom: getRelativeSize(2),
  },
  headerSubtitle: {
    fontSize: getRelativeFontSize(4),
    color: 'rgba(255, 255, 255, 0.7)',
    textAlign: 'center',
  },
  searchContainer: {
    paddingHorizontal: getRelativeSize(6),
    marginBottom: getRelativeSize(4),
  },
  searchBox: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'rgba(255, 255, 255, 0.1)',
    borderRadius: getRelativeSize(12),
    paddingHorizontal: getRelativeSize(5),
    paddingVertical: getRelativeSize(4),
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.2)',
  },
  categoriesContainer: {
    paddingHorizontal: getRelativeSize(6),
    marginBottom: getRelativeSize(5),
    paddingVertical: getRelativeSize(2),
  },
  newCategoryButton: {
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    borderRadius: getRelativeSize(4),
    paddingHorizontal: getRelativeSize(5),
    paddingVertical: getRelativeSize(5),
    marginRight: getRelativeSize(3),
    borderWidth: 2,
    minWidth: getRelativeSize(22),
    minHeight: getRelativeSize(18),
    position: 'relative',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  categoryIcon: {
    fontSize: getRelativeFontSize(4.5),
    marginBottom: getRelativeSize(1.5),
    lineHeight: getRelativeFontSize(4.5),
  },
  newCategoryButtonText: {
    fontSize: getRelativeFontSize(3.8),
    fontWeight: '600',
    textAlign: 'center',
    lineHeight: getRelativeFontSize(4.5),
    marginTop: getRelativeSize(0.5),
  },
  categoryIndicator: {
    position: 'absolute',
    bottom: getRelativeSize(-1),
    width: getRelativeSize(10),
    height: getRelativeSize(1),
    borderRadius: getRelativeSize(0.5),
  },
  whiteIndicator: {
    backgroundColor: 'white',
  },
  searchIcon: {
    fontSize: getRelativeFontSize(5),
    color: '#999',
    marginRight: getRelativeSize(3),
  },
  searchInput: {
    flex: 1,
    color: 'white',
    fontSize: getRelativeFontSize(4.2),
    paddingVertical: 0,
  },
  scrollContent: {
    flexGrow: 1,
    paddingHorizontal: getRelativeSize(6),
    paddingBottom: getRelativeSize(25), // 增加底部间距以避开Tab栏
  },
  statsContainer: {
    marginBottom: getRelativeSize(5),
  },
  statsText: {
    color: 'rgba(255, 255, 255, 0.6)',
    fontSize: getRelativeFontSize(3.5),
    textAlign: 'center',
  },
  cardsGrid: {
    gap: getRelativeSize(4),
  },
  card: {
    backgroundColor: 'transparent',
    borderRadius: getRelativeSize(4),
    overflow: 'hidden',
    width: width - getRelativeSize(8),
    alignSelf: 'center',
    marginTop: getRelativeSize(3),
    marginBottom: getRelativeSize(3),
  },
  cardImage: {
    width: '105%',
    height: getRelativeSize(45),
    borderTopLeftRadius: getRelativeSize(4),
    borderTopRightRadius: getRelativeSize(4),
    marginLeft: getRelativeSize(-2),
    marginBottom: getRelativeSize(-4),
  },
  cardContentBackground: {
    padding: getRelativeSize(6),
    width: '111%',
    justifyContent: 'center',
    paddingTop: getRelativeSize(4),
    top: getRelativeSize(-6),
    left: getRelativeSize(-4),
  },
  cardTextContent: {
  },
  cardTitle: {
    fontSize: getRelativeFontSize(5),
    fontWeight: 'bold',
    color: '#333333',
    marginBottom: getRelativeSize(1.2),
  },
  cardMeta: {
    fontSize: getRelativeFontSize(3.5),
    color: '#666666',
    marginBottom: getRelativeSize(2.5),
  },
  cardDescription: {
    fontSize: getRelativeFontSize(3.5),
    color: '#444444',
    marginBottom: getRelativeSize(4),
  },
  downloadButton: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#333333',
    borderRadius: getRelativeSize(5),
    paddingVertical: getRelativeSize(2),
    paddingHorizontal: getRelativeSize(4),
    alignSelf: 'flex-start',
  },
  downloadButtonText: {
    color: 'white',
    fontSize: getRelativeFontSize(4),
    fontWeight: 'bold',
    marginRight: getRelativeSize(2),
  },
  downloadIcon: {
    width: getRelativeSize(5),
    height: getRelativeSize(5),
    tintColor: 'white',
  },
});

export default CommunityScreen;