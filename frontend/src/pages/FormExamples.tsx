import { Flex, Heading, Text } from '@radix-ui/themes';
import { FormBuilder } from '@/components/FormBuilder';
import type { FormField } from '@/types';

const sampleFormFields: FormField[] = [
  {
    id: 'name',
    type: 'text',
    label: 'Project Name',
    placeholder: 'Enter project name',
    required: true,
  },
  {
    id: 'category',
    type: 'select',
    label: 'Category',
    placeholder: 'Select category',
    required: true,
    options: ['Web Application', 'Mobile App', 'Desktop Software', 'API Service'],
  },
  {
    id: 'priority',
    type: 'select',
    label: 'Priority',
    options: ['Low', 'Medium', 'High', 'Critical'],
  },
  {
    id: 'description',
    type: 'textarea',
    label: 'Description',
    placeholder: 'Describe your project...',
  },
  {
    id: 'notifications',
    type: 'checkbox',
    label: 'Enable notifications',
  },
  {
    id: 'publicAccess',
    type: 'checkbox',
    label: 'Allow public access',
  },
];

interface FormExamplesProps {
  onFormSubmit: (data: Record<string, any>) => void;
}

export function FormExamples({ onFormSubmit }: FormExamplesProps) {
  const handleCancel = () => {
    alert('Form cancelled');
  };

  return (
    <Flex direction="column" gap="6">
      <Heading size="8">Dynamic Form Examples</Heading>
      <Text color="gray">
        This shows a dynamically generated form with validation, different field types, and error handling.
        The form builder can create forms from configuration objects, making it easy to generate complex forms programmatically.
      </Text>
      <FormBuilder
        fields={sampleFormFields}
        title="Create New Project"
        submitLabel="Create Project"
        onSubmit={onFormSubmit}
        onCancel={handleCancel}
      />
    </Flex>
  );
}
