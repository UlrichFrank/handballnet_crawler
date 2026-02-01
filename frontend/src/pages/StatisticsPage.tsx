import { Flex, Heading, Text, Card } from '@radix-ui/themes';
import { StatsGrid } from '@/components/StatsGrid';

const sampleStats = [
  {
    title: 'Total Users',
    value: '12,543',
    change: 12.5,
    changeType: 'increase' as const,
    subtitle: 'Active users this month'
  },
  {
    title: 'Revenue',
    value: '$48,392',
    change: -3.2,
    changeType: 'decrease' as const,
    subtitle: 'Monthly revenue'
  },
  {
    title: 'Projects',
    value: '156',
    change: 0,
    changeType: 'neutral' as const,
    subtitle: 'Total projects'
  },
  {
    title: 'Completion Rate',
    value: '89%',
    progress: 89,
    subtitle: 'Overall project completion'
  },
  {
    title: 'Active Sessions',
    value: '2,847',
    change: 8.3,
    changeType: 'increase' as const,
    subtitle: 'Current active sessions'
  },
  {
    title: 'Error Rate',
    value: '0.02%',
    change: -15.2,
    changeType: 'increase' as const,
    subtitle: 'System error rate'
  }
];

export function StatisticsPage() {
  return (
    <Flex direction="column" gap="6">
      <Heading size="8">Statistics Dashboard</Heading>
      <Text color="gray">
        This demonstrates a statistics dashboard with various metrics, trends, and progress indicators.
        The components show real-time data with trend analysis and visual progress tracking.
      </Text>
      <StatsGrid stats={sampleStats} />
      
      <Card style={{ marginTop: '32px' }}>
        <Flex direction="column" gap="3" p="4">
          <Heading size="5">System Health Metrics</Heading>
          <Flex direction="column" gap="2">
            <Text size="2">
              <Text weight="medium">System Uptime: </Text>
              <Text color="green">99.98%</Text>
            </Text>
            <Text size="2">
              <Text weight="medium">Average Response Time: </Text>
              <Text color="green">145ms</Text>
            </Text>
            <Text size="2">
              <Text weight="medium">Database Connections: </Text>
              <Text color="blue">234/500</Text>
            </Text>
            <Text size="2">
              <Text weight="medium">Cache Hit Rate: </Text>
              <Text color="green">94.7%</Text>
            </Text>
            <Text size="2">
              <Text weight="medium">CPU Usage: </Text>
              <Text color="yellow">67%</Text>
            </Text>
            <Text size="2">
              <Text weight="medium">Memory Usage: </Text>
              <Text color="orange">78%</Text>
            </Text>
          </Flex>
        </Flex>
      </Card>

      <Card>
        <Flex direction="column" gap="3" p="4">
          <Heading size="5">Business Metrics</Heading>
          <Flex direction="column" gap="2">
            <Text size="2">
              <Text weight="medium">Customer Satisfaction: </Text>
              <Text color="green">4.8/5.0</Text>
            </Text>
            <Text size="2">
              <Text weight="medium">Support Tickets: </Text>
              <Text color="yellow">23 open</Text>
            </Text>
            <Text size="2">
              <Text weight="medium">Feature Adoption: </Text>
              <Text color="blue">76%</Text>
            </Text>
            <Text size="2">
              <Text weight="medium">Monthly Growth: </Text>
              <Text color="green">+12.3%</Text>
            </Text>
          </Flex>
        </Flex>
      </Card>
    </Flex>
  );
}
