import { useState } from "react";
import { Box, Flex, Text, TextField, Select, Checkbox, Button, Card, Heading } from "@radix-ui/themes";
import type { FormField } from "@/types";

interface FormBuilderProps {
  fields: FormField[];
  onSubmit: (data: Record<string, any>) => void;
  onCancel?: () => void;
  title?: string;
  submitLabel?: string;
}

export function FormBuilder({
  fields,
  onSubmit,
  onCancel,
  title = "Form",
  submitLabel = "Submit"
}: FormBuilderProps) {
  const [formData, setFormData] = useState<Record<string, any>>({});
  const [errors, setErrors] = useState<Record<string, string>>({});

  const handleChange = (fieldId: string, value: any) => {
    setFormData(prev => ({
      ...prev,
      [fieldId]: value
    }));
    
    // Clear error when user starts typing
    if (errors[fieldId]) {
      setErrors(prev => ({
        ...prev,
        [fieldId]: ''
      }));
    }
  };

  const validateForm = () => {
    const newErrors: Record<string, string> = {};
    
    fields.forEach(field => {
      if (field.required && !formData[field.id]) {
        newErrors[field.id] = `${field.label} is required`;
      }
    });
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (validateForm()) {
      onSubmit(formData);
    }
  };

  const renderField = (field: FormField) => {
    const hasError = !!errors[field.id];
    
    switch (field.type) {
      case 'text':
      case 'number':
        return (
          <Flex direction="column" gap="2" key={field.id}>
            <Text size="2" weight="bold">
              {field.label}
              {field.required && <Text color="red"> *</Text>}
            </Text>
            <TextField.Root
              type={field.type}
              value={formData[field.id] || ''}
              onChange={(e) => handleChange(field.id, e.target.value)}
              placeholder={field.placeholder}
              style={{
                borderColor: hasError ? 'var(--red-7)' : undefined
              }}
            />
            {hasError && (
              <Text size="1" color="red">
                {errors[field.id]}
              </Text>
            )}
          </Flex>
        );
        
      case 'select':
        return (
          <Flex direction="column" gap="2" key={field.id}>
            <Text size="2" weight="bold">
              {field.label}
              {field.required && <Text color="red"> *</Text>}
            </Text>
            <Select.Root
              value={formData[field.id] || ''}
              onValueChange={(value) => handleChange(field.id, value)}
            >
              <Select.Trigger 
                placeholder={field.placeholder || 'Select option'}
                style={{
                  borderColor: hasError ? 'var(--red-7)' : undefined
                }}
              />
              <Select.Content>
                {field.options?.map(option => (
                  <Select.Item key={option} value={option}>
                    {option}
                  </Select.Item>
                ))}
              </Select.Content>
            </Select.Root>
            {hasError && (
              <Text size="1" color="red">
                {errors[field.id]}
              </Text>
            )}
          </Flex>
        );
        
      case 'checkbox':
        return (
          <Flex align="center" gap="2" key={field.id}>
            <Checkbox
              checked={formData[field.id] || false}
              onCheckedChange={(checked) => handleChange(field.id, checked)}
            />
            <Text size="2" weight="bold">
              {field.label}
              {field.required && <Text color="red"> *</Text>}
            </Text>
            {hasError && (
              <Text size="1" color="red" ml="6">
                {errors[field.id]}
              </Text>
            )}
          </Flex>
        );
        
      case 'textarea':
        return (
          <Flex direction="column" gap="2" key={field.id}>
            <Text size="2" weight="bold">
              {field.label}
              {field.required && <Text color="red"> *</Text>}
            </Text>
            <TextField.Root
              value={formData[field.id] || ''}
              onChange={(e) => handleChange(field.id, e.target.value)}
              placeholder={field.placeholder}
              style={{
                minHeight: '80px',
                borderColor: hasError ? 'var(--red-7)' : undefined
              }}
            />
            {hasError && (
              <Text size="1" color="red">
                {errors[field.id]}
              </Text>
            )}
          </Flex>
        );
        
      default:
        return null;
    }
  };

  return (
    <Card style={{ maxWidth: '500px' }}>
      <Box p="4">
        <Flex direction="column" gap="4">
          <Heading size="5">{title}</Heading>
          
          <form onSubmit={handleSubmit}>
            <Flex direction="column" gap="4">
              {fields.map(renderField)}
              
              <Flex gap="3" justify="end" mt="4">
                {onCancel && (
                  <Button type="button" variant="soft" color="gray" onClick={onCancel}>
                    Cancel
                  </Button>
                )}
                <Button type="submit">
                  {submitLabel}
                </Button>
              </Flex>
            </Flex>
          </form>
        </Flex>
      </Box>
    </Card>
  );
}
