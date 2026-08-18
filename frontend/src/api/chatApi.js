const chatEndpoint = '/api/v1/chat';

export async function sendChatMessage(message, conversationId) {
  const requestBody = { message };

  if (conversationId) {
    requestBody.conversation_id = conversationId;
  }

  const response = await fetch(chatEndpoint, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(requestBody),
  });

  if (!response.ok) {
    throw new Error('Chat request failed');
  }

  return response.json();
}