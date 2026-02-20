# AI Reviews

AI-powered conversational review writing using GPT-4.1. The user chats naturally about their experience, the AI detects relevant tags (add/remove), and generates a polished review description.

**Flow:**
1. **Start** → AI sends a friendly opening question
2. **Message** → User chats back and forth (AI calls `add_tag`/`remove_tag` tools behind the scenes)
3. **Generate** → AI writes the final review description from the conversation
4. **Confirm** → Creates a real `Review` object and applies tag changes to the business

All endpoints require **authentication** and **verified email**.

## List AI Review Sessions

```
GET /api/ai-reviews/
```

Returns all of the current user's AI review chat sessions.

**Response:**

```json
[
  {
    "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "business": 42,
    "business_name": "Café Luna",
    "user": 1,
    "username": "hanyang",
    "rating": 4,
    "status": "active",
    "conversation": [
      { "role": "assistant", "content": "Hey! You gave Café Luna 4 stars..." },
      { "role": "user", "content": "The oat milk lattes are amazing" }
    ],
    "tags_to_add": ["oat-milk", "cozy"],
    "tags_to_remove": [],
    "generated_description": "",
    "review": null,
    "created_at": "2025-02-20T01:23:45Z",
    "updated_at": "2025-02-20T01:24:12Z"
  }
]
```

## Retrieve AI Review Session

```
GET /api/ai-reviews/{id}/
```

Returns a single chat session by UUID.

## Start AI Review Chat

```
POST /api/ai-reviews/start/
```

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `business` | int | Yes | Business ID to review |
| `rating` | int (1-5) | Yes | Star rating |

**Request:**

```json
{ "business": 42, "rating": 4 }
```

**Response (201 Created):**

```json
{
  "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "business": 42,
  "business_name": "Café Luna",
  "user": 1,
  "username": "hanyang",
  "rating": 4,
  "status": "active",
  "conversation": [
    {
      "role": "assistant",
      "content": "Hey! You gave Café Luna 4 stars — sounds like a solid spot! What stood out most about your visit?"
    }
  ],
  "tags_to_add": [],
  "tags_to_remove": [],
  "generated_description": "",
  "review": null,
  "created_at": "2025-02-20T01:23:45Z",
  "updated_at": "2025-02-20T01:23:45Z"
}
```

**Notes:**
- If the user already has an active session for the same business, returns the existing session (200) instead of creating a new one.
- If the user has already reviewed the business, returns a validation error.

**Errors:**

| Status | Reason |
|--------|--------|
| 400 | Already reviewed this business |
| 503 | AI service temporarily unavailable |

## Send Message

```
POST /api/ai-reviews/{id}/message/
```

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `message` | string | Yes | User's reply (max 2000 chars) |

**Request:**

```json
{ "message": "The oat milk lattes are incredible, and the atmosphere is super cozy" }
```

**Response (200):**

```json
{
  "reply": "Oat milk lattes AND a cozy vibe — that's a winning combo! Was it more of a quick grab-and-go, or did you settle in for a while?",
  "tags_added": ["oat-milk", "cozy"],
  "tags_removed": [],
  "session": { /* full ReviewChat session object (same shape as List response) */ }
}
```

**How tags work:** The AI uses OpenAI function-calling tools (`add_tag`, `remove_tag`) during the conversation. Tags are accumulated in `tags_to_add` / `tags_to_remove` on the session and applied to the business only when the review is confirmed.

**Errors:**

| Status | Reason |
|--------|--------|
| 400 | Session is no longer active |
| 503 | AI service temporarily unavailable |

## Generate Review

```
POST /api/ai-reviews/{id}/generate/
```

No request body required. Uses the conversation history to generate a natural review description.

**Response (200):**

```json
{
  "generated_description": "Café Luna is my go-to for a chill morning pick-me-up. Their oat milk lattes are velvety smooth — easily some of the best in the area. The interior has a warm, cozy feel that makes you want to linger, even on a quick coffee run. Service is friendly and fast. A solid 4-star spot I'll keep coming back to.",
  "session": { /* full ReviewChat session object */ }
}
```

**Notes:**
- Requires at least one user message in the conversation.
- Can be called multiple times to regenerate.

**Errors:**

| Status | Reason |
|--------|--------|
| 400 | Session is no longer active / no user messages yet |
| 503 | AI service temporarily unavailable |

## Confirm Review

```
POST /api/ai-reviews/{id}/confirm/
```

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `description` | string | No | Override the generated text |
| `photo` | string | No | Base64-encoded photo (same as normal reviews) |

Creates a real `Review` object (same model as manual reviews) and applies all accumulated tag changes to the business.

**Request:**

```json
{}
```

Or with overrides:

```json
{
  "description": "My custom review text...",
  "photo": "data:image/jpeg;base64,/9j/4AAQ..."
}
```

**Response (201 Created):**

```json
{
  "review": {
    "id": 6,
    "user": 1,
    "username": "hanyang",
    "business": 42,
    "business_name": "Café Luna",
    "rating": 4,
    "description": "Café Luna is my go-to for a chill morning pick-me-up...",
    "image_url": null,
    "helpfulness_score": 0,
    "created_at": "2025-02-20T01:30:00Z"
  },
  "tags_added": ["oat-milk", "cozy"],
  "tags_removed": []
}
```

**Errors:**

| Status | Reason |
|--------|--------|
| 400 | Session is no longer active / no description available / already reviewed |

## Abandon Session

```
DELETE /api/ai-reviews/{id}/
```

Marks the session as `abandoned`. No review is created, no tags are applied.

**Response:** `204 No Content`

## Session Status Values

| Status | Description |
|--------|-------------|
| `active` | Chat in progress |
| `completed` | Review created successfully |
| `abandoned` | User cancelled the session |

## Client Functions

```javascript
import {
  getAIReviewSessions, startAIReview, sendAIReviewMessage,
  generateAIReview, confirmAIReview, abandonAIReview
} from '@/api/client'

// List sessions
const { data } = await getAIReviewSessions()

// Start a new chat
const { data: session } = await startAIReview(42, 4)  // business=42, rating=4

// Chat with the AI
const { data: msgRes } = await sendAIReviewMessage(session.id, 'Great oat milk lattes!')
console.log(msgRes.reply)         // AI's response
console.log(msgRes.tags_added)    // ['oat-milk']

// Generate the review text
const { data: genRes } = await generateAIReview(session.id)
console.log(genRes.generated_description)

// Confirm and publish
const { data: confirmRes } = await confirmAIReview(session.id)
console.log(confirmRes.review)     // the created Review object
console.log(confirmRes.tags_added) // tags applied to the business

// Or abandon
await abandonAIReview(session.id)
```
