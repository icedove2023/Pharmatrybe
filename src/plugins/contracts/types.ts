export type ContractStatus = 'approved' | 'unsupported' | 'deprecated' | 'invalid';
export type JsonSchemaType = 'string' | 'number' | 'integer' | 'boolean' | 'array' | 'object';
export type FieldWidget = 'text' | 'textarea' | 'number' | 'checkbox' | 'select' | 'radio' | 'date' | 'date-time' | 'multi-select';

export interface JsonSchema {
  $schema?: string;
  type?: JsonSchemaType;
  title?: string;
  description?: string;
  properties?: Record<string, JsonSchema>;
  required?: string[];
  enum?: Array<string | number | boolean | null>;
  items?: JsonSchema;
  minimum?: number;
  maximum?: number;
  minLength?: number;
  maxLength?: number;
  pattern?: string;
  format?: string;
  additionalProperties?: boolean;
  [key: string]: unknown;
}

export interface ContractProvenance {
  owner: string;
  source: string;
  artifact: string;
  artifactVersion: string;
  approvedBy: string;
  approvedAt: string;
}

export interface UiField {
  field: string;
  label?: string;
  helpText?: string;
  widget?: FieldWidget;
  order?: number;
  section?: string;
}

export interface UiSchema {
  fields: UiField[];
}

export interface PluginInputContract {
  pluginId: string;
  contractId: string;
  contractVersion: string;
  schemaVersion: string;
  displayName: string;
  description?: string;
  status: ContractStatus;
  provenance: ContractProvenance;
  inputSchema: JsonSchema;
  uiSchema?: UiSchema;
  requiredFields?: string[];
  routingRequirements?: string[];
  supportedExecutionMode: 'sync';
}

export interface FormValidationIssue {
  path: string;
  message: string;
  keyword?: string;
}

export interface FormValidationResult {
  valid: boolean;
  issues: FormValidationIssue[];
}
