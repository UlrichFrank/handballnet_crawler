import { Card, Flex, Text, Heading, Progress, Badge, Box } from "@radix-ui/themes";
import { ArrowUpIcon, ArrowDownIcon, MinusIcon } from "@radix-ui/react-icons";

interface StatCardProps {
  title: string;
  value: string | number;
  change?: number;
  changeType?: 'increase' | 'decrease' | 'neutral';
  subtitle?: string;
  progress?: number;
}

export function StatCard({ title, value, change, changeType, subtitle, progress }: StatCardProps) {
  const getTrendIcon = () => {
    switch (changeType) {
      case 'increase':
        return <ArrowUpIcon style={{ color: 'var(--green-9)' }} />;
      case 'decrease':
        return <ArrowDownIcon style={{ color: 'var(--red-9)' }} />;
      case 'neutral':
        return <MinusIcon style={{ color: 'var(--gray-9)' }} />;
      default:
        return null;
    }
  };

  const getTrendColor = () => {
    switch (changeType) {
      case 'increase':
        return 'green';
      case 'decrease':
        return 'red';
      case 'neutral':
        return 'gray';
      default:
        return 'gray';
    }
  };

  return (
    <Card style={{ width: '100%' }}>
      <Flex direction="column" gap="3" p="4">
        <Flex justify="between" align="center">
          <Text size="2" color="gray" weight="medium">
            {title}
          </Text>
          {change !== undefined && (
            <Flex align="center" gap="1">
              {getTrendIcon()}
              <Badge color={getTrendColor()} variant="soft">
                {change > 0 ? '+' : ''}{change}%
              </Badge>
            </Flex>
          )}
        </Flex>
        
        <Heading size="6">{value}</Heading>
        
        {subtitle && (
          <Text size="2" color="gray">
            {subtitle}
          </Text>
        )}
        
        {progress !== undefined && (
          <Flex direction="column" gap="1">
            <Text size="2" color="gray">Progress</Text>
            <Progress value={progress} />
            <Text size="1" color="gray" style={{ alignSelf: 'flex-end' }}>
              {progress}%
            </Text>
          </Flex>
        )}
      </Flex>
    </Card>
  );
}

interface StatsGridProps {
  stats: StatCardProps[];
}

export function StatsGrid({ stats }: StatsGridProps) {
  return (
    <Box style={{ 
      display: 'grid', 
      gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
      gap: '16px'
    }}>
      {stats.map((stat, index) => (
        <StatCard key={index} {...stat} />
      ))}
    </Box>
  );
}
