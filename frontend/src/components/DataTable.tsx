import { Table, Badge, Button, Flex, Text } from "@radix-ui/themes";
import { Pencil1Icon, TrashIcon, EyeOpenIcon } from "@radix-ui/react-icons";
import type { TableData } from "@/types";

interface DataTableProps {
  data: TableData[];
  onEdit?: (item: TableData) => void;
  onDelete?: (item: TableData) => void;
  onView?: (item: TableData) => void;
}

export function DataTable({ data, onEdit, onDelete, onView }: DataTableProps) {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'green';
      case 'inactive':
        return 'red';
      case 'pending':
        return 'yellow';
      default:
        return 'gray';
    }
  };

  const formatDate = (date: Date) => {
    return new Date(date).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  return (
    <Table.Root>
      <Table.Header>
        <Table.Row>
          <Table.ColumnHeaderCell>Name</Table.ColumnHeaderCell>
          <Table.ColumnHeaderCell>Status</Table.ColumnHeaderCell>
          <Table.ColumnHeaderCell>Value</Table.ColumnHeaderCell>
          <Table.ColumnHeaderCell>Category</Table.ColumnHeaderCell>
          <Table.ColumnHeaderCell>Last Updated</Table.ColumnHeaderCell>
          <Table.ColumnHeaderCell>Actions</Table.ColumnHeaderCell>
        </Table.Row>
      </Table.Header>

      <Table.Body>
        {data.map((item) => (
          <Table.Row key={item.id}>
            <Table.Cell>
              <Text weight="medium">{item.name}</Text>
            </Table.Cell>
            <Table.Cell>
              <Badge color={getStatusColor(item.status)} variant="soft">
                {item.status}
              </Badge>
            </Table.Cell>
            <Table.Cell>
              <Text>{item.value.toLocaleString()}</Text>
            </Table.Cell>
            <Table.Cell>
              <Text color="gray">{item.category}</Text>
            </Table.Cell>
            <Table.Cell>
              <Text color="gray" size="2">
                {formatDate(item.lastUpdated)}
              </Text>
            </Table.Cell>
            <Table.Cell>
              <Flex gap="1">
                {onView && (
                  <Button
                    size="1"
                    variant="ghost"
                    onClick={() => onView(item)}
                  >
                    <EyeOpenIcon />
                  </Button>
                )}
                {onEdit && (
                  <Button
                    size="1"
                    variant="ghost"
                    onClick={() => onEdit(item)}
                  >
                    <Pencil1Icon />
                  </Button>
                )}
                {onDelete && (
                  <Button
                    size="1"
                    variant="ghost"
                    color="red"
                    onClick={() => onDelete(item)}
                  >
                    <TrashIcon />
                  </Button>
                )}
              </Flex>
            </Table.Cell>
          </Table.Row>
        ))}
      </Table.Body>
    </Table.Root>
  );
}
