<!--
  MissionsPage.vue — Gamified Missions / Challenges (route: /missions)
  ─────────────────────────────────────────────────────────────────────────────
  Auth-required page with template "missions" that encourage users to explore
  local businesses and leave reviews.

  MISSION STRUCTURE (local data, not from API)
  Each mission has:
  • icon      — rendered via h() as an inline SVG component
  • title     — e.g. "First Review", "Weekend Explorer"
  • desc      — flavour text explaining the challenge
  • progress  — current / goal numbers
  • reward    — what the user earns (e.g. "Explorer Badge")
  • unlocked  — whether the user can claim the reward

  VISUAL DESIGN
  • Cards show a progress bar (% filled) with primary colour.
  • "Claim Reward" button appears when progress === goal.
  • TemplateNotice at bottom warns this is demo-only.

  NOTE: Missions are currently hard-coded. Future: fetch from API and
  track real user progress server-side.

  MODULAR FLOW
    Static mission data → template renders mission cards
    → progress bar width = (progress/goal) × 100%
    → Claim button is local-only (no API call yet)
  ─────────────────────────────────────────────────────────────────────────────
-->
<template>
  <div class="missions-page">
    <!-- Header -->
    <header class="page-header">
      <button class="back-btn" title="Go Back" @click="router.back()">
        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24"
          fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="m15 18-6-6 6-6"/>
        </svg>
      </button>
      <h1 class="page-title">Missions</h1>
    </header>

    <!-- Template banner -->
    <div class="template-banner">
      <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none"
        stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/>
      </svg>
      <p><strong>Template Preview</strong> — These are demo missions. Real missions and rewards will be available once we collaborate with local businesses.</p>
    </div>

    <!-- Stats bar -->
    <div class="stats-bar">
      <div class="stat">
        <span class="stat-value">{{ completedCount }}</span>
        <span class="stat-label">Completed</span>
      </div>
      <div class="stat-divider" />
      <div class="stat">
        <span class="stat-value">{{ totalPoints }}</span>
        <span class="stat-label">Points</span>
      </div>
      <div class="stat-divider" />
      <div class="stat">
        <span class="stat-value">{{ currentStreak }}</span>
        <span class="stat-label">Day Streak</span>
      </div>
    </div>

    <!-- Active Missions -->
    <section class="missions-section">
      <h2 class="section-heading">Active Missions</h2>
      <div class="missions-grid">
        <div
          v-for="mission in activeMissions"
          :key="mission.id"
          class="mission-card"
          :class="{ 'is-featured': mission.featured }"
        >
          <!-- Difficulty badge -->
          <div class="mission-badge" :class="`badge-${mission.difficulty}`">
            {{ mission.difficulty }}
          </div>

          <!-- Mission header -->
          <div class="mission-header">
            <div class="mission-icon-box">
              <component :is="missionIconComponent(mission.icon)" />
            </div>
            <div class="mission-meta">
              <h3 class="mission-title">{{ mission.title }}</h3>
              <span class="mission-category">{{ mission.category }}</span>
            </div>
          </div>

          <!-- Description -->
          <p class="mission-desc">{{ mission.desc }}</p>

          <!-- Progress bar -->
          <div class="progress-area">
            <div class="progress-header">
              <span class="progress-label">{{ mission.current }} / {{ mission.goal }} {{ mission.unit }}</span>
              <span class="progress-pct">{{ Math.round((mission.current / mission.goal) * 100) }}%</span>
            </div>
            <div class="progress-track">
              <div class="progress-fill" :style="{ width: `${(mission.current / mission.goal) * 100}%` }" />
            </div>
          </div>

          <!-- Reward + expiry -->
          <div class="mission-footer">
            <div class="mission-reward">
              <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none"
                stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="12" cy="8" r="7"/><polyline points="8.21 13.89 7 23 12 20 17 23 15.79 13.88"/>
              </svg>
              <span>{{ mission.reward }}</span>
            </div>
            <div class="mission-expiry">
              <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none"
                stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>
              </svg>
              <span>{{ mission.daysLeft }}d left</span>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Weekly Challenges -->
    <section class="missions-section">
      <h2 class="section-heading">Weekly Challenges</h2>
      <div class="challenges-list">
        <div
          v-for="challenge in weeklyChallenges"
          :key="challenge.id"
          class="challenge-card"
          :class="{ 'is-complete': challenge.complete }"
        >
          <div class="challenge-left">
            <div class="challenge-check">
              <svg v-if="challenge.complete" xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none"
                stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                <path d="M20 6 9 17l-5-5"/>
              </svg>
              <span v-else class="challenge-number">{{ challenge.id }}</span>
            </div>
            <div class="challenge-info">
              <span class="challenge-title">{{ challenge.title }}</span>
              <span class="challenge-desc">{{ challenge.desc }}</span>
            </div>
          </div>
          <div class="challenge-reward-tag">
            <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none"
              stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
            </svg>
            <span>{{ challenge.points }} pts</span>
          </div>
        </div>
      </div>
    </section>

    <!-- Completed Missions -->
    <section class="missions-section">
      <h2 class="section-heading">Completed</h2>
      <div class="completed-list">
        <div
          v-for="mission in completedMissions"
          :key="mission.id"
          class="completed-card"
        >
          <div class="completed-icon">
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none"
              stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/>
            </svg>
          </div>
          <div class="completed-info">
            <span class="completed-title">{{ mission.title }}</span>
            <span class="completed-meta">{{ mission.reward }} — Completed {{ mission.completedDate }}</span>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { computed, h } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

