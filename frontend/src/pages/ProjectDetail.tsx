import { Flex, Heading, Text, Box, Button, Card } from '@radix-ui/themes';
import { useNavigate, useParams } from 'react-router-dom';
import { ItemCard } from '@/components/ItemCard';
import type { Project, Item } from '@/types';

interface ProjectDetailProps {
  projects: Project[];
  onConfigureItem: (item: Item) => void;
}

export function ProjectDetail({ projects, onConfigureItem }: ProjectDetailProps) {
  const navigate = useNavigate();
  const { projectId } = useParams<{ projectId: string }>();
  
  const project = projects.find(p => p.id === projectId);

  if (!project) {
    return (
      <Flex direction="column" gap="6">
        <Heading size="8">Project Not Found</Heading>
        <Text color="gray">The requested project could not be found.</Text>
        <Button onClick={() => navigate('/')} style={{ alignSelf: 'flex-start' }}>
          Back to Dashboard
        </Button>
      </Flex>
    );
  }

  const getConfiguredCount = (project: Project) => {
    return project.items.filter(i => i.configured).length;
  };

  return (
    <Flex direction="column" gap="6">
      <Flex justify="between" align="center">
        <Box>
          <Heading size="8">{project.name}</Heading>
          <Text color="gray">{project.description}</Text>
        </Box>
        <Button variant="outline" onClick={() => navigate('/')}>
          Back to Dashboard
        </Button>
      </Flex>

      <Box style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: '24px' }}>
        {project.items.map((item) => (
          <ItemCard
            key={item.id}
            item={item}
            onConfigure={onConfigureItem}
          />
        ))}
      </Box>

      <Card style={{ marginTop: '32px' }}>
        <Flex direction="column" gap="3" p="4">
          <Heading size="5">Project Summary</Heading>
          <Flex direction="column" gap="2">
            <Text size="2">
              <Text weight="medium">Total Items: </Text>
              {project.items.length}
            </Text>
            <Text size="2">
              <Text weight="medium">Configured: </Text>
              {getConfiguredCount(project)}
            </Text>
            <Text size="2">
              <Text weight="medium">Remaining: </Text>
              {project.items.length - getConfiguredCount(project)}
            </Text>
            <Text size="2">
              <Text weight="medium">Progress: </Text>
              {Math.round((getConfiguredCount(project) / project.items.length) * 100)}%
            </Text>
          </Flex>
        </Flex>
      </Card>
    </Flex>
  );
}
