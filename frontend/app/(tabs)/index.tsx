import { mockInsights } from '@/data/mock-insights';
import { ScrollView, View, Text } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import '../../global.css';

export default function HomeScreen() {
  const latestWeek = mockInsights[0];

  return (
    <SafeAreaView className="flex-1 bg-neutral-900">
      <ScrollView className="p-5">
        <Text className="text-2xl font-bold text-white">
          Welcome Back!
        </Text>
        <Text className="text-base text-gray-300 mt-2 mb-6">
          {latestWeek.summary}
        </Text>
        <Text className="text-lg font-bold text-white mb-3">
          This week's insights
        </Text>
        {latestWeek.insights.map((insight) => (
          <View key={insight.id} className="bg-neutral-800 rounded-lg p-3 mb-2">
            <View className="flex-row gap-2 mb-1">
              <Text className="text-yellow-400 font-semibold">{insight.type}</Text>
              <Text className="text-gray-400">{insight.sources.join(', ')}</Text>
            </View>
            <Text className="text-white">{insight.description}</Text>
            {insight.reflection_question && (
              <Text className="text-gray-400 italic mt-1">{insight.reflection_question}</Text>
            )}
          </View>
        ))}
      </ScrollView>
    </SafeAreaView>
  );
}