// ── SVG icon helpers (no emojis) ─────────────────────────────────────────
function missionIconComponent(name) {
  const icons = {
    explore: {
      render: () => h('svg', { xmlns: 'http://www.w3.org/2000/svg', width: 22, height: 22, viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': 2, 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }, [
        h('circle', { cx: 12, cy: 12, r: 10 }),
        h('polygon', { points: '16.24 7.76 14.12 14.12 7.76 16.24 9.88 9.88 16.24 7.76' })
      ])
    },
    review: {
      render: () => h('svg', { xmlns: 'http://www.w3.org/2000/svg', width: 22, height: 22, viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': 2, 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }, [
        h('path', { d: 'M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7' }),
        h('path', { d: 'M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z' })
      ])
    },
    bookmark: {
      render: () => h('svg', { xmlns: 'http://www.w3.org/2000/svg', width: 22, height: 22, viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': 2, 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }, [
        h('path', { d: 'M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z' })
      ])
    },
    star: {
      render: () => h('svg', { xmlns: 'http://www.w3.org/2000/svg', width: 22, height: 22, viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': 2, 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }, [
        h('polygon', { points: '12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2' })
      ])
    },
    map: {
      render: () => h('svg', { xmlns: 'http://www.w3.org/2000/svg', width: 22, height: 22, viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': 2, 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }, [
        h('polygon', { points: '1 6 1 22 8 18 16 22 23 18 23 2 16 6 8 2 1 6' }),
        h('line', { x1: 8, y1: 2, x2: 8, y2: 18 }),
        h('line', { x1: 16, y1: 6, x2: 16, y2: 22 })
      ])
    },
    coupon: {
      render: () => h('svg', { xmlns: 'http://www.w3.org/2000/svg', width: 22, height: 22, viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': 2, 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }, [
        h('rect', { x: 1, y: 4, width: 22, height: 16, rx: 2, ry: 2 }),
        h('line', { x1: 1, y1: 10, x2: 23, y2: 10 })
      ])
    }
  }
  return icons[name] || icons.explore
}

