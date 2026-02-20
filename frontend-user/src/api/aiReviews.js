/**
 * aiReviews.js — AI-Powered Conversational Review System
 * ========================================================
 * PURPOSE:
 *   Endpoints for the AI review chat feature. Users chat with an AI
 *   assistant that helps them write a thoughtful review, then the AI
 *   generates polished review text they can edit and publish.
 *
 * MODULAR LOGIC:
 *   The flow is a state machine with clear steps:
 *   1. start()    → creates a session, AI asks first question
 *   2. message()  → user answers, AI responds (repeat as needed)
 *   3. generate() → AI drafts the review from the conversation
 *   4. confirm()  → user publishes (creates a real Review on backend)
 *   5. abandon()  → user cancels (session deleted)
 *
 *   Each step is a separate endpoint, keeping the logic clean.
 */
import api from './core'

/** List all AI review sessions for the current user. */
export const getAIReviewSessions = () => api.get('/ai-reviews/')

/** Get a single AI review session by UUID. */
export const getAIReviewSession = (id) => api.get(`/ai-reviews/${id}/`)

/** Start a new AI review chat session. */
export const startAIReview = (businessId, rating) =>
  api.post('/ai-reviews/start/', { business: businessId, rating })

/** Send a user message in an AI review chat. */
export const sendAIReviewMessage = (sessionId, message) =>
  api.post(`/ai-reviews/${sessionId}/message/`, { message })

/** Ask the AI to generate a review from the conversation. */
export const generateAIReview = (sessionId) =>
  api.post(`/ai-reviews/${sessionId}/generate/`)

/** Confirm & publish the AI review (creates a real Review object). */
export const confirmAIReview = (sessionId, payload = {}) =>
  api.post(`/ai-reviews/${sessionId}/confirm/`, payload)

/** Abandon / delete an AI review session. */
export const abandonAIReview = (sessionId) =>
  api.delete(`/ai-reviews/${sessionId}/`)
