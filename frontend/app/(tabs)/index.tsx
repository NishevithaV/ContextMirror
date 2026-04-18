import { mockInsights } from '@/data/mock-insights';
import { Ionicons } from '@expo/vector-icons';
import { LinearGradient } from 'expo-linear-gradient';
import { ScrollView, View, Text, Pressable } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import '../../global.css';

export default function HomeScreen() {
  const latestWeek = mockInsights[0];

  return (
    <SafeAreaView className="flex-1 bg-base">
      <ScrollView
        className="px-5"
        contentContainerStyle={{ paddingBottom: 40 }}
        showsVerticalScrollIndicator={false}
      >
        {/* Header */}
        <View className="flex-row items-center justify-between mt-2 mb-5">
          <View className="flex-row items-center gap-3">
            <View className="w-11 h-11 rounded-full bg-elevated items-center justify-center">
              <Text className="text-white font-semibold">A</Text>
            </View>
            <View>
              <Text className="text-text-muted text-xs">Welcome back</Text>
              <Text className="text-white text-lg font-semibold">Alex Kim</Text>
            </View>
          </View>
          <Pressable className="w-11 h-11 rounded-full bg-elevated items-center justify-center">
            <Ionicons name="notifications-outline" size={20} color="#fff" />
          </Pressable>
        </View>

        {/* Hero gradient card */}
        <LinearGradient
          colors={['#1E3A8A', '#3B5FD9', '#0F0F10']}
          start={{ x: 0, y: 0 }}
          end={{ x: 1, y: 1 }}
          style={{ borderRadius: 24, padding: 20, marginBottom: 20 }}
        >
          <Text className="text-white/70 text-xs uppercase tracking-widest">
            This week's story
          </Text>
          <Text className="text-white text-xl font-semibold mt-2 leading-7">
            {latestWeek.summary}
          </Text>
          <Text className="text-white/50 text-xs mt-4">
            Generated {latestWeek.generated_at}
          </Text>
        </LinearGradient>

        {/* Quick stats */}
        <View className="flex-row gap-3 mb-6">
          <View className="flex-1 bg-card rounded-2xl p-4">
            <Text className="text-text-muted text-xs">Insights</Text>
            <Text className="text-white text-2xl font-semibold mt-1">
              {latestWeek.insights.length}
            </Text>
          </View>
          <View className="flex-1 bg-card rounded-2xl p-4">
            <Text className="text-text-muted text-xs">Sources active</Text>
            <Text className="text-white text-2xl font-semibold mt-1">2</Text>
          </View>
          <View className="flex-1 bg-card rounded-2xl p-4">
            <Text className="text-text-muted text-xs">Timeframe</Text>
            <Text className="text-white text-2xl font-semibold mt-1">7d</Text>
          </View>
        </View>

        {/* Insights list */}
        <Text className="text-white text-lg font-semibold mb-3">
          This week's insights
        </Text>

        {latestWeek.insights.map((insight) => (
          <View key={insight.id} className="bg-card rounded-2xl p-4 mb-3">
            <View className="flex-row items-center gap-2 mb-2">
              <View className="bg-primary/20 px-3 py-1 rounded-full">
                <Text className="text-primary text-xs font-semibold">
                  {insight.type}
                </Text>
              </View>
              <Text className="text-text-muted text-xs">
                {insight.sources.join(' · ')}
              </Text>
            </View>
            <Text className="text-white text-base leading-6">
              {insight.description}
            </Text>
            {insight.reflection_question && (
              <View className="mt-3 pt-3 border-t border-elevated">
                <Text className="text-text-muted text-sm italic">
                  {insight.reflection_question}
                </Text>
              </View>
            )}
          </View>
        ))}
      </ScrollView>
    </SafeAreaView>
  );
}