// ── Template mission data ────────────────────────────────────────────────
const activeMissions = [
  {
    id: 1,
    title: 'Local Explorer',
    category: 'Discovery',
    desc: 'Visit 5 different local businesses this week to discover hidden gems in your neighbourhood.',
    icon: 'explore',
    difficulty: 'easy',
    current: 2,
    goal: 5,
    unit: 'visits',
    reward: '50 pts + Explorer Badge',
    daysLeft: 5,
    featured: true,
  },
  {
    id: 2,
    title: 'Review Champion',
    category: 'Community',
    desc: 'Write 3 thoughtful reviews for businesses you have visited. Help others discover great spots.',
    icon: 'review',
    difficulty: 'medium',
    current: 1,
    goal: 3,
    unit: 'reviews',
    reward: '75 pts + Reviewer Badge',
    daysLeft: 12,
    featured: false,
  },
  {
    id: 3,
    title: 'Bookmark Collector',
    category: 'Engagement',
    desc: 'Save 10 businesses to your favourites list. Build your personal collection of go-to places.',
    icon: 'bookmark',
    difficulty: 'easy',
    current: 7,
    goal: 10,
    unit: 'bookmarks',
    reward: '30 pts',
    daysLeft: 8,
    featured: false,
  },
  {
    id: 4,
    title: 'Neighbourhood Navigator',
    category: 'Discovery',
    desc: 'Explore businesses in 3 different categories. Broaden your horizons beyond your usual picks.',
    icon: 'map',
    difficulty: 'medium',
    current: 1,
    goal: 3,
    unit: 'categories',
    reward: '60 pts + Navigator Badge',
    daysLeft: 6,
    featured: false,
  },
  {
    id: 5,
    title: 'Coupon Hunter',
    category: 'Savings',
    desc: 'Claim and redeem 2 coupons from local businesses. Save money while supporting local.',
    icon: 'coupon',
    difficulty: 'hard',
    current: 0,
    goal: 2,
    unit: 'coupons',
    reward: '100 pts + Saver Badge',
    daysLeft: 3,
    featured: false,
  },
  {
    id: 6,
    title: 'Five Star Finder',
    category: 'Community',
    desc: 'Rate 5 businesses with a star rating. Your feedback helps the community discover quality spots.',
    icon: 'star',
    difficulty: 'easy',
    current: 4,
    goal: 5,
    unit: 'ratings',
    reward: '40 pts',
    daysLeft: 10,
    featured: false,
  },
]

const weeklyChallenges = [
  { id: 1, title: 'First visit of the week', desc: 'Visit any local business.', points: 10, complete: true },
  { id: 2, title: 'Leave a review', desc: 'Write a review for a recently visited business.', points: 15, complete: true },
  { id: 3, title: 'Try something new', desc: 'Visit a business in a category you have not explored.', points: 20, complete: false },
  { id: 4, title: 'Bookmark 3 businesses', desc: 'Save 3 new businesses to your favourites.', points: 10, complete: false },
  { id: 5, title: 'Share a recommendation', desc: 'Recommend a business to a friend.', points: 25, complete: false },
]

const completedMissions = [
  { id: 101, title: 'Welcome Aboard', reward: '20 pts', completedDate: 'Feb 14' },
  { id: 102, title: 'First Review', reward: '25 pts + Newbie Badge', completedDate: 'Feb 12' },
  { id: 103, title: 'Profile Complete', reward: '15 pts', completedDate: 'Feb 10' },
]

// ── Computed stats ───────────────────────────────────────────────────────
const completedCount = computed(() => completedMissions.length)
const totalPoints = computed(() => {
  const earned = 20 + 25 + 15 + 10 + 15 // completed missions + weekly challenges done
  return earned
})
const currentStreak = computed(() => 3)
</script>

<style scoped>
.missions-page {
  min-height: 100vh;
  background: var(--color-bg);
  color: var(--color-text);
  padding: 0 0 60px;
}

