import React, { useMemo, useState } from 'react';
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
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { useLanguage } from './context/LanguageContext'; // Assuming context is available
import { PersonaManager } from './utils/personaManager';
import { builtInPresets, buildInstructionFromPreset } from './utils/personaPresets';
import { getFeaturedPersonas, getPersonaDisplayMeta } from './utils/personaDisplay';
<<<<<<< Updated upstream
=======
import { usePersona } from './context/PersonaContext';
import { personaAPIClient, PersonaData } from './services/PersonaAPIClient';
>>>>>>> Stashed changes

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
<<<<<<< Updated upstream
  const [selectedCategory, setSelectedCategory] = useState('全部'); // 默认中文标签
=======
  const [selectedCategory, setSelectedCategory] = useState('all');
  const insets = useSafeAreaInsets();
>>>>>>> Stashed changes

  const getLocalizedText = (zhText: string, enText: string) => {
    return currentLanguage === 'zh' ? zhText : enText;
  };

<<<<<<< Updated upstream
  // 简化分类（固定少量高层次标签）
  const categories = [
    { zh: '全部', en: 'All' },
    { zh: '娱乐', en: 'Entertainment' },
    { zh: '叙事', en: 'Narrative' },
    { zh: '专业', en: 'Professional' },
  ];

  const mapTagToSimplifiedCategory = (tag: string): '娱乐' | '叙事' | '专业' => {
    // 允许模糊归类
    if (['搞笑', '电竞', '运动'].includes(tag)) return '娱乐';
    if (['温柔', '生活', '风光'].includes(tag)) return '叙事';
    if (['理性', '数码', '资讯', '大片'].includes(tag)) return '专业';
    return '叙事';
  };

  const cardsFromPresets = getFeaturedPersonas().map(p => ({
    id: p.id,
    title: p.name,
    author: getPersonaDisplayMeta(p.id).author,
    downloads: getPersonaDisplayMeta(p.id).downloads,
    description: p.description,
    image: getPersonaDisplayMeta(p.id).coverImage,
    tag: p.tag,
    simpleCategory: mapTagToSimplifiedCategory(p.tag),
  }));
=======
  // 全新的分类标签系统 - 纯文字版本
  const newCategories = [
    {
      id: 'all',
      zh: '全部',
      en: 'All',
      color: '#6366F1',
      description: '所有风格',
    },
    {
      id: 'trending',
      zh: '热门',
      en: 'Trending',
      color: '#EF4444',
      description: '最受欢迎',
    },
    {
      id: 'creative',
      zh: '创意',
      en: 'Creative',
      color: '#F59E0B',
      description: '富有创意',
    },
    {
      id: 'professional',
      zh: '专业',
      en: 'Professional',
      color: '#10B981',
      description: '商务专业',
    },
    {
      id: 'lifestyle',
      zh: '生活',
      en: 'Lifestyle',
      color: '#8B5CF6',
      description: '日常生活',
    },
    {
      id: 'entertainment',
      zh: '娱乐',
      en: 'Entertainment',
      color: '#EC4899',
      description: '娱乐搞笑',
    },
  ];

  // 基于标签的智能分类映射
  const getSmartCategory = (tag: string): string => {
    const tagMap: { [key: string]: string } = {
      // 娱乐类
      '搞笑': 'entertainment',
      '电竞': 'entertainment',
      '游戏': 'entertainment',

      // 生活类
      '运动': 'lifestyle',
      '生活': 'lifestyle',
      '旅行': 'lifestyle',
      '风光': 'lifestyle',
      'Vlog': 'lifestyle',

      // 专业类
      '理性': 'professional',
      '数码': 'professional',
      '科技': 'professional',
      '资讯': 'professional',
      '测评': 'professional',
      '新闻': 'professional',

      // 创意类
      '温柔': 'creative',
      '浪漫': 'creative',
      '艺术': 'creative',
      '电影': 'creative',
      '大片': 'creative',
    };

    // 添加调试信息
    console.log(`Tag "${tag}" mapped to category: ${tagMap[tag] || 'creative'}`);
    return tagMap[tag] || 'creative';
  };

  const cardsFromPresets = getFeaturedPersonas().map((p, index) => {
    const category = getSmartCategory(p.tag);
    const card = {
      id: p.id,
      title: p.name,
      author: getPersonaDisplayMeta(p.id).author,
      downloads: getPersonaDisplayMeta(p.id).downloads,
      description: p.description,
      image: getPersonaDisplayMeta(p.id).coverImage,
      tag: p.tag,
      category: category,
      isHot: index < 3, // 前三个作为热门内容
      popularity: Math.floor(Math.random() * 1000) + 100, // 模拟人气值
    };

    // 添加调试信息
    console.log(`Card "${p.name}" with tag "${p.tag}" assigned to category "${category}"`);
    return card;
  });
