import React, { useEffect } from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import { createMaterialTopTabNavigator } from '@react-navigation/material-top-tabs';
import { StackNavigationProp } from '@react-navigation/stack';
import { RouteProp } from '@react-navigation/native';
import { Platform, Text, View, ImageBackground, StyleSheet, PermissionsAndroid, Alert, Linking, Animated, TouchableOpacity, StatusBar, UIManager } from 'react-native';
import { MaterialTopTabBarProps } from '@react-navigation/material-top-tabs';
import { SafeAreaProvider, useSafeAreaInsets } from 'react-native-safe-area-context';
import MediaPickerScreen from './Src/App/MediaPickerScreen';
import EditMediaScreen from './Src/App/EditMediaScreen';
import SettingsScreen from './Src/App/SettingsScreen';
import HomeScreen from './Src/App/HomeScreen';
import CommunityScreen from './Src/App/CommunityScreen';
import PersonaScreen from './Src/App/PersonaScreen';
import CreatePersonaScreen from './Src/App/CreatePersonaScreen';
import StyleCardDetailScreen from './Src/App/StyleCardDetailScreen';
import SelectPersonaScreen from './Src/App/SelectPersonaScreen';
import { requestStoragePermissions } from './Src/App/utils/permissionManager';
import { LanguageProvider, useLanguage } from './Src/App/context/LanguageContext';
import { UserProvider } from './Src/App/context/UserContext';
import { PersonaProvider } from './Src/App/context/PersonaContext';

// Custom Tab Bar Icons
const HomeTabIcon = ({ focused, color }: { focused: boolean; color: string }) => {
  const scaleValue = React.useRef(new Animated.Value(1)).current;

  React.useEffect(() => {
    Animated.spring(scaleValue, {
      toValue: focused ? 1.2 : 1,
      friction: 5,
      tension: 100,
      useNativeDriver: true,
    }).start();
  }, [focused, scaleValue]);

  return <Animated.Text style={{ color, fontSize: 24, fontWeight: focused ? 'bold' : 'normal', transform: [{ scale: scaleValue }] }}>🏠</Animated.Text>;
};

const ProjectsTabIcon = ({ focused, color }: { focused: boolean; color: string }) => {
  const scaleValue = React.useRef(new Animated.Value(1)).current;

  React.useEffect(() => {
    Animated.spring(scaleValue, {
      toValue: focused ? 1.2 : 1,
      friction: 5,
      tension: 100,
      useNativeDriver: true,
    }).start();
  }, [focused, scaleValue]);

  return <Animated.Text style={{ color, fontSize: 24, fontWeight: focused ? 'bold' : 'normal', transform: [{ scale: scaleValue }] }}>📁</Animated.Text>;
};

const SettingsTabIcon = ({ focused, color }: { focused: boolean; color: string }) => {
  const scaleValue = React.useRef(new Animated.Value(1)).current;

  React.useEffect(() => {
    Animated.spring(scaleValue, {
      toValue: focused ? 1.2 : 1,
      friction: 5,
      tension: 100,
      useNativeDriver: true,
    }).start();
  }, [focused, scaleValue]);

  return <Animated.Text style={{ color, fontSize: 24, fontWeight: focused ? 'bold' : 'normal', transform: [{ scale: scaleValue }] }}>⚙️</Animated.Text>;
};

const CommunityTabIcon = ({ focused, color }: { focused: boolean; color: string }) => {
  const scaleValue = React.useRef(new Animated.Value(1)).current;

  React.useEffect(() => {
    Animated.spring(scaleValue, {
      toValue: focused ? 1.2 : 1,
      friction: 5,
      tension: 100,
      useNativeDriver: true,
    }).start();
  }, [focused, scaleValue]);

  return <Animated.Text style={{ color, fontSize: 24, fontWeight: focused ? 'bold' : 'normal', transform: [{ scale: scaleValue }] }}>👥</Animated.Text>;
};

const PersonaTabIcon = ({ focused, color }: { focused: boolean; color: string }) => {
  const scaleValue = React.useRef(new Animated.Value(1)).current;

  React.useEffect(() => {
    Animated.spring(scaleValue, {
      toValue: focused ? 1.2 : 1,
      friction: 5,
      tension: 100,
      useNativeDriver: true,
    }).start();
  }, [focused, scaleValue]);

  return <Animated.Text style={{ color, fontSize: 24, fontWeight: focused ? 'bold' : 'normal', transform: [{ scale: scaleValue }] }}>😀</Animated.Text>;
};