/* ── Header ── */
.page-header {
  display: flex; align-items: center; gap: 16px;
  padding: 24px 32px;
  border-bottom: 1px solid var(--color-border);
}
.back-btn {
  display: flex; align-items: center; justify-content: center;
  width: 36px; height: 36px; border-radius: 50%; border: none; cursor: pointer;
  background: var(--color-surface); color: var(--color-text-muted);
  transition: background 0.2s, color 0.2s; text-decoration: none;
}
.back-btn:hover { background: var(--color-primary); color: #fff; }
.page-title { font-size: 22px; font-weight: 700; color: var(--color-text); }

/* ── Template banner ── */
.template-banner {
  display: flex; align-items: flex-start; gap: 10px;
  max-width: 800px; margin: 24px auto 0; padding: 14px 18px;
  background: rgba(234,179,8,0.06); border: 1px solid rgba(234,179,8,0.2);
  border-radius: 10px; color: #b45309; font-size: 13px; line-height: 1.5;
}
.template-banner svg { flex-shrink: 0; margin-top: 2px; }
.template-banner p { margin: 0; }
.template-banner strong { color: #92400e; }

/* ── Stats bar ── */
.stats-bar {
  display: flex; align-items: center; justify-content: center; gap: 0;
  max-width: 400px; margin: 24px auto; padding: 16px 24px;
  background: var(--color-surface); border: 1px solid var(--color-border);
  border-radius: 12px;
}
.stat { flex: 1; text-align: center; }
.stat-value { display: block; font-size: 22px; font-weight: 700; color: var(--color-primary); }
.stat-label { display: block; font-size: 11px; color: var(--color-text-muted); text-transform: uppercase; letter-spacing: 0.05em; margin-top: 2px; }
.stat-divider { width: 1px; height: 32px; background: var(--color-border); flex-shrink: 0; }

/* ── Sections ── */
.missions-section {
  max-width: 900px; margin: 0 auto;
  padding: 0 32px;
}
.section-heading {
  font-size: 16px; font-weight: 600; color: var(--color-text-muted);
  text-transform: uppercase; letter-spacing: 0.05em;
  margin: 32px 0 16px;
}

/* ═══════════════════════════════════════════════════════════════════════════ */
/* MISSION CARDS                                                              */
/* ═══════════════════════════════════════════════════════════════════════════ */
.missions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 16px;
}

.mission-card {
  position: relative;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 14px;
  padding: 20px;
  transition: transform 0.25s ease, box-shadow 0.25s ease;
}
.mission-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 28px rgba(0,0,0,0.07);
}
.mission-card.is-featured {
  border-color: rgba(74,112,169,0.3);
}

/* ── Difficulty badge ── */
.mission-badge {
  position: absolute; top: 14px; right: 14px;
  padding: 2px 10px; font-size: 10px; font-weight: 700;
  text-transform: uppercase; letter-spacing: 0.06em;
  border-radius: 20px;
}
.badge-easy   { background: rgba(34,197,94,0.1);  color: var(--color-success); border: 1px solid rgba(34,197,94,0.2); }
.badge-medium { background: rgba(245,158,11,0.1); color: var(--color-warning); border: 1px solid rgba(245,158,11,0.2); }
.badge-hard   { background: rgba(239,68,68,0.08); color: var(--color-danger);  border: 1px solid rgba(239,68,68,0.15); }

/* ── Mission header ── */
.mission-header {
  display: flex; align-items: center; gap: 12px;
  margin-bottom: 12px;
}
.mission-icon-box {
  width: 44px; height: 44px; border-radius: 10px;
  background: rgba(74,112,169,0.08);
  display: flex; align-items: center; justify-content: center;
  color: var(--color-primary); flex-shrink: 0;
}
.mission-meta { flex: 1; min-width: 0; }
.mission-title { font-size: 15px; font-weight: 600; color: var(--color-text); margin: 0; }
.mission-category { font-size: 11px; color: var(--color-text-muted); }

/* ── Description ── */
.mission-desc {
  font-size: 13px; color: var(--color-text-muted); line-height: 1.5;
  margin: 0 0 16px;
}

