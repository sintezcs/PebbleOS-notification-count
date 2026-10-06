/* SPDX-FileCopyrightText: 2026 Notification count API contributors */
/* SPDX-License-Identifier: Apache-2.0 */

#include "notification_service.h"

#include "syscall/syscall.h"

uint32_t notification_service_peek_count(void) {
  return sys_notification_get_count();
}
