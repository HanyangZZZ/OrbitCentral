<!--
  IconLibraryPage.vue — Drag & Drop Icon Manager (route: /icons)
  ─────────────────────────────────────────────────────────────────────────────
  Developer / admin utility page for managing SVG icons used across the app.

  FEATURES
  • Drag-and-drop file upload (or click to browse)
  • Previews uploaded SVG icons in a grid
  • Icons are persisted to localStorage (no backend storage)
  • Copy icon markup to clipboard
  • Delete individual icons or clear all
  • Search/filter icons by name

  This page is NOT linked from the main navigation — it's accessed directly
  via /icons and is intended for the development team.

  MODULAR FLOW
    File drop/select → FileReader → SVG string stored in localStorage array
    → grid renders each icon → copy/delete actions modify localStorage.
  ─────────────────────────────────────────────────────────────────────────────
-->
<template>
  <div class="icon-library-page">
    <!-- Header -->
    <header class="page-header">
      <router-link to="/" class="back-btn" title="Back to home">
        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24"
          fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="m15 18-6-6 6-6"/>
        </svg>
      </router-link>
      <h1 class="page-title">
        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24"
          fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/>
          <rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/>
        </svg>
        Icon Library
      </h1>
      <span class="icon-count">{{ totalIconCount }} icon{{ totalIconCount !== 1 ? 's' : '' }}</span>
    </header>

    <!-- Toolbar -->
    <div class="toolbar">
      <!-- Folder tabs -->
      <div class="folder-tabs">
        <button
          v-for="folder in folders"
          :key="folder.name"
          class="folder-tab"
          :class="{ active: activeFolder === folder.name }"
          @click="activeFolder = folder.name"
        >
          <span class="folder-icon">{{ folder.icon }}</span>
          <span class="folder-name">{{ folder.name }}</span>
          <span class="folder-badge">{{ folder.icons.length }}</span>
        </button>
        <button class="folder-tab add-folder-btn" @click="showNewFolderInput = true" v-if="!showNewFolderInput">
          <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24"
            fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/>
          </svg>
          <span>New Folder</span>
        </button>
        <div v-if="showNewFolderInput" class="new-folder-input-wrap">
          <input
            ref="newFolderRef"
            v-model="newFolderName"
            type="text"
            class="new-folder-input"
            placeholder="Folder name…"
            @keydown.enter="createFolder"
            @keydown.escape="cancelNewFolder"
            @blur="cancelNewFolder"
          />
        </div>
      </div>

      <!-- Actions -->
      <div class="toolbar-actions">
        <label class="upload-btn">
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24"
            fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/>
          </svg>
          Upload Icons
          <input
            type="file"
            accept="image/*,.svg"
            multiple
            class="sr-only"
            @change="handleFileUpload"
          />
        </label>
        <button
          v-if="currentFolder && currentFolder.name !== 'All'"
          class="delete-folder-btn"
          @click="deleteFolder(currentFolder.name)"
        >
          <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24"
            fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
          </svg>
          Delete Folder
        </button>
      </div>
    </div>

    <!-- Drop zone -->
    <div
      class="drop-zone"
      :class="{ 'is-dragging': isDragging }"
      @dragenter.prevent="isDragging = true"
      @dragover.prevent="isDragging = true"
      @dragleave.prevent="isDragging = false"
      @drop.prevent="handleDrop"
    >
      <!-- Empty state -->
      <div v-if="displayedIcons.length === 0" class="empty-state">
        <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24"
          fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
          <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><circle cx="8.5" cy="8.5" r="1.5"/>
          <polyline points="21 15 16 10 5 21"/>
        </svg>
        <p class="empty-title">No icons yet</p>
        <p class="empty-desc">Drag & drop image files here, or click "Upload Icons" to add your custom icons.</p>
      </div>

      <!-- Icons grid -->
      <div v-else class="icons-grid">
        <div
          v-for="icon in displayedIcons"
          :key="icon.id"
          class="icon-card"
          :class="{ selected: selectedIcon?.id === icon.id }"
          @click="selectIcon(icon)"
        >
          <div class="icon-preview">
            <img :src="icon.dataUrl" :alt="icon.name" />
          </div>
          <div class="icon-meta">
            <span class="icon-name" :title="icon.name">{{ icon.name }}</span>
            <span class="icon-size">{{ formatSize(icon.size) }}</span>
          </div>

          <!-- Hover actions -->
          <div class="icon-actions">
            <button class="icon-action-btn" title="Copy path" @click.stop="copyPath(icon)">
              <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24"
                fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <rect x="9" y="9" width="13" height="13" rx="2" ry="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>
              </svg>
            </button>
            <button class="icon-action-btn" title="Download" @click.stop="downloadIcon(icon)">
              <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24"
                fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/>
              </svg>
            </button>
            <button class="icon-action-btn move-btn" title="Move to folder" @click.stop="startMove(icon)">
              <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24"
                fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/>
              </svg>
            </button>
            <button class="icon-action-btn danger" title="Delete" @click.stop="deleteIcon(icon)">
              <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24"
                fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
              </svg>
            </button>
          </div>
        </div>
      </div>

      <!-- Drag overlay -->
      <Transition name="fade">
        <div v-if="isDragging" class="drag-overlay">
          <svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" viewBox="0 0 24 24"
            fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/>
          </svg>
          <p>Drop images here to add to <strong>{{ activeFolder }}</strong></p>
        </div>
      </Transition>
    </div>

    <!-- Selected icon detail panel -->
    <Transition name="panel-slide">
      <div v-if="selectedIcon" class="detail-panel">
        <div class="detail-header">
          <h3 class="detail-title">Icon Details</h3>
          <button class="detail-close" @click="selectedIcon = null">
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24"
              fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
          </button>
        </div>
        <div class="detail-preview">
          <img :src="selectedIcon.dataUrl" :alt="selectedIcon.name" />
        </div>
        <div class="detail-info">
          <div class="detail-row">
            <span class="detail-label">Name</span>
            <input
              v-model="selectedIcon.name"
              class="detail-name-input"
              @change="persistFolders"
            />
          </div>
          <div class="detail-row">
            <span class="detail-label">Folder</span>
            <span class="detail-value">{{ selectedIcon.folder }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Size</span>
            <span class="detail-value">{{ formatSize(selectedIcon.size) }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Type</span>
            <span class="detail-value">{{ selectedIcon.type }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Added</span>
            <span class="detail-value">{{ formatDate(selectedIcon.addedAt) }}</span>
          </div>
        </div>
        <div class="detail-actions">
          <button class="btn btn-primary" @click="copyPath(selectedIcon)">
            <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24"
              fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <rect x="9" y="9" width="13" height="13" rx="2" ry="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>
            </svg>
            {{ copyFeedback ? 'Copied!' : 'Copy Data URL' }}
          </button>
          <button class="btn btn-outline" @click="downloadIcon(selectedIcon)">Download</button>
        </div>
      </div>
    </Transition>

    <!-- Move-to-folder modal -->
    <Transition name="fade">
      <div v-if="movingIcon" class="modal-overlay" @click.self="movingIcon = null">
        <div class="move-modal">
          <h3 class="move-title">Move "{{ movingIcon.name }}" to…</h3>
          <div class="move-folder-list">
            <button
              v-for="folder in folders.filter(f => f.name !== 'All' && f.name !== movingIcon.folder)"
              :key="folder.name"
              class="move-folder-option"
              @click="moveToFolder(folder.name)"
            >
              <span class="folder-icon">{{ folder.icon }}</span>
              <span>{{ folder.name }}</span>
            </button>
          </div>
          <button class="btn btn-outline move-cancel" @click="movingIcon = null">Cancel</button>
        </div>
      </div>
    </Transition>

    <!-- Toast notification -->
    <Transition name="toast">
      <div v-if="toast" class="toast" :class="toast.type">
        {{ toast.message }}
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, computed, watch, nextTick, onMounted } from 'vue'
import { formatSize, formatDate } from '@/utils/helpers'

// ── Constants ────────────────────────────────────────────────────────────────
const STORAGE_KEY = 'fblc-icon-library'
const FOLDER_EMOJIS = ['📁', '🎨', '🏷️', '⭐', '🖼️', '🔷', '📌', '🧩', '💎', '🌈']

// ── State ────────────────────────────────────────────────────────────────────
const folders = ref([])
const activeFolder = ref('All')
const selectedIcon = ref(null)
const isDragging = ref(false)
const showNewFolderInput = ref(false)
const newFolderName = ref('')
const newFolderRef = ref(null)
const movingIcon = ref(null)
const copyFeedback = ref(false)
const toast = ref(null)

// ── Computed ─────────────────────────────────────────────────────────────────
const currentFolder = computed(() =>
  folders.value.find(f => f.name === activeFolder.value)
)

const displayedIcons = computed(() => {
  if (activeFolder.value === 'All') {
    return folders.value.flatMap(f => f.name === 'All' ? [] : f.icons)
  }
  return currentFolder.value?.icons ?? []
})

const totalIconCount = computed(() =>
  folders.value.reduce((sum, f) => f.name === 'All' ? sum : sum + f.icons.length, 0)
)

// ── Init ─────────────────────────────────────────────────────────────────────
onMounted(() => {
  loadFromStorage()
  // Ensure 'All' and 'General' folders exist
  if (!folders.value.find(f => f.name === 'All')) {
    folders.value.unshift({ name: 'All', icon: '📋', icons: [] })
  }
  if (!folders.value.find(f => f.name === 'General')) {
    folders.value.push({ name: 'General', icon: '📁', icons: [] })
  }
})

// ── Persistence (localStorage) ───────────────────────────────────────────────
function loadFromStorage() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (raw) folders.value = JSON.parse(raw)
  } catch { /* ignore */ }
}

