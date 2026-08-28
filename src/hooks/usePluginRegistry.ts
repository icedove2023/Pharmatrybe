import { useQuery } from '@tanstack/react-query';
import { adminApi } from '@/api';
import { PluginInfo } from '@/types';
import { useAuthStore } from '@/stores/authStore';

/**
 * Single source of truth for the registered plugin list. Reused by Sidebar,
 * DashboardView's "Registered integrations" popover, and plugin explorer
 * views so nav, dashboard, and explorers never drift from what the backend
 * actually reports.
 */
export function usePluginRegistry() {
  const isAuthenticated = useAuthStore((state) => state.status === 'authenticated');

  return useQuery<PluginInfo[]>({
    queryKey: ['registeredPlugins'],
    queryFn: () => adminApi.getRegisteredPlugins(),
    enabled: isAuthenticated,
    staleTime: 30_000,
  });
}
