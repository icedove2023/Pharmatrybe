import { PluginContractError } from './errors';
import { assertValidPluginContract } from './validation';
import { PluginInputContract } from './types';

export class PluginContractRegistry {
  private readonly contracts = new Map<string, PluginInputContract>();

  register(contract: PluginInputContract): void {
    assertValidPluginContract(contract);
    const key = `${contract.pluginId}@${contract.contractVersion}`;
    if (this.contracts.has(key)) throw new PluginContractError('CONTRACT_INVALID', `Contract ${key} is already registered.`);
    this.contracts.set(key, contract);
  }

  resolve(pluginId: string, contractVersion: string): PluginInputContract {
    const contract = this.contracts.get(`${pluginId}@${contractVersion}`);
    if (!contract) throw new PluginContractError('CONTRACT_NOT_FOUND', `No contract is registered for ${pluginId}@${contractVersion}.`);
    if (contract.status === 'deprecated') throw new PluginContractError('CONTRACT_VERSION_UNSUPPORTED', `Contract ${pluginId}@${contractVersion} is deprecated.`);
    if (contract.status !== 'approved') throw new PluginContractError('CONTRACT_NOT_APPROVED', `Contract ${pluginId}@${contractVersion} is not approved.`);
    return contract;
  }

  has(pluginId: string, contractVersion: string): boolean { return this.contracts.has(`${pluginId}@${contractVersion}`); }
  registerIfAbsent(contract: PluginInputContract): void {
    if (!this.has(contract.pluginId, contract.contractVersion)) this.register(contract);
  }
  validate(contract: PluginInputContract): void { assertValidPluginContract(contract); }
  clear(): void { this.contracts.clear(); }
}

export const pluginContractRegistry = new PluginContractRegistry();
