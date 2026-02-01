import { useState } from "react";
import { Dialog, Button, Flex, Text, TextField, Select, Checkbox } from "@radix-ui/themes";
import { Cross2Icon } from "@radix-ui/react-icons";
import type { Item, ItemConfig, BasicConfig, AdvancedConfig, SecurityConfig, SystemConfig } from "@/types";

interface ConfigurationDialogProps {
  item: Item | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSave: (item: Item, config: ItemConfig) => void;
}

export function ConfigurationDialog({ item, open, onOpenChange, onSave }: ConfigurationDialogProps) {
  const [config, setConfig] = useState<ItemConfig>({});

  if (!item) return null;

  const handleSave = () => {
    onSave(item, config);
    onOpenChange(false);
  };

  const handleClose = () => {
    setConfig({});
    onOpenChange(false);
  };

  const renderConfigForm = () => {
    switch (item.category) {
      case 'basic':
        return (
          <Flex direction="column" gap="4">
            <Flex direction="column" gap="2">
              <Text size="2" weight="bold">Component Type</Text>
              <TextField.Root
                value={(config as BasicConfig).type || ''}
                onChange={(e) => setConfig({ ...config, type: e.target.value })}
                placeholder="e.g., Standard, Premium, Custom"
              />
            </Flex>
            <Flex direction="column" gap="2">
              <Text size="2" weight="bold">Size/Capacity</Text>
              <TextField.Root
                type="number"
                value={(config as BasicConfig).size?.toString() || ''}
                onChange={(e) => setConfig({ ...config, size: parseInt(e.target.value) || 0 })}
                placeholder="100"
              />
            </Flex>
            <Flex direction="column" gap="2">
              <Text size="2" weight="bold">Protocol/Interface</Text>
              <TextField.Root
                value={(config as BasicConfig).protocol || ''}
                onChange={(e) => setConfig({ ...config, protocol: e.target.value })}
                placeholder="HTTP, WebSocket, REST API"
              />
            </Flex>
            <Flex direction="column" gap="2">
              <Text size="2" weight="bold">Additional Features</Text>
              <TextField.Root
                value={(config as BasicConfig).features?.join(', ') || ''}
                onChange={(e) => setConfig({ ...config, features: e.target.value.split(', ').filter(f => f.trim()) })}
                placeholder="Feature 1, Feature 2, Feature 3"
              />
            </Flex>
          </Flex>
        );
      case 'advanced':
        return (
          <Flex direction="column" gap="4">
            <Flex direction="column" gap="2">
              <Text size="2" weight="bold">Components</Text>
              <TextField.Root
                value={(config as AdvancedConfig).components?.join(', ') || ''}
                onChange={(e) => setConfig({ ...config, components: e.target.value.split(', ').filter(c => c.trim()) })}
                placeholder="Component A, Component B, Component C"
              />
            </Flex>
            <Flex direction="column" gap="2">
              <Text size="2" weight="bold">Algorithms/Methods</Text>
              <TextField.Root
                value={(config as AdvancedConfig).algorithms?.join(', ') || ''}
                onChange={(e) => setConfig({ ...config, algorithms: e.target.value.split(', ').filter(a => a.trim()) })}
                placeholder="Algorithm 1, Method 2, Process 3"
              />
            </Flex>
            <Flex direction="column" gap="2">
              <Text size="2" weight="bold">Performance Level</Text>
              <Select.Root
                value={(config as AdvancedConfig).level || ''}
                onValueChange={(value) => setConfig({ ...config, level: value })}
              >
                <Select.Trigger placeholder="Select Level" />
                <Select.Content>
                  <Select.Item value="Basic">Basic</Select.Item>
                  <Select.Item value="Intermediate">Intermediate</Select.Item>
                  <Select.Item value="Advanced">Advanced</Select.Item>
                  <Select.Item value="Expert">Expert</Select.Item>
                </Select.Content>
              </Select.Root>
            </Flex>
            <Flex direction="column" gap="2">
              <Text size="2" weight="bold">Performance Rating</Text>
              <TextField.Root
                value={(config as AdvancedConfig).performance || ''}
                onChange={(e) => setConfig({ ...config, performance: e.target.value })}
                placeholder="High, Medium, Low"
              />
            </Flex>
          </Flex>
        );
      case 'security':
        return (
          <Flex direction="column" gap="4">
            <Flex direction="column" gap="2">
              <Text size="2" weight="bold">Encryption Type</Text>
              <TextField.Root
                value={(config as SecurityConfig).encryptionType || ''}
                onChange={(e) => setConfig({ ...config, encryptionType: e.target.value })}
                placeholder="AES-256, RSA, SHA-256"
              />
            </Flex>
            <Flex direction="column" gap="2">
              <Text size="2" weight="bold">Key Length</Text>
              <TextField.Root
                type="number"
                value={(config as SecurityConfig).keyLength?.toString() || ''}
                onChange={(e) => setConfig({ ...config, keyLength: parseInt(e.target.value) || 0 })}
                placeholder="256"
              />
            </Flex>
            <Flex align="center" gap="2">
              <Checkbox
                checked={(config as SecurityConfig).secureEnabled || false}
                onCheckedChange={(checked) => setConfig({ ...config, secureEnabled: checked as boolean })}
              />
              <Text size="2" weight="bold">Enable Secure Mode</Text>
            </Flex>
            <Flex align="center" gap="2">
              <Checkbox
                checked={(config as SecurityConfig).certificateManagement || false}
                onCheckedChange={(checked) => setConfig({ ...config, certificateManagement: checked as boolean })}
              />
              <Text size="2" weight="bold">Certificate Management</Text>
            </Flex>
          </Flex>
        );
      case 'system':
        return (
          <Flex direction="column" gap="4">
            <Flex direction="column" gap="2">
              <Text size="2" weight="bold">System Type</Text>
              <TextField.Root
                value={(config as SystemConfig).systemType || ''}
                onChange={(e) => setConfig({ ...config, systemType: e.target.value })}
                placeholder="Primary, Secondary, Backup"
              />
            </Flex>
            <Flex direction="column" gap="2">
              <Text size="2" weight="bold">Update Mechanism</Text>
              <TextField.Root
                value={(config as SystemConfig).updateMechanism || ''}
                onChange={(e) => setConfig({ ...config, updateMechanism: e.target.value })}
                placeholder="Automatic, Manual, Scheduled"
              />
            </Flex>
            <Flex align="center" gap="2">
              <Checkbox
                checked={(config as SystemConfig).backupSupport || false}
                onCheckedChange={(checked) => setConfig({ ...config, backupSupport: checked as boolean })}
              />
              <Text size="2" weight="bold">Backup Support</Text>
            </Flex>
            <Flex align="center" gap="2">
              <Checkbox
                checked={(config as SystemConfig).compressionEnabled || false}
                onCheckedChange={(checked) => setConfig({ ...config, compressionEnabled: checked as boolean })}
              />
              <Text size="2" weight="bold">Enable Compression</Text>
            </Flex>
          </Flex>
        );
      default:
        return (
          <Flex direction="column" gap="4">
            <Text>Custom configuration form for {item.category} items.</Text>
            <Flex direction="column" gap="2">
              <Text size="2" weight="bold">Custom Setting</Text>
              <TextField.Root
                value={config.customValue || ''}
                onChange={(e) => setConfig({ ...config, customValue: e.target.value })}
                placeholder="Enter custom value"
              />
            </Flex>
          </Flex>
        );
    }
  };

  return (
    <Dialog.Root open={open} onOpenChange={onOpenChange}>
      <Dialog.Content maxWidth="500px">
        <Dialog.Title>
          Configure {item.name}
        </Dialog.Title>
        
        <Dialog.Description size="2" mb="4">
          Configure the settings for {item.name}. Make changes and click save when you're done.
        </Dialog.Description>

        {renderConfigForm()}

        <Flex gap="3" mt="6" justify="end">
          <Button variant="soft" color="gray" onClick={handleClose}>
            Cancel
          </Button>
          <Button onClick={handleSave}>
            Save configuration
          </Button>
        </Flex>

        <Dialog.Close>
          <Button
            variant="ghost"
            color="gray"
            size="2"
            style={{
              position: 'absolute',
              top: '12px',
              right: '12px',
            }}
            onClick={handleClose}
          >
            <Cross2Icon />
          </Button>
        </Dialog.Close>
      </Dialog.Content>
    </Dialog.Root>
  );
}
