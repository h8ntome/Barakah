import test from 'node:test';
import assert from 'node:assert/strict';
import { conversationOptions } from '../src/utils/conversationOptions.js';

test('active conversation remains explicitly selectable when history page changes', () => {
  const record = {id: 'owned-selected', created_at: '2026-01-01T12:00:00Z'};
  assert.equal(conversationOptions([record], record.id).filter(x => x.value === record.id).length, 1);
  const nextPage = conversationOptions([], record.id);
  assert.equal(nextPage[0].label, 'New conversation');
  assert.equal(nextPage.find(x => x.value === record.id).label, 'Selected conversation · owned-');
  assert.deepEqual(conversationOptions([], ''), [{value: '', label: 'New conversation'}]);
});
