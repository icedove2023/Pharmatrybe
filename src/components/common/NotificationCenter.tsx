import React from 'react';
import { Bell, CheckCircle2, Info, AlertOctagon, AlertTriangle, X } from 'lucide-react';
import { motion, AnimatePresence } from 'motion/react';
import { useNotificationStore } from '@/stores/notificationStore';
import type { AppNotification } from '@/stores/notificationStore';

const levelStyles = {
  critical: { icon: AlertOctagon, tone: 'text-[var(--color-safety-critical)]', surface: 'border-[var(--color-safety-critical-border)] bg-[var(--color-safety-critical-bg)]' },
  warning: { icon: AlertTriangle, tone: 'text-[var(--color-safety-warning)]', surface: 'border-[var(--color-safety-warning-border)] bg-[var(--color-safety-warning-bg)]' },
  info: { icon: Info, tone: 'text-[var(--color-safety-info)]', surface: 'border-[var(--color-safety-info-border)] bg-[var(--color-safety-info-bg)]' },
  success: { icon: CheckCircle2, tone: 'text-[var(--color-safety-success)]', surface: 'border-[var(--color-safety-success-border)] bg-[var(--color-safety-success-bg)]' },
} as const;

function NotificationItem({ notification, onDismiss }: { notification: AppNotification; onDismiss: () => void }) {
  const style = levelStyles[notification.level];
  const Icon = style.icon;
  return (
    <div className={`flex gap-2.5 rounded-[var(--radius-lg)] border p-3 shadow-clinical-md backdrop-blur-sm ${style.surface}`}>
      <Icon className={`mt-0.5 h-4 w-4 shrink-0 ${style.tone}`} aria-hidden="true" />
      <div className="min-w-0 flex-1">
        <p className={`text-[11px] font-semibold ${style.tone}`}>{notification.title}</p>
        {notification.message && <p className="mt-0.5 text-[11px] leading-relaxed text-slate-text-secondary">{notification.message}</p>}
        <time className="mt-1 block text-[10px] text-slate-text-muted">{new Date(notification.createdAt).toLocaleString()}</time>
      </div>
      {!notification.dismissed && (
        <button type="button" onClick={onDismiss} aria-label={`Dismiss ${notification.title}`} className="h-fit rounded p-0.5 text-slate-text-muted hover:bg-black/5 hover:text-slate-text-primary">
          <X className="h-3.5 w-3.5" aria-hidden="true" />
        </button>
      )}
    </div>
  );
}

export function NotificationCenter() {
  const [isOpen, setIsOpen] = React.useState(false);
  const notifications = useNotificationStore((state) => state.notifications);
  const dismiss = useNotificationStore((state) => state.dismiss);
  const active = notifications.filter((item) => !item.dismissed);
  const unreadCount = active.length;

  return (
    <div className="relative">
      <button
        type="button"
        onClick={() => setIsOpen((open) => !open)}
        className="focus-clinical relative rounded-[var(--radius-sm)] p-2 text-slate-text-secondary hover:bg-slate-inset-hover"
        title="Open notifications"
        aria-label={`Open notifications${unreadCount ? ` (${unreadCount} active)` : ''}`}
        aria-expanded={isOpen}
      >
        <Bell className="h-4 w-4" aria-hidden="true" />
        {unreadCount > 0 && <span className="absolute right-1 top-1 flex h-2 w-2 rounded-full bg-[var(--color-safety-critical)] ring-2 ring-slate-surface" />}
      </button>

      <AnimatePresence>
        {active.length > 0 && (
          <div className="pointer-events-none fixed inset-x-4 top-20 z-40 flex flex-col items-end gap-2 sm:inset-x-auto sm:right-6 sm:w-96">
            {active.slice(0, 3).map((notification) => (
              <motion.div
                key={notification.id}
                initial={{ opacity: 0, y: -8, scale: 0.98 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                exit={{ opacity: 0, x: 16 }}
                className="pointer-events-auto w-full shadow-lg"
              >
                <NotificationItem notification={notification} onDismiss={() => dismiss(notification.id)} />
              </motion.div>
            ))}
          </div>
        )}
      </AnimatePresence>

      {isOpen && (
        <div className="absolute right-0 z-50 mt-2 w-[min(22rem,calc(100vw-2rem))] origin-top-right animate-fade-in rounded-[var(--radius-lg)] border border-slate-border bg-slate-surface-raised p-4 shadow-clinical-lg">
          <div className="mb-3 flex items-center justify-between border-b border-slate-border-subtle pb-2">
            <div>
              <h4 className="text-xs font-semibold text-slate-text-primary">Notification history</h4>
              <p className="mt-0.5 text-[10px] text-slate-text-muted">Alerts remain available for future reference.</p>
            </div>
            {notifications.length > 0 && (
              <button type="button" onClick={() => useNotificationStore.getState().clearHistory()} className="text-[10px] font-semibold text-slate-text-secondary hover:text-slate-text-primary">
                Clear history
              </button>
            )}
          </div>
          <div className="max-h-96 space-y-2 overflow-y-auto">
            {notifications.length === 0 ? (
              <p className="py-4 text-center text-xs text-slate-text-muted">No notifications.</p>
            ) : notifications.map((notification) => (
              <React.Fragment key={notification.id}>
                <NotificationItem notification={notification} onDismiss={() => dismiss(notification.id)} />
              </React.Fragment>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export function NotificationHistory() {
  const notifications = useNotificationStore((state) => state.notifications);
  const dismiss = useNotificationStore((state) => state.dismiss);
  return (
    <section className="rounded-[var(--radius-lg)] border border-slate-border bg-slate-surface p-5">
      <div className="mb-3 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-slate-text-primary">Notification history</h3>
          <p className="mt-0.5 text-[11px] text-slate-text-muted">System alerts and workflow events retained for reference.</p>
        </div>
        <Bell className="h-4 w-4 text-[var(--color-clinical-400)]" aria-hidden="true" />
      </div>
      <div className="space-y-2">
        {notifications.length === 0 ? <p className="rounded-md border border-dashed border-slate-border p-5 text-center text-xs text-slate-text-muted">No notifications recorded.</p> : notifications.slice(0, 10).map((notification) => <React.Fragment key={notification.id}><NotificationItem notification={notification} onDismiss={() => dismiss(notification.id)} /></React.Fragment>)}
      </div>
    </section>
  );
}
