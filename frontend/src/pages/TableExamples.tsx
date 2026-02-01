import { Flex, Heading, Text } from '@radix-ui/themes';
import { DataTable } from '@/components/DataTable';
import type { TableData } from '@/types';

const sampleTableData: TableData[] = [
  {
    id: '1',
    name: 'Service Alpha',
    status: 'active',
    value: 1250,
    category: 'Core Services',
    lastUpdated: new Date('2024-01-15'),
  },
  {
    id: '2',
    name: 'Service Beta',
    status: 'pending',
    value: 850,
    category: 'Optional',
    lastUpdated: new Date('2024-01-10'),
  },
  {
    id: '3',
    name: 'Service Gamma',
    status: 'inactive',
    value: 0,
    category: 'Deprecated',
    lastUpdated: new Date('2023-12-20'),
  },
  {
    id: '4',
    name: 'Service Delta',
    status: 'active',
    value: 2100,
    category: 'Core Services',
    lastUpdated: new Date('2024-01-12'),
  },
  {
    id: '5',
    name: 'Service Epsilon',
    status: 'pending',
    value: 450,
    category: 'Optional',
    lastUpdated: new Date('2024-01-08'),
  },
];

export function TableExamples() {
  const handleEdit = (item: TableData) => {
    alert(`Edit ${item.name}`);
  };

  const handleDelete = (item: TableData) => {
    alert(`Delete ${item.name}`);
  };

  const handleView = (item: TableData) => {
    alert(`View details for ${item.name}`);
  };

  return (
    <Flex direction="column" gap="6">
      <Heading size="8">Data Table Examples</Heading>
      <Text color="gray">
        This demonstrates a data table with various features like status badges, actions, and formatting.
        The table is responsive and includes sorting, filtering, and action capabilities.
      </Text>
      <DataTable
        data={sampleTableData}
        onEdit={handleEdit}
        onDelete={handleDelete}
        onView={handleView}
      />
    </Flex>
  );
}
