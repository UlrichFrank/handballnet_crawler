import { Flex, Heading, Button, Card, Text, Box } from '@radix-ui/themes';
import { PlusIcon } from '@radix-ui/react-icons';
import { useNavigate } from 'react-router-dom';
import type { Project } from '@/types';

interface DashboardProps {
  projects: Project[];
  onCreateProject: () => void;
  onSelectProject: (project: Project) => void;
}

export function Dashboard({ projects, onCreateProject, onSelectProject }: DashboardProps) {
  const navigate = useNavigate();

  const getConfiguredCount = (project: Project) => {
    return project.items.filter(i => i.configured).length;
  };

  const handleOpenProject = (project: Project) => {
    onSelectProject(project);
    navigate(`/project/${project.id}`);
  };

  return (
    <Flex direction="column" gap="6">
      <Flex justify="between" align="center">
        <Heading size="8">UI Component Demo</Heading>
        <Button onClick={onCreateProject}>
          <PlusIcon />
          New Project
        </Button>
      </Flex>

      {projects.length === 0 ? (
        <Card style={{ maxWidth: '600px' }}>
          <Flex direction="column" gap="3" p="4">
            <Heading size="5">Welcome to the UI Mockup Template</Heading>
            <Text color="gray">
              This template demonstrates various UI components and patterns commonly used in modern web applications.
              Create your first project to explore the different components and features.
            </Text>
            <Button onClick={onCreateProject} style={{ alignSelf: 'flex-start' }}>
              <PlusIcon />
              Create Demo Project
            </Button>
          </Flex>
        </Card>
      ) : (
        <Box style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: '24px' }}>
          {projects.map((project) => (
            <Card key={project.id} style={{ cursor: 'pointer' }}>
              <Flex direction="column" gap="3" p="4">
                <Heading size="4">{project.name}</Heading>
                <Text color="gray" size="2">{project.description}</Text>
                <Flex direction="column" gap="2">
                  <Text size="2">
                    <Text weight="medium">Items configured: </Text>
                    {getConfiguredCount(project)}/{project.items.length}
                  </Text>
                  <Text size="2" color="gray">
                    Last updated: {new Date(project.updatedAt).toLocaleDateString()}
                  </Text>
                  <Button onClick={() => handleOpenProject(project)} style={{ marginTop: '8px' }}>
                    Open Project
                  </Button>
                </Flex>
              </Flex>
            </Card>
          ))}
        </Box>
      )}
    </Flex>
  );
}
