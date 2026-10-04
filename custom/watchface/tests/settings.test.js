const assert = require('node:assert/strict');
const test = require('node:test');
const config = require('../src/pkjs/config');
const manifest = require('../package.json');

function flatten(items) {
  return items.flatMap(item => [item, ...flatten(item.items || [])]);
}

test('watch notification counter is an optional, default-off bottom bezel setting', () => {
  const section = config.find(item => item.items && item.items.some(
    child => child.type === 'heading' && child.defaultValue === 'Bottom bezel'));
  const toggle = section.items.find(item => item.messageKey === 'ShowNotifications');
  assert.ok(toggle, 'Missing watch notification toggle');
  assert.equal(toggle.type, 'toggle');
  assert.equal(toggle.defaultValue, false);
  assert.ok(manifest.pebble.messageKeys.includes('ShowNotifications'));
  assert.ok(flatten(config).some(item => item.messageKey === 'BezelLabel'));
});

test('notification number defaults on and the icon selector defaults to envelope', () => {
  const items = flatten(config);
  const number = items.find(item => item.messageKey === 'ShowNotificationNumber');
  assert.ok(number, 'Missing notification number toggle');
  assert.equal(number.type, 'toggle');
  assert.equal(number.defaultValue, true);
  const icon = items.find(item => item.messageKey === 'NotificationIcon');
  assert.ok(icon, 'Missing notification icon selector');
  assert.equal(icon.defaultValue, 'envelope');
  assert.deepEqual(icon.options.map(option => option.value), ['envelope', 'bell', 'dot']);
  assert.ok(manifest.pebble.messageKeys.includes('ShowNotificationNumber'));
  assert.ok(manifest.pebble.messageKeys.includes('NotificationIcon'));
});
