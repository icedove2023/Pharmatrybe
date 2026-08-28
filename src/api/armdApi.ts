/**
 * ARMD Deep Molecular Resistance API Client
 * Connects to runtime ARMD endpoints (/api/v1/armd)
 */

import { ArmdModelSummary, ArmdModelDetail } from '@/types';


export const armdApi = {
  /**
   * GET /api/v1/armd
   * Returns list of registered ARMD predictive ML models
   */
  getArmdModels: async (): Promise<ArmdModelSummary[]> => {
    throw new Error('ARMD model registry is not exposed by the backend.');
  },

  /**
   * GET /api/v1/armd/{model_id}
   * Returns complete model architecture, performance metrics, and feature importances
   */
  getArmdModelDetails: async (id: string): Promise<ArmdModelDetail | null> => {
    void id;
    throw new Error('ARMD model details are not exposed by the backend.');
  },
};
