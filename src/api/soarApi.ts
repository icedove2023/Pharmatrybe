/**
 * SOAR Regional Resistance Surveillance API Client
 * Connects to runtime SOAR surveillance endpoints (/api/v1/soar)
 */

import { SoarDataPoint } from '@/types';


export interface SoarFilterParams {
  country?: string;
  pathogen?: string;
  antibiotic?: string;
  year?: number;
}

export const soarApi = {
  /**
   * GET /api/v1/soar
   * Returns SOAR surveillance dataset with optional server-side filtering
   */
  getSoarData: async (filters?: SoarFilterParams): Promise<SoarDataPoint[]> => {
    void filters;
    throw new Error('SOAR surveillance records are not exposed by the backend.');
  },

  /**
   * Returns unique countries in surveillance registry
   */
  getAvailableCountries: async (): Promise<string[]> => {
    throw new Error('SOAR surveillance filters are not exposed by the backend.');
  },

  /**
   * Returns unique pathogens in surveillance registry
   */
  getAvailablePathogens: async (): Promise<string[]> => {
    throw new Error('SOAR pathogen filters are not exposed by the backend.');
  },

  /**
   * Returns unique antibiotics in surveillance registry
   */
  getAvailableAntibiotics: async (): Promise<string[]> => {
    throw new Error('SOAR antibiotic filters are not exposed by the backend.');
  },
};
