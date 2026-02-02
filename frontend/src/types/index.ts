export interface Item {
  id: string;
  name: string;
  description: string;
  category: ItemCategory;
  configured: boolean;
  config?: ItemConfig;
}

export interface ItemConfig {
  [key: string]: any;
}

// Example configurations for different item types
export interface BasicConfig extends ItemConfig {
  type: string;
  size: number;
  protocol: string;
  features: string[];
}

export interface AdvancedConfig extends ItemConfig {
  components: string[];
  algorithms: string[];
  performance: string;
  level: 'Basic' | 'Intermediate' | 'Advanced' | 'Expert';
}

export interface SecurityConfig extends ItemConfig {
  encryptionType: string;
  keyLength: number;
  secureEnabled: boolean;
  certificateManagement: boolean;
}

export interface SystemConfig extends ItemConfig {
  systemType: string;
  updateMechanism: string;
  backupSupport: boolean;
  compressionEnabled: boolean;
}

export interface Project {
  id: string;
  name: string;
  description: string;
  createdAt: Date;
  updatedAt: Date;
  items: Item[];
}

export type ItemCategory = 'basic' | 'advanced' | 'security' | 'system' | 'custom';

export const ITEM_CATEGORIES: Record<ItemCategory, string> = {
  basic: 'Basic Components',
  advanced: 'Advanced Features',
  security: 'Security & Privacy',
  system: 'System Configuration',
  custom: 'Custom Solutions'
};

// Example data structure for tables
export interface TableData {
  id: string;
  name: string;
  status: 'active' | 'inactive' | 'pending';
  value: number;
  category: string;
  lastUpdated: Date;
}

// Form field types
export interface FormField {
  id: string;
  type: 'text' | 'number' | 'select' | 'checkbox' | 'textarea';
  label: string;
  placeholder?: string;
  required?: boolean;
  options?: string[];
  value?: any;
}
