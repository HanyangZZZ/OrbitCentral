/**
 * auth.js — Authentication & User Profile Endpoints
 * ====================================================
 * PURPOSE:
 *   Wraps every auth-related API call. Components never build URLs or
 *   call Axios directly — they import these named functions instead.
 *
 * MODULAR LOGIC:
 *   Each function maps 1-to-1 with a backend endpoint. This makes the
 *   API surface easy to scan: need to log in? Call login(). Need to
 *   delete an account? Call deleteAccount(). Simple.
 *
 * OOP FLOW:
 *   core.js (Axios instance) → this file adds auth-specific methods →
 *   useAuth composable and page components import from here.
 */
import api from './core'
import { hasCookieConsent } from '@/components/CookieConsent.vue'

// ── Account creation & login ─────────────────────────────────────────────
export const register       = (payload, captchaToken = '')  => api.post('/auth/register/', { ...payload, cookie_consent: hasCookieConsent(), captcha_token: captchaToken })
export const login          = (username, password, captchaToken = '') => api.post('/auth/login/', { username, password, cookie_consent: hasCookieConsent(), captcha_token: captchaToken })

// ── Email verification ───────────────────────────────────────────────────
export const verifyEmail    = (token)                => api.post('/auth/verify-email/', { token })
export const resendVerify   = ()                     => api.post('/auth/resend-verify/')

// ── Profile management ──────────────────────────────────────────────────
export const getMe          = ()                     => api.get('/auth/me/')
export const updateMe       = (payload)              => api.patch('/auth/me/', payload)

// ── Session & security ──────────────────────────────────────────────────
export const logout         = ()                     => api.post('/auth/logout/')
export const deleteAccount  = ()                     => api.delete('/auth/me/')
export const forgotPassword = (email, captchaToken = '') => api.post('/auth/forgot-password/', { email, captcha_token: captchaToken })
export const resetPassword  = (token, newPassword)   => api.post('/auth/reset-password/', { token, new_password: newPassword })