// Custom Tab Bar Component
const CustomTabBar: React.FC<MaterialTopTabBarProps> = ({ state, descriptors, navigation }) => {
  const { currentLanguage } = useLanguage();
  const insets = useSafeAreaInsets();
  const getLocalizedText = (zhText: string, enText: string) => {
    return currentLanguage === 'zh' ? zhText : enText;
  };

  return (
    <ImageBackground
      source={require('./Src/Images/bottom-tabs.png')}
      style={[styles.tabBarBackground, {
        paddingBottom: insets.bottom,
        height: 100 + insets.bottom,
      }]}
      resizeMode="cover"
    >
      <View style={styles.tabBarContainer}>
        {state.routes.map((route, index) => {
          const { options } = descriptors[route.key];

          const isFocused = state.index === index;

          const onPress = () => {
            const event = navigation.emit({
              type: 'tabPress',
              target: route.key,
              canPreventDefault: true,
            });

            if (!isFocused && !event.defaultPrevented) {
              navigation.navigate(route.name);
            }
          };

          const onLongPress = () => {
            navigation.emit({
              type: 'tabLongPress',
              target: route.key,
            });
          };

          const icon = options.tabBarIcon ? options.tabBarIcon({ focused: isFocused, color: isFocused ? '#007AFF' : 'gray' }) : null;

          const getLabelText = () => {
            if (options.tabBarLabel !== undefined) {
              return typeof options.tabBarLabel === 'string'
                ? getLocalizedText(
                  options.tabBarLabel === '主页' ? '主页' : options.tabBarLabel === '剪辑' ? '剪辑' : options.tabBarLabel === '设置' ? '设置' : options.tabBarLabel === '社区' ? '社区' : 'Persona',
                  options.tabBarLabel === 'Home' ? 'Home' : options.tabBarLabel === 'Edit' ? 'Edit' : options.tabBarLabel === 'Settings' ? 'Settings' : options.tabBarLabel === 'Community' ? 'Community' : 'Persona'
                )
                : typeof options.tabBarLabel === 'function'
                  ? options.tabBarLabel({ focused: isFocused, color: isFocused ? '#007AFF' : 'gray', children: '' })
                  : String(options.tabBarLabel);
            } else if (options.title !== undefined) {
              return typeof options.title === 'string'
                ? getLocalizedText(
                  options.title === '主页' ? '主页' : options.title === '剪辑' ? '剪辑' : options.title === '设置' ? '设置' : options.title === '社区' ? '社区' : 'Persnoa',
                  options.title === 'Home' ? 'Home' : options.title === 'Edit' ? 'Edit' : options.title === 'Settings' ? 'Settings' : options.title === 'Community' ? 'Community' : 'Persona'
                )
                : String(options.title);
            } else {
              return getLocalizedText(
                route.name === 'HomeTab' ? '主页' : route.name === 'Projects' ? '剪辑' : route.name === 'Settings' ? '设置' : route.name === 'Community' ? '社区' : 'Persona',
                route.name === 'HomeTab' ? 'Home' : route.name === 'Projects' ? 'Edit' : route.name === 'Settings' ? 'Settings' : route.name === 'Community' ? 'Community' : 'Persona'
              );
            }
          };

          return (
            <TouchableOpacity
              key={route.key}
              accessibilityRole="button"
              accessibilityState={isFocused ? { selected: true } : {}}
              accessibilityLabel={options.tabBarAccessibilityLabel}
              onPress={onPress}
              onLongPress={onLongPress}
              style={styles.tabBarItem}
            >
              {icon}
              <Text style={{ color: isFocused ? '#007AFF' : 'gray', fontSize: 12, marginBottom: 3 }}>
                {getLabelText()}
              </Text>
            </TouchableOpacity>
          );
        })}
      </View>
    </ImageBackground>
  );
};