/* ── Progress bar ── */
.progress-area { margin-bottom: 14px; }
.progress-header {
  display: flex; justify-content: space-between; align-items: center;
  margin-bottom: 6px;
}
.progress-label { font-size: 12px; color: var(--color-text-muted); }
.progress-pct { font-size: 12px; font-weight: 600; color: var(--color-primary); }

.progress-track {
  width: 100%; height: 6px;
  background: rgba(0,0,0,0.04);
  border-radius: 3px; overflow: hidden;
}
.progress-fill {
  height: 100%;
  background: var(--color-primary);
  border-radius: 3px;
  transition: width 0.4s ease;
}

/* ── Footer: reward + expiry ── */
.mission-footer {
  display: flex; align-items: center; justify-content: space-between;
}
.mission-reward {
  display: flex; align-items: center; gap: 5px;
  font-size: 12px; font-weight: 600; color: var(--color-primary);
}
.mission-expiry {
  display: flex; align-items: center; gap: 4px;
  font-size: 11px; color: var(--color-text-muted);
  background: rgba(0,0,0,0.03); padding: 3px 10px;
  border-radius: 20px;
}

/* ═══════════════════════════════════════════════════════════════════════════ */
/* WEEKLY CHALLENGES                                                          */
/* ═══════════════════════════════════════════════════════════════════════════ */
.challenges-list {
  display: flex; flex-direction: column; gap: 8px;
}

.challenge-card {
  display: flex; align-items: center; justify-content: space-between;
  background: var(--color-surface); border: 1px solid var(--color-border);
  border-radius: 10px; padding: 14px 18px;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.challenge-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0,0,0,0.05);
}
.challenge-card.is-complete {
  opacity: 0.6;
}
.challenge-card.is-complete .challenge-check {
  background: var(--color-success); color: #fff;
  border-color: var(--color-success);
}

.challenge-left { display: flex; align-items: center; gap: 14px; flex: 1; min-width: 0; }

.challenge-check {
  width: 32px; height: 32px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  background: rgba(0,0,0,0.03); border: 1.5px solid var(--color-border);
  flex-shrink: 0;
}
.challenge-number { font-size: 13px; font-weight: 700; color: var(--color-text-muted); }

.challenge-info { display: flex; flex-direction: column; gap: 1px; min-width: 0; }
.challenge-title { font-size: 14px; font-weight: 600; color: var(--color-text); }
.challenge-desc { font-size: 12px; color: var(--color-text-muted); }

.challenge-reward-tag {
  display: flex; align-items: center; gap: 4px;
  padding: 4px 10px; border-radius: 20px;
  background: rgba(74,112,169,0.06); border: 1px solid rgba(74,112,169,0.12);
  font-size: 11px; font-weight: 600; color: var(--color-primary);
  flex-shrink: 0;
}

/* ═══════════════════════════════════════════════════════════════════════════ */
/* COMPLETED MISSIONS                                                         */
/* ═══════════════════════════════════════════════════════════════════════════ */
.completed-list {
  display: flex; flex-direction: column; gap: 6px;
}

.completed-card {
  display: flex; align-items: center; gap: 14px;
  padding: 12px 18px;
  background: var(--color-surface); border: 1px solid var(--color-border);
  border-radius: 10px;
}

.completed-icon {
  width: 36px; height: 36px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  background: rgba(34,197,94,0.08); color: var(--color-success);
  flex-shrink: 0;
}

.completed-info { display: flex; flex-direction: column; gap: 2px; }
.completed-title { font-size: 14px; font-weight: 600; color: var(--color-text); }
.completed-meta { font-size: 12px; color: var(--color-text-muted); }

/* ── Responsive ── */
@media (max-width: 640px) {
  .page-header { padding: 16px 20px; }
  .missions-section { padding: 0 16px; }
  .missions-grid { grid-template-columns: 1fr; gap: 12px; }
  .stats-bar { margin: 16px; max-width: none; }
  .template-banner { margin: 16px; }
  .challenge-card { flex-direction: column; align-items: flex-start; gap: 10px; }
  .challenge-reward-tag { align-self: flex-end; }
}
</style>