function persistFolders() {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(folders.value))
  } catch (e) {
    showToast('Storage full — try removing some icons', 'error')
  }
}

// ── Folder management ────────────────────────────────────────────────────────
watch(showNewFolderInput, async (v) => {
  if (v) {
    await nextTick()
    newFolderRef.value?.focus()
  }
})

function createFolder() {
  const name = newFolderName.value.trim()
  if (!name) { cancelNewFolder(); return }
  if (folders.value.find(f => f.name.toLowerCase() === name.toLowerCase())) {
    showToast('A folder with that name already exists', 'error')
    return
  }
  const emoji = FOLDER_EMOJIS[folders.value.length % FOLDER_EMOJIS.length]
  folders.value.push({ name, icon: emoji, icons: [] })
  activeFolder.value = name
  persistFolders()
  cancelNewFolder()
  showToast(`Folder "${name}" created`)
}

function cancelNewFolder() {
  showNewFolderInput.value = false
  newFolderName.value = ''
}

function deleteFolder(folderName) {
  if (folderName === 'All' || folderName === 'General') return
  const idx = folders.value.findIndex(f => f.name === folderName)
  if (idx === -1) return
  const folder = folders.value[idx]
  // Move icons to General
  const general = folders.value.find(f => f.name === 'General')
  if (general && folder.icons.length) {
    folder.icons.forEach(icon => { icon.folder = 'General' })
    general.icons.push(...folder.icons)
  }
  folders.value.splice(idx, 1)
  activeFolder.value = 'All'
  persistFolders()
  showToast(`Folder "${folderName}" deleted. Icons moved to General.`)
}