type RootStackParamList = {
  HomeTab: undefined;
  EditMedia: { mediaUri: string; isVideo: boolean; };
  MediaPicker: undefined;
  Projects: undefined;
  Settings: undefined;
  Community: undefined;
  Persona: undefined;
  CreatePersona: undefined;
  StyleCardDetail: { card: any; };
  SelectPersona: { onApply?: (instruction: string) => void } | undefined;
  MainTabs: undefined;
};



const Stack = createStackNavigator<RootStackParamList>();
const Tab = createMaterialTopTabNavigator<RootStackParamList>();

// 主页堆栈导航器
const HomeStack = () => {
  const { currentLanguage } = useLanguage();
  const getLocalizedText = (zhText: string, enText: string) => {
    return currentLanguage === 'zh' ? zhText : enText;
  };

  return (
    <Stack.Navigator>
      <Stack.Screen
        name="MediaPicker"
        component={MediaPickerScreen}
        options={{
          headerShown: false,
          headerTransparent: true,
        }}
      />
      <Stack.Screen
        name="EditMedia"
        component={EditMediaScreen}
        options={{ title: getLocalizedText('项目编辑', 'Project Edit'), headerTransparent: true, headerTintColor: 'white', headerShown: false }}
      />
      <Stack.Screen
        name="SelectPersona"
        component={SelectPersonaScreen}
        options={{ headerShown: false }}
      />
    </Stack.Navigator>
  );
};

// 新增：包含底部导航的组件，将在此处使用 useLanguage
const MainTabs = () => {
  const { currentLanguage } = useLanguage();
  const insets = useSafeAreaInsets();

  const getLocalizedText = (zhText: string, enText: string) => {
    return currentLanguage === 'zh' ? zhText : enText;
  };

  return (
    <Tab.Navigator
      initialRouteName="Projects"
      tabBarPosition="bottom"
      tabBar={props => <CustomTabBar {...props} />}
      screenOptions={{
        tabBarActiveTintColor: '#007AFF',
        tabBarInactiveTintColor: 'gray',
        tabBarStyle: {
          height: 65 + insets.bottom,
          backgroundColor: 'transparent',
          borderTopWidth: 0,
          shadowColor: '#000',
          shadowOffset: { width: 0, height: -2 },
          shadowOpacity: 0.1,
          shadowRadius: 5,
          elevation: 10,
          zIndex: 999,
          paddingBottom: insets.bottom,
        },
        tabBarLabelStyle: {
          fontSize: 12,
          marginBottom: 3,
        },
        tabBarIndicatorStyle: {
          opacity: 0,
        },
      }}
    >
      <Tab.Screen
        name="HomeTab"
        component={HomeScreen}
        options={{
          title: getLocalizedText('主页', 'Home'),
          tabBarIcon: ({ color, focused }) => (
            <HomeTabIcon color={color} focused={focused} />
          ),
        }}
      />
      <Tab.Screen
        name="Community"
        component={CommunityScreen}
        options={{
          title: getLocalizedText('社区', 'Community'),
          tabBarIcon: ({ color, focused }) => (
            <CommunityTabIcon color={color} focused={focused} />
          ),
        }}
      />
      <Tab.Screen
        name="Persona"
        component={PersonaScreen}
        options={{
          title: getLocalizedText('Persona', 'Persona'),
          tabBarIcon: ({ color, focused }) => (
            <PersonaTabIcon color={color} focused={focused} />
          ),
        }}
      />
      <Tab.Screen
        name="Projects"
        component={HomeStack}
        options={{
          title: getLocalizedText('剪辑', 'Edit'),
          tabBarIcon: ({ color, focused }) => (
            <ProjectsTabIcon color={color} focused={focused} />
          ),
        }}
      />
      <Tab.Screen
        name="Settings"
        component={SettingsScreen}
        options={{
          title: getLocalizedText('设置', 'Settings'),
          tabBarIcon: ({ color, focused }) => (
            <SettingsTabIcon color={color} focused={focused} />
          ),
        }}
      />
    </Tab.Navigator>
  );
};

