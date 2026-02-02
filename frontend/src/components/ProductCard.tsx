import { Card, Button, Flex, Text, Heading, Badge } from "@radix-ui/themes";
import { CheckCircledIcon, CircleIcon, GearIcon } from "@radix-ui/react-icons";
import type { Item } from "@/types";

interface ItemCardProps {
  item: Item;
  onConfigure: (item: Item) => void;
}

export function ItemCard({ item, onConfigure }: ItemCardProps) {
  const getStatusIcon = () => {
    return item.configured ? (
      <CheckCircledIcon style={{ color: 'var(--green-9)' }} />
    ) : (
      <CircleIcon style={{ color: 'var(--gray-9)' }} />
    );
  };

  const getStatusText = () => {
    return item.configured ? "Configured" : "Not configured";
  };

  const getCategoryColor = (category: string) => {
    const colors: Record<string, any> = {
      basic: "blue",
      advanced: "purple", 
      security: "red",
      system: "green",
      custom: "orange"
    };
    return colors[category] || "gray";
  };

  return (
    <Card style={{ width: '100%' }}>
      <Flex direction="column" gap="3" p="4">
        <Flex justify="between" align="center">
          <Heading size="4">{item.name}</Heading>
          {getStatusIcon()}
        </Flex>
        <Text color="gray" size="2">{item.description}</Text>
        
        <Flex align="center" gap="2" justify="between">
          <Flex align="center" gap="2">
            <Text size="2" color="gray">Status:</Text>
            <Badge 
              variant="solid" 
              color={item.configured ? "green" : "gray"}
            >
              {getStatusText()}
            </Badge>
          </Flex>
          <Badge 
            variant="soft" 
            color={getCategoryColor(item.category)}
          >
            {item.category}
          </Badge>
        </Flex>
        
        <Button 
          onClick={() => onConfigure(item)} 
          variant={item.configured ? "outline" : "solid"}
          style={{ width: '100%' }}
        >
          <GearIcon />
          {item.configured ? "Edit Settings" : "Configure"}
        </Button>
      </Flex>
    </Card>
  );
}
