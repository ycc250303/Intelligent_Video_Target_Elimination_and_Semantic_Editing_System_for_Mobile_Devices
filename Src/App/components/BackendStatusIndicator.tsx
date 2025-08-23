/**
 * 后端连接状态指示器组件
 */
import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { usePersona } from '../context/PersonaContext';

interface BackendStatusIndicatorProps {
  showText?: boolean;
  style?: any;
}

export const BackendStatusIndicator: React.FC<BackendStatusIndicatorProps> = ({ 
  showText = false, 
  style 
}) => {
  const { isBackendConnected } = usePersona();

  return (
    <View style={[styles.container, style]}>
      <View style={[
        styles.indicator, 
        { backgroundColor: isBackendConnected ? '#10B981' : '#EF4444' }
      ]} />
      {showText && (
        <Text style={[
          styles.text,
          { color: isBackendConnected ? '#10B981' : '#EF4444' }
        ]}>
          {isBackendConnected ? '后端已连接' : '离线模式'}
        </Text>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  indicator: {
    width: 8,
    height: 8,
    borderRadius: 4,
    marginRight: showText ? 6 : 0,
  },
  text: {
    fontSize: 12,
    fontWeight: '500',
  },
});

export default BackendStatusIndicator;