// 权限请求函数 (保留作为备用)
/*
const requestPermissions = async () => {
  if (Platform.OS === 'android') {
    try {
      if (Platform.Version >= 33) {
        const permissions = [
          PermissionsAndroid.PERMISSIONS.READ_MEDIA_IMAGES,
          PermissionsAndroid.PERMISSIONS.READ_MEDIA_VIDEO,
          PermissionsAndroid.PERMISSIONS.READ_MEDIA_AUDIO,
          PermissionsAndroid.PERMISSIONS.POST_NOTIFICATIONS,
        ];

        const results = await PermissionsAndroid.requestMultiple(permissions);

        const allGranted = Object.values(results).every(
          result => result === PermissionsAndroid.RESULTS.GRANTED
        );

        if (!allGranted) {
          Alert.alert(
            '权限请求',
            '需要存储权限才能正常使用应用。请在设置中开启相关权限。',
            [
              {
                text: '去设置',
                onPress: () => {
                  Linking.openSettings().catch(() => {
                    Alert.alert('提示', '无法打开设置页面');
                  });
                },
              },
              {
                text: '取消',
                style: 'cancel',
              },
            ]
          );
        }
      } else {
        const permissions = [
          PermissionsAndroid.PERMISSIONS.WRITE_EXTERNAL_STORAGE,
          PermissionsAndroid.PERMISSIONS.READ_EXTERNAL_STORAGE,
        ];

        const results = await PermissionsAndroid.requestMultiple(permissions);

        const allGranted = Object.values(results).every(
          result => result === PermissionsAndroid.RESULTS.GRANTED
        );

        if (!allGranted) {
          Alert.alert(
            '权限请求',
            '需要存储权限才能正常使用应用。请在设置中开启相关权限。',
            [
              {
                text: '去设置',
                onPress: () => {
                  Linking.openSettings().catch(() => {
                    Alert.alert('提示', '无法打开设置页面');
                  });
                },
              },
              {
                text: '取消',
                style: 'cancel',
              },
            ]
          );
        }
      }
    } catch (err) {
      console.warn('权限请求失败:', err);
    }
  }
}; */

// 主应用组件
const App: React.FC = () => {
  // 在应用启动时请求权限并配置系统UI
  useEffect(() => {
    const checkPermissions = async () => {
      const granted = await requestStoragePermissions();
      if (!granted) {
        console.warn('存储权限未获得，部分功能可能无法正常使用');
      }
    };

    // 配置系统UI - 隐藏系统导航栏
    const configureSystemUI = () => {
      if (Platform.OS === 'android') {
        // Android - 设置全屏沉浸式模式
        if (UIManager.setLayoutAnimationEnabledExperimental) {
          UIManager.setLayoutAnimationEnabledExperimental(true);
        }
      }
    };

    checkPermissions();
    configureSystemUI();
  }, []);

  return (
    <SafeAreaProvider>
      <StatusBar
        hidden={true}
        translucent={true}
        backgroundColor="transparent"
        barStyle="light-content"
      />
      <View style={styles.container}>
        <ImageBackground
          source={require('./Src/Images/background.png')}
          style={styles.backgroundImage}
          resizeMode="cover"
        >
          <LanguageProvider>
            <UserProvider>
              <PersonaProvider>
                <NavigationContainer>
                  <Stack.Navigator screenOptions={{ headerShown: false }}>
                    <Stack.Screen name="MainTabs" component={MainTabs} />
                    <Stack.Screen name="CreatePersona" component={CreatePersonaScreen} />
                    <Stack.Screen name="StyleCardDetail" component={StyleCardDetailScreen} />
                  </Stack.Navigator>
                </NavigationContainer>
              </PersonaProvider>
            </UserProvider>
          </LanguageProvider>
        </ImageBackground>
      </View>
    </SafeAreaProvider>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  backgroundImage: {
    flex: 1,
    width: '100%',
    height: '100%',
  },
  tabBarBackground: {
    height: 100,
    position: 'absolute',
    bottom: 0,
    left: 0,
    right: 0,
    justifyContent: 'flex-start',
    alignItems: 'center',
    backgroundColor: 'transparent',
    borderTopWidth: 0,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: -2 },
    shadowOpacity: 0.1,
    shadowRadius: 5,
    elevation: 10,
    zIndex: 999,
  },
  tabBarContainer: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    alignItems: 'center',
    width: '100%',
    height: 100,
    paddingTop: 20,
  },
  tabBarItem: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 25,
  },
});

export default App;