import { ScrollView, View, Text } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { mockInsights } from '@/data/mock-insights';

import '../../global.css';

const dataSources = [
  { name: 'Google Calendar', connected: true },
  { name: 'WhatsApp', connected: true },
  { name: 'Health data', connected: false },
];

export default function ProfileScreen() {
  return (
    <SafeAreaView className="flex-1 bg-neutral-900">
      <ScrollView className="p-5">
        <Text className="text-2xl font-bold text-white">Alex Kim</Text>
        <Text className="text-gray-400 mb-5">Member since Jan 2025</Text>

        <Text className="text-lg font-bold text-white mb-3">Connected sources</Text>
        {dataSources.map((source) => (
          <View key={source.name} className="flex-row justify-between bg-neutral-800 rounded-lg p-3 mb-2">
            <Text className="text-white">{source.name}</Text>
            <Text className={source.connected ? 'text-green-500' : 'text-gray-500'}>
              {source.connected ? 'Connected' : 'Not connected'}
            </Text>
          </View>
        ))}

        <Text className="text-lg font-bold text-white mt-5 mb-3">Past breakdowns</Text>
        {mockInsights.map((week) => (
          <View key={week.generated_at} className="bg-neutral-800 rounded-lg p-3 mb-2">
            <View className="flex-row justify-between">
              <Text className="font-bold text-white">{week.generated_at}</Text>
              <Text className="text-gray-400">{week.insights.length} insights</Text>
            </View>
            <Text className="text-gray-300 mt-1" numberOfLines={2}>{week.summary}</Text>
          </View>
        ))}
      </ScrollView>
    </SafeAreaView>
  );
}