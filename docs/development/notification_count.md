# Reading the watch notification count

The native SDK exposes a read-only count of notifications retained by this watch:

```c
uint32_t count = notification_service_peek_count();
```

This returns the number of non-deleted notification records in watch storage.
Viewed records are included. Multiple notifications grouped under one sender in
the system list are counted individually. This does not read the phone's active
notifications, and it does not expose titles, message bodies, application names,
or IDs. Storage is cleared on reboot, as before. An unreadable store returns zero.

The snapshot is taken under the existing recursive notification-storage mutex.
It traverses record headers without deserializing payloads or allocating message
buffers. Apps should refresh on launch or focus and at an appropriate interval;
the snapshot API does not subscribe to changes.

This API is registered at exported-symbol revision 110 and process SDK version
5.0x6c. Build the firmware and its SDK together following
[SDK export instructions](sdk_export.md). A watchface built against this revision
requires firmware containing the same ABI. The firmware's SDK compatibility check
rejects a newer app on older firmware.

The notification-storage test exercises the public wrapper and privileged syscall
against the host fake flash filesystem, including viewed records, deletion,
clearing, and counts exceeding a two-digit display. Run:

```sh
pbl test -R notification_storage
```
