export type ContractErrorCode =
  | 'CONTRACT_NOT_FOUND'
  | 'CONTRACT_NOT_APPROVED'
  | 'CONTRACT_VERSION_UNSUPPORTED'
  | 'CONTRACT_INVALID'
  | 'FORM_VALIDATION_ERROR'
  | 'PLUGIN_ADAPTER_ERROR';

export class PluginContractError extends Error {
  readonly code: ContractErrorCode;
  readonly details?: unknown;

  constructor(code: ContractErrorCode, message: string, details?: unknown) {
    super(message);
    this.name = 'PluginContractError';
    this.code = code;
    this.details = details;
  }
}
