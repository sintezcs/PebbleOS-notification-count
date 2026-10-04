/* SPDX-FileCopyrightText: 2026 Notification count API contributors */
/* SPDX-License-Identifier: Apache-2.0 */

#pragma once

#include <stdint.h>

//! @addtogroup Foundation
//! @{
//!   @addtogroup EventService
//!   @{
//!     @addtogroup NotificationService
//! \brief Read-only access to the number of notifications stored on the watch.
//! @{

//! Get a snapshot of the number of retained notifications on this watch.
//! Read notifications are included; deleted notifications are excluded.
//! Each notification is counted separately, even when the system notification
//! list groups several notifications into one row. No content is exposed.
//! Notifications are cleared when the watch restarts. This is a watch-local
//! count, independent of the phone's active notifications or unread messages.
//! @return The count, or zero when notification storage cannot be read.
uint32_t notification_service_peek_count(void);

//!     @} // group NotificationService
//!   @} // group EventService
//! @} // group Foundation