// ── File handling ────────────────────────────────────────────────────────────
function handleFileUpload(e) {
  const files = Array.from(e.target.files)
  processFiles(files)
  e.target.value = '' // reset file input
}

function handleDrop(e) {
  isDragging.value = false
  const files = Array.from(e.dataTransfer.files).filter(f => f.type.startsWith('image/') || f.name.endsWith('.svg'))
  if (!files.length) {
    showToast('Only image files are supported', 'error')
    return
  }
  processFiles(files)
}

function processFiles(files) {
  const targetFolderName = activeFolder.value === 'All' ? 'General' : activeFolder.value
  const targetFolder = folders.value.find(f => f.name === targetFolderName)
  if (!targetFolder) return

  let added = 0
  files.forEach(file => {
    const reader = new FileReader()
    reader.onload = () => {
      const icon = {
        id: `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
        name: file.name.replace(/\.[^.]+$/, ''),
        folder: targetFolderName,
        dataUrl: reader.result,
        size: file.size,
        type: file.type || 'image/svg+xml',
        addedAt: new Date().toISOString(),
      }
      targetFolder.icons.push(icon)
      added++
      if (added === files.length) {
        persistFolders()
        showToast(`${added} icon${added > 1 ? 's' : ''} added to "${targetFolderName}"`)
      }
    }
    reader.readAsDataURL(file)
  })
}

// ── Icon actions ─────────────────────────────────────────────────────────────
function selectIcon(icon) {
  selectedIcon.value = selectedIcon.value?.id === icon.id ? null : icon
}

function deleteIcon(icon) {
  const folder = folders.value.find(f => f.name === icon.folder)
  if (!folder) return
  const idx = folder.icons.findIndex(i => i.id === icon.id)
  if (idx !== -1) folder.icons.splice(idx, 1)
  if (selectedIcon.value?.id === icon.id) selectedIcon.value = null
  persistFolders()
  showToast(`"${icon.name}" deleted`)
}

function copyPath(icon) {
  navigator.clipboard.writeText(icon.dataUrl).then(() => {
    copyFeedback.value = true
    showToast('Data URL copied to clipboard')
    setTimeout(() => { copyFeedback.value = false }, 2000)
  }).catch(() => {
    showToast('Failed to copy', 'error')
  })
}

function downloadIcon(icon) {
  const a = document.createElement('a')
  a.href = icon.dataUrl
  const ext = icon.type === 'image/svg+xml' ? '.svg' : icon.type === 'image/png' ? '.png' : '.jpg'
  a.download = `${icon.name}${ext}`
  a.click()
}

function startMove(icon) {
  movingIcon.value = icon
}

function moveToFolder(targetFolderName) {
  const icon = movingIcon.value
  if (!icon) return
  // Remove from current folder
  const srcFolder = folders.value.find(f => f.name === icon.folder)
  if (srcFolder) {
    const idx = srcFolder.icons.findIndex(i => i.id === icon.id)
    if (idx !== -1) srcFolder.icons.splice(idx, 1)
  }
  // Add to target folder
  const destFolder = folders.value.find(f => f.name === targetFolderName)
  if (destFolder) {
    icon.folder = targetFolderName
    destFolder.icons.push(icon)
  }
  persistFolders()
  movingIcon.value = null
  showToast(`Moved to "${targetFolderName}"`)
}

// ── Helpers ──────────────────────────────────────────────────────────────────
// formatSize, formatDate — imported from @/utils/helpers

let toastTimer = null
function showToast(message, type = 'success') {
  clearTimeout(toastTimer)
  toast.value = { message, type }
  toastTimer = setTimeout(() => { toast.value = null }, 3000)
}
</script>

<style scoped>
/* ══════════════════════════════════════════════════════════════════════════ */
/* LAYOUT                                                                     */
/* ══════════════════════════════════════════════════════════════════════════ */
.icon-library-page {
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
  width: 36px; height: 36px; border-radius: 50%;
  background: var(--color-surface); color: var(--color-text-muted);
  transition: background 0.2s, color 0.2s; text-decoration: none;
}
.back-btn:hover { background: var(--color-primary); color: #fff; }
.page-title {
  display: flex; align-items: center; gap: 10px;
  font-size: 22px; font-weight: 700; color: var(--color-primary);
}
.icon-count {
  margin-left: auto;
  font-size: 13px; font-weight: 500; color: var(--color-text-muted);
  background: rgba(0,0,0,0.03); padding: 4px 14px; border-radius: 20px;
  border: 1px solid var(--color-border);
}

/* ══════════════════════════════════════════════════════════════════════════ */
/* TOOLBAR                                                                    */
/* ══════════════════════════════════════════════════════════════════════════ */
.toolbar {
  display: flex; align-items: center; justify-content: space-between;
  gap: 16px; padding: 16px 32px;
  border-bottom: 1px solid var(--color-border);
  background: var(--color-surface);
  flex-wrap: wrap;
}

/* ── Folder tabs ── */
.folder-tabs {
  display: flex; align-items: center; gap: 6px;
  flex-wrap: wrap;
}
.folder-tab {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 7px 14px; border-radius: 8px;
  background: transparent; border: 1px solid var(--color-border);
  color: var(--color-text-light); font-size: 13px; font-weight: 500;
  cursor: pointer; transition: all 0.15s;
}
.folder-tab:hover { border-color: var(--color-primary); color: var(--color-primary); }
.folder-tab.active {
  background: rgba(74,112,169,0.08); border-color: var(--color-primary);
  color: var(--color-primary); font-weight: 600;
}
.folder-icon { font-size: 14px; }
.folder-badge {
  font-size: 10px; font-weight: 700;
  background: rgba(74,112,169,0.1); color: var(--color-primary);
  padding: 1px 7px; border-radius: 10px;
}
.folder-tab.active .folder-badge { background: var(--color-primary); color: #fff; }

.add-folder-btn {
  border-style: dashed; color: var(--color-text-muted);
}
.add-folder-btn:hover { border-color: var(--color-primary); color: var(--color-primary); }

.new-folder-input-wrap { display: flex; }
.new-folder-input {
  padding: 7px 12px; border-radius: 8px;
  border: 1px solid var(--color-primary); background: var(--color-surface);
  color: var(--color-text); font-size: 13px; outline: none; width: 140px;
  box-shadow: 0 0 0 3px rgba(74,112,169,0.12);
}

/* ── Actions ── */
.toolbar-actions { display: flex; align-items: center; gap: 8px; }
.upload-btn {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 8px 16px; border-radius: 8px;
  background: var(--color-primary); color: #fff;
  font-size: 13px; font-weight: 600; cursor: pointer;
  transition: background 0.15s;
}
.upload-btn:hover { background: var(--color-primary-hover); }
.delete-folder-btn {
  display: inline-flex; align-items: center; gap: 4px;
  padding: 8px 12px; border-radius: 8px;
  background: transparent; border: 1px solid var(--color-border);
  color: var(--color-danger); font-size: 12px; cursor: pointer;
  transition: all 0.15s;
}
.delete-folder-btn:hover { border-color: var(--color-danger); background: rgba(239,68,68,0.06); }

/* ══════════════════════════════════════════════════════════════════════════ */
/* DROP ZONE                                                                  */
/* ══════════════════════════════════════════════════════════════════════════ */
.drop-zone {
  position: relative;
  min-height: 400px;
  padding: 32px;
  max-width: 1400px;
  margin: 0 auto;
}
.drop-zone.is-dragging { background: rgba(74,112,169,0.04); }

/* Empty state */
.empty-state {
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  gap: 12px; padding: 80px 24px; text-align: center;
  color: var(--color-text-muted);
}
.empty-state svg { opacity: 0.35; }
.empty-title { font-size: 18px; font-weight: 600; color: var(--color-text-light); margin: 0; }
.empty-desc { font-size: 14px; margin: 0; max-width: 400px; line-height: 1.5; }

/* Drag overlay */
.drag-overlay {
  position: absolute; inset: 0;
  display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 12px;
  background: rgba(74,112,169,0.06);
  border: 2px dashed var(--color-primary);
  border-radius: 16px;
  color: var(--color-primary); font-size: 16px; font-weight: 600;
  z-index: 10;
}

/* ══════════════════════════════════════════════════════════════════════════ */
/* ICONS GRID                                                                 */
/* ══════════════════════════════════════════════════════════════════════════ */
.icons-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  gap: 16px;
}

.icon-card {
  position: relative;
  border-radius: 12px;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  overflow: hidden;
  cursor: pointer;
  transition: all 0.15s;
}
.icon-card:hover {
  border-color: rgba(74,112,169,0.3);
  box-shadow: var(--shadow-md);
}
.icon-card.selected {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 2px rgba(74,112,169,0.2);
}

.icon-preview {
  display: flex; align-items: center; justify-content: center;
  height: 100px; padding: 12px;
  background: repeating-conic-gradient(rgba(0,0,0,0.04) 0% 25%, transparent 0% 50%) 50% / 16px 16px;
}
.icon-preview img {
  max-width: 100%; max-height: 100%;
  object-fit: contain;
}

.icon-meta {
  padding: 8px 10px;
  border-top: 1px solid var(--color-border);
}
.icon-name {
  display: block; font-size: 12px; font-weight: 500;
  color: var(--color-text);
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.icon-size { font-size: 10px; color: var(--color-text-muted); }

/* Hover actions overlay */
.icon-actions {
  position: absolute; top: 6px; right: 6px;
  display: flex; gap: 3px;
  opacity: 0; transition: opacity 0.15s;
}
.icon-card:hover .icon-actions { opacity: 1; }

.icon-action-btn {
  width: 28px; height: 28px; border-radius: 6px;
  display: flex; align-items: center; justify-content: center;
  background: var(--color-surface); border: 1px solid var(--color-border);
  color: var(--color-text-muted); cursor: pointer;
  transition: all 0.1s;
  box-shadow: var(--shadow-sm);
}
.icon-action-btn:hover { color: var(--color-primary); border-color: var(--color-primary); }
.icon-action-btn.danger:hover { color: var(--color-danger); border-color: var(--color-danger); }

/* ══════════════════════════════════════════════════════════════════════════ */
/* DETAIL PANEL                                                               */
/* ══════════════════════════════════════════════════════════════════════════ */
.detail-panel {
  position: fixed; right: 0; top: 60px; bottom: 0;
  width: 320px; background: var(--color-surface);
  border-left: 1px solid var(--color-border);
  box-shadow: var(--shadow-lg);
  padding: 24px; overflow-y: auto;
  z-index: 50;
  display: flex; flex-direction: column; gap: 20px;
}
.detail-header {
  display: flex; align-items: center; justify-content: space-between;
}
.detail-title { font-size: 16px; font-weight: 700; color: var(--color-text); margin: 0; }
.detail-close {
  width: 32px; height: 32px; border-radius: 8px; display: flex; align-items: center; justify-content: center;
  background: rgba(0,0,0,0.03); border: none; color: var(--color-text-muted); cursor: pointer;
  transition: all 0.15s;
}
.detail-close:hover { background: rgba(0,0,0,0.06); color: var(--color-text); }

.detail-preview {
  display: flex; align-items: center; justify-content: center;
  height: 160px; border-radius: 12px; padding: 16px;
  background: repeating-conic-gradient(rgba(0,0,0,0.04) 0% 25%, transparent 0% 50%) 50% / 16px 16px;
  border: 1px solid var(--color-border);
}
.detail-preview img { max-width: 100%; max-height: 100%; object-fit: contain; }

.detail-info { display: flex; flex-direction: column; gap: 10px; }
.detail-row { display: flex; align-items: center; gap: 10px; }
.detail-label {
  font-size: 12px; font-weight: 500; color: var(--color-text-muted);
  min-width: 60px; flex-shrink: 0;
}
.detail-value { font-size: 13px; color: var(--color-text); }
.detail-name-input {
  flex: 1; padding: 5px 8px; border-radius: 6px;
  border: 1px solid var(--color-border); background: var(--color-bg);
  color: var(--color-text); font-size: 13px; outline: none;
  transition: border-color 0.15s;
}
.detail-name-input:focus { border-color: var(--color-primary); }

.detail-actions { display: flex; gap: 8px; margin-top: auto; }
.detail-actions .btn { flex: 1; font-size: 13px; gap: 6px; }

/* ══════════════════════════════════════════════════════════════════════════ */
/* MOVE MODAL                                                                 */
/* ══════════════════════════════════════════════════════════════════════════ */
.modal-overlay {
  position: fixed; inset: 0; background: rgba(15,23,42,0.4);
  display: flex; align-items: center; justify-content: center;
  z-index: 200;
}
.move-modal {
  background: var(--color-surface); border-radius: 16px;
  padding: 24px; width: 90%; max-width: 360px;
  box-shadow: var(--shadow-lg);
}
.move-title { font-size: 16px; font-weight: 600; margin: 0 0 16px; color: var(--color-text); }
.move-folder-list { display: flex; flex-direction: column; gap: 6px; margin-bottom: 16px; }
.move-folder-option {
  display: flex; align-items: center; gap: 10px;
  padding: 10px 14px; border-radius: 8px;
  background: var(--color-bg); border: 1px solid var(--color-border);
  color: var(--color-text); font-size: 14px; cursor: pointer;
  transition: all 0.15s;
}
.move-folder-option:hover { border-color: var(--color-primary); background: rgba(74,112,169,0.06); }
.move-cancel { width: 100%; }

/* ══════════════════════════════════════════════════════════════════════════ */
/* TOAST                                                                      */
/* ══════════════════════════════════════════════════════════════════════════ */
.toast {
  position: fixed; bottom: 24px; left: 50%; transform: translateX(-50%);
  padding: 10px 20px; border-radius: 10px;
  font-size: 13px; font-weight: 500;
  z-index: 999; box-shadow: var(--shadow-lg);
}
.toast.success { background: var(--color-primary); color: #fff; }
.toast.error { background: var(--color-danger); color: #fff; }

/* ══════════════════════════════════════════════════════════════════════════ */
/* TRANSITIONS                                                                */
/* ══════════════════════════════════════════════════════════════════════════ */
.fade-enter-active, .fade-leave-active { transition: opacity 0.2s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }

.panel-slide-enter-active { transition: transform 0.25s ease-out, opacity 0.2s; }
.panel-slide-leave-active { transition: transform 0.2s ease-in, opacity 0.15s; }
.panel-slide-enter-from { transform: translateX(100%); opacity: 0; }
.panel-slide-leave-to { transform: translateX(100%); opacity: 0; }

.toast-enter-active { transition: all 0.25s ease-out; }
.toast-leave-active { transition: all 0.2s ease-in; }
.toast-enter-from { opacity: 0; transform: translate(-50%, 16px); }
.toast-leave-to { opacity: 0; transform: translate(-50%, 16px); }

/* ══════════════════════════════════════════════════════════════════════════ */
/* RESPONSIVE                                                                 */
/* ══════════════════════════════════════════════════════════════════════════ */
@media (max-width: 768px) {
  .page-header { padding: 16px 20px; }
  .toolbar { padding: 12px 16px; }
  .drop-zone { padding: 16px; }
  .icons-grid { grid-template-columns: repeat(auto-fill, minmax(110px, 1fr)); gap: 10px; }
  .detail-panel { width: 100%; top: auto; height: 50vh; border-left: none; border-top: 1px solid var(--color-border); }
}
</style>