>>>>>>> Stashed changes

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
<<<<<<< Updated upstream
    const byCategory = selectedCategory === '全部' ? true : card.simpleCategory === selectedCategory;
    if (!byCategory) return false;
    if (!searchQuery.trim()) return true;
=======
    // 全新的筛选逻辑
    let matchesCategory = false;

    switch (selectedCategory) {
      case 'all':
        matchesCategory = true;
        break;
      case 'trending':
        matchesCategory = card.isHot || card.popularity > 500;
        break;
      default:
        matchesCategory = card.category === selectedCategory;
        break;
    }

    // 添加调试信息
    console.log(`Filtering card "${card.title}": category="${card.category}", selectedCategory="${selectedCategory}", matches=${matchesCategory}`);

    if (!matchesCategory) {
      return false;
    }

    // 搜索筛选
    if (!searchQuery.trim()) {
      return true;
    }

>>>>>>> Stashed changes
    const q = searchQuery.trim().toLowerCase();
    return (
      card.title.toLowerCase().includes(q) ||
      card.description.toLowerCase().includes(q) ||
      String(card.author).toLowerCase().includes(q)
    );
  });

  return (
    <ImageBackground
      source={require('../Images/background.png')}
      style={styles.background}
      resizeMode="cover"
    >
<<<<<<< Updated upstream
      <View style={styles.headerTitleWrapper}>
        <Text style={styles.headerTitle}>{getLocalizedText('社区', 'Community')}</Text>
      </View>

      <View style={styles.searchSortContainer}>
        <View style={styles.searchBox}>
          <TextInput
            style={styles.searchInput}
            placeholder={getLocalizedText('搜索风格卡...', 'Search Style Card...')}
            placeholderTextColor="#888"
            value={searchQuery}
            onChangeText={setSearchQuery}
          />
          <TouchableOpacity style={styles.searchIconContainer}>
            <Text style={styles.searchIcon}>🔍</Text>
          </TouchableOpacity>
        </View>
        <TouchableOpacity style={styles.sortButton}>
          <Text style={styles.sortButtonText}>{getLocalizedText('按热度排序', 'Sort by Popularity')}</Text>
          <Text style={styles.sortDropdownIcon}>▼</Text>
        </TouchableOpacity>
      </View>

      <ScrollView horizontal contentContainerStyle={styles.categoryTabsContainer} showsHorizontalScrollIndicator={false}>
        {categories.map((category) => (
          <TouchableOpacity
            key={category.zh}
            style={[
              styles.categoryTab,
              selectedCategory === category.zh && styles.selectedCategoryTab,
            ]}
            onPress={() => setSelectedCategory(category.zh)}
          >
            <Text style={[
              styles.categoryTabText,
              selectedCategory === category.zh && styles.selectedCategoryTabText,
            ]}>
              {getLocalizedText(category.zh, category.en)}
            </Text>
          </TouchableOpacity>
        ))}
      </ScrollView>

      <ScrollView contentContainerStyle={styles.scrollContent}>
        {filteredCards.map((card) => (
          <TouchableOpacity
            key={card.id}
            style={styles.card}
            onPress={() => navigation.navigate('StyleCardDetail', { card: card })}
          >
            <Image source={card.image} style={styles.cardImage} resizeMode="cover" />
            <ImageBackground
              source={require('../Images/Community/text_background.png')}
              style={styles.cardContentBackground}
              resizeMode="stretch"
=======
      <ScrollView
        style={styles.mainScrollView}
        contentContainerStyle={styles.mainScrollContent}
        showsVerticalScrollIndicator={false}
      >
        {/* 页面标题 */}
        <View style={[styles.headerSection, { paddingTop: insets.top + getRelativeSize(8) }]}>
          <Text style={styles.headerTitle}>{getLocalizedText('社区', 'Community')}</Text>
        </View>

        {/* 搜索区域 */}
        <View style={styles.searchSection}>
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

        {/* 分类标签区域 */}
        <View style={styles.categoriesSection}>
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
                    styles.textOnlyCategoryButton,
                    {
                      backgroundColor: categoryColor,
                      borderColor: borderColor,
                    },
                  ]}
                  onPress={() => setSelectedCategory(category.id)}
                  activeOpacity={0.8}
                >
                  <Text style={[
                    styles.textOnlyCategoryButtonText,
                    { color: textColor },
                  ]}>
                    {getLocalizedText(category.zh, category.en)}
                  </Text>
                  {isSelected && (
                    <View style={[styles.categoryIndicator, styles.whiteIndicator]} />
                  )}
                </TouchableOpacity>
              );
            })}
          </ScrollView>
        </View>

        {/* 统计信息 */}
        <View style={styles.statsSection}>
          <Text style={styles.statsText}>
            {getLocalizedText(
              `共 ${filteredCards.length} 个风格`,
              `${filteredCards.length} Styles Total (Category: ${selectedCategory})`
            )}
          </Text>
        </View>

        {/* 内容卡片区域 */}
        <View style={styles.cardsSection}>
          {filteredCards.map((card) => (
            <TouchableOpacity
              key={card.id}
              style={styles.card}
              onPress={() => navigation.navigate('StyleCardDetail', { card: card })}
              activeOpacity={0.8}
>>>>>>> Stashed changes
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
<<<<<<< Updated upstream
  headerTitleWrapper: {
    width: '100%',
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: getRelativeSize(20),
    marginBottom: getRelativeSize(2),
  },
  headerTitle: {
    fontSize: getRelativeFontSize(7),
    fontWeight: 'bold',
    color: 'white',
    flex: 1,
    textAlign: 'center',
  },
  searchSortContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: getRelativeSize(5),
    marginBottom: getRelativeSize(5),
    marginTop: getRelativeSize(5),
=======
  mainScrollView: {
    flex: 1,
  },
  mainScrollContent: {
    flexGrow: 1,
    paddingBottom: getRelativeSize(25), // 给底部Tab栏留出空间
  },
  headerSection: {
    paddingHorizontal: getRelativeSize(6),
    paddingBottom: getRelativeSize(6),
    alignItems: 'center',
    justifyContent: 'center',
  },
  headerTitle: {
    fontSize: getRelativeFontSize(7.5),
    fontWeight: '800',
    color: 'white',
    textAlign: 'center',
  },
  searchSection: {
    paddingHorizontal: getRelativeSize(6),
    marginBottom: getRelativeSize(5),
>>>>>>> Stashed changes
  },
  searchBox: {
    flexDirection: 'row',
    alignItems: 'center',
<<<<<<< Updated upstream
    backgroundColor: '#1F1F1F', // Deep dark grey
    borderRadius: getRelativeSize(6),
    paddingHorizontal: getRelativeSize(4),
    flex: 1,
    marginRight: getRelativeSize(2.5),
    height: '100%',
=======
    backgroundColor: 'rgba(255, 255, 255, 0.1)',
    borderRadius: getRelativeSize(12),
    paddingHorizontal: getRelativeSize(5),
    paddingVertical: getRelativeSize(2),
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.2)',
  },
  categoriesSection: {
    marginBottom: getRelativeSize(5),
  },
  categoriesContainer: {
    paddingHorizontal: getRelativeSize(6),
    paddingVertical: getRelativeSize(2),
  },
  textOnlyCategoryButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    borderRadius: getRelativeSize(6),
    paddingHorizontal: getRelativeSize(4),
    paddingVertical: getRelativeSize(2.5),
    marginRight: getRelativeSize(3),
    borderWidth: 1.5,
    position: 'relative',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  textOnlyCategoryButtonText: {
    fontSize: getRelativeFontSize(3.5),
    fontWeight: '600',
    textAlign: 'center',
  },
  categoryIndicator: {
    position: 'absolute',
    bottom: getRelativeSize(-1),
    left: '80%',
    marginLeft: getRelativeSize(-1.5),
    width: getRelativeSize(7),
    height: getRelativeSize(0.8),
    borderRadius: getRelativeSize(0.4),
  },
  whiteIndicator: {
    backgroundColor: 'white',
  },
  searchIcon: {
    fontSize: getRelativeFontSize(5),
    color: '#999',
    marginRight: getRelativeSize(3),
>>>>>>> Stashed changes
  },
  searchInput: {
    flex: 1,
    color: 'white',
    fontSize: getRelativeFontSize(4),
  },
  searchIconContainer: {
    paddingLeft: getRelativeSize(2.5),
  },
  searchIcon: {
    fontSize: getRelativeFontSize(5),
    color: '#999999', // Lighter grey for search icon
  },
  sortButton: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#1F1F1F', // Deep dark grey, consistent with searchBox
    borderRadius: getRelativeSize(6),
    paddingHorizontal: getRelativeSize(4),
    paddingVertical: getRelativeSize(2.5),
  },
  sortButtonText: {
    color: 'white',
    fontSize: getRelativeFontSize(4),
    marginRight: getRelativeSize(1.2),
  },
  sortDropdownIcon: {
    color: 'white',
    fontSize: getRelativeFontSize(3),
  },
  categoryTabsContainer: {
    paddingHorizontal: getRelativeSize(8),
  },
  categoryTab: {
    backgroundColor: '#3A3A3A',
    borderRadius: getRelativeSize(4),
    paddingHorizontal: getRelativeSize(5),
    marginRight: getRelativeSize(4),
  },
  selectedCategoryTab: {
    backgroundColor: '#FFD700',
    borderRadius: getRelativeSize(4),
  },
  categoryTabText: {
    color: 'white',
    fontSize: getRelativeFontSize(4),
    fontWeight: 'bold',
  },
  selectedCategoryTabText: {
    color: 'black',
    fontSize: getRelativeFontSize(4),
  },
<<<<<<< Updated upstream
  scrollContent: {
    flexGrow: 1,
    padding: getRelativeSize(4),
    paddingBottom: getRelativeSize(5),
=======
  statsSection: {
    paddingHorizontal: getRelativeSize(6),
    marginBottom: getRelativeSize(5),
  },
  statsText: {
    color: 'rgba(255, 255, 255, 0.6)',
    fontSize: getRelativeFontSize(3.5),
    textAlign: 'center',
  },
  cardsSection: {
    paddingHorizontal: getRelativeSize(6),
>>>>>>> Stashed changes
  },
  card: {
    backgroundColor: 'transparent',
    borderRadius: getRelativeSize(4),
    overflow: 'hidden',
    width: width - getRelativeSize(8),
    alignSelf: 'center',
    marginTop: getRelativeSize(5),
    marginBottom: getRelativeSize(5),
  },
  cardImage: {
    width: '100%',
    //height: getRelativeSize(45),
    borderTopLeftRadius: getRelativeSize(4),
    borderTopRightRadius: getRelativeSize(4),
    marginLeft: getRelativeSize(-2),
    marginBottom: getRelativeSize(-4), // Negative margin to make the text background overlap slightly
  },
  cardContentBackground: {
    padding: getRelativeSize(6),
    width: '111%',
    justifyContent: 'center',
    paddingTop: getRelativeSize(4), // Add top padding to create space for overlapping
    top: getRelativeSize(-6), // Move up to overlap with the image
    left: getRelativeSize(-4),
  },
  cardTextContent: {
  },
  cardTitle: {
    fontSize: getRelativeFontSize(5),
    fontWeight: 'bold',
    color: '#333333', // Dark color for title
    marginBottom: getRelativeSize(1.2),
  },
  cardMeta: {
    fontSize: getRelativeFontSize(3.5),
    color: '#666666', // Medium grey for meta info
    marginBottom: getRelativeSize(2.5),
  },
  cardDescription: {
    fontSize: getRelativeFontSize(3.5),
    color: '#444444', // Dark grey for description
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
    width: '5%',
    height: '100%',
    tintColor: 'white',
  },
});

export default CommunityScreen; 