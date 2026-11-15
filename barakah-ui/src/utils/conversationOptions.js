export function conversationOptions(conversations, selectedId) {
  const options = conversations.map((item) => ({
    value: item.id,
    label: `${item.created_at.slice(0, 16).replace('T', ' ')} · ${item.id.slice(0, 6)}`,
  }));
  if (selectedId && !options.some((option) => option.value === selectedId)) {
    options.unshift({ value: selectedId, label: `Selected conversation · ${selectedId.slice(0, 6)}` });
  }
  return [{ value: '', label: 'New conversation' }, ...options];
}
