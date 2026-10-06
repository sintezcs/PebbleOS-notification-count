/* SPDX-FileCopyrightText: 2026 Notification count API contributors */
/* SPDX-License-Identifier: Apache-2.0 */

#include "syscall/syscall_internal.h"

#include "pbl/services/notifications/notification_storage.h"

static bool prv_count_notification(void *context, SerializedTimelineItemHeader *header) {
  uint32_t *count = context;
  ++*count;
  return true;
}

DEFINE_SYSCALL(uint32_t, sys_notification_get_count) {
  uint32_t count = 0;
  // The iterator holds the storage mutex and skips deleted entries.
  notification_storage_iterate(prv_count_notification, &count);
  return count;
}
