import { mockInsights } from '@/data/mock-insights';
import { Ionicons } from '@expo/vector-icons';
import { ScrollView, View, Text } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import '../../global.css';

type SourceKey = 'calendar' | 'whatsapp' | 'health';

const dataSources: {
  key: SourceKey;
  name: string;
  icon: keyof typeof Ionicons.glyphMap;
  connected: boolean;
}[] = [
  { key: 'calendar', name: 'Google Calendar', icon: 'calendar-outline', connected: true },
  { key: 'whatsapp', name: 'WhatsApp', icon: 'chatbubbles-outline', connected: true },
  { key: 'health', name: 'Health data', icon: 'heart-outline', connected: false },
];

export default function ProfileScreen() {
  return (
    <SafeAreaView className="flex-1 bg-base">
      <ScrollView
        className="px-5"
        contentContainerStyle={{ paddingBottom: 40 }}
        showsVerticalScrollIndicator={false}
      >
        {/* Header */}
        <View className="items-center mt-4 mb-6">
          <View className="w-20 h-20 rounded-full bg-elevated items-center justify-center mb-3">
            <Text className="text-white text-2xl font-semibold">A</Text>
          </View>
          <Text className="text-white text-xl font-semibold">Alex Kim</Text>
          <Text className="text-text-muted text-sm mt-1">Member since Jan 2025</Text>
        </View>

        {/* Connected sources */}
        <Text className="text-white text-lg font-semibold mb-3">Connected sources</Text>
        {dataSources.map((source) => (
          <View
            key={source.key}
            className="flex-row items-center bg-card rounded-2xl p-4 mb-3"
          >
            <View className="w-10 h-10 rounded-full bg-elevated items-center justify-center mr-3">
              <Ionicons name={source.icon} size={18} color="#fff" />
            </View>
            <Text className="text-white text-base flex-1">{source.name}</Text>
            <View
              className={`px-3 py-1 rounded-full ${
                source.connected ? 'bg-positive/20' : 'bg-elevated'
              }`}
            >
              <Text
                className={`text-xs font-semibold ${
                  source.connected ? 'text-positive' : 'text-text-muted'
                }`}
              >
                {source.connected ? 'Connected' : 'Not connected'}
              </Text>
            </View>
          </View>
        ))}

        {/* Past breakdowns */}
        <Text className="text-white text-lg font-semibold mt-6 mb-3">
          Past breakdowns
        </Text>
        {mockInsights.map((week) => (
          <View key={week.generated_at} className="bg-card rounded-2xl p-4 mb-3">
            <View className="flex-row justify-between items-center mb-2">
              <Text className="text-white font-semibold">{week.generated_at}</Text>
              <View className="bg-primary/20 px-3 py-1 rounded-full">
                <Text className="text-primary text-xs font-semibold">
                  {week.insights.length} insights
                </Text>
              </View>
            </View>
            <Text className="text-text-muted text-sm leading-5" numberOfLines={2}>
              {week.summary}
            </Text>
          </View>
        ))}
      </ScrollView>
    </SafeAreaView>
  );
}